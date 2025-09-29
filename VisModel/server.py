# server.py
# Minimal async HTTP service to render OBJ -> MP4 using PyVista/VTK.
# Exposes:
#   POST /render         -> submit a render job (non-blocking), returns job_id
#   GET  /status/{id}    -> check job status
#   GET  /result/{id}    -> download resulting MP4 when finished
#   GET  /health         -> health probe

import asyncio
import io
import logging
import os
import pathlib
import traceback
import uuid
from aiohttp import web
from concurrent.futures import ProcessPoolExecutor

# Project imports: your existing pipeline
from MeshBuilderVTK import MeshBuilderVTK
from RenderPyVista import Visualizer

logging.basicConfig(level=logging.INFO)

# Where to store final videos
VIDEOS_DIR = pathlib.Path("../common_data/video")
VIDEOS_DIR.mkdir(exist_ok=True)
MODELS_DIR = pathlib.Path("../common_data/models")

# CPU-bound rendering is offloaded to processes to avoid blocking the event loop
executor = ProcessPoolExecutor(max_workers=os.cpu_count())

# In-memory job storage for demo purposes
# In production you might use a DB or Redis
jobs = {}  # job_id -> {"status": "...", "result_path": "...", "error": "...", "params": {...}}

async def health(request: web.Request):
    # Simple liveness endpoint
    return web.json_response({"status": "ok"})

def render_obj_to_mp4(obj_path: str, out_path: str, params: dict):
    """
    Synchronous worker function executed in a separate process.
    Steps:
      1) Read OBJ/STL via VTK using MeshBuilderVTK
      2) Create a PyVista Visualizer with off-screen rendering
      3) Produce frames and encode MP4 to a BytesIO
      4) Persist the MP4 to disk
    """
    # 1) Load mesh
    builder = MeshBuilderVTK(obj_path)
    poly = builder.build_mesh()

    # 2) Parameters with safe defaults
    frames = int(params.get("frames", 120))
    angle = float(params.get("angle", 3.0))      # degrees per frame
    width = int(params.get("width", 1024))
    height = int(params.get("height", 1024))

    # 3) Render to memory using your Visualizer
    vis = Visualizer(poly_data=poly, frames=frames, angle=angle, window_size=(width, height))
    video_bytes: io.BytesIO = vis.gen_gif()  # despite the name, it returns MP4 via imageio

    if video_bytes is None:
        raise RuntimeError("Renderer returned no data")

    # 4) Write MP4 to file
    with open(out_path, "wb") as f:
        f.write(video_bytes.getbuffer())

    return out_path

async def submit_render(request: web.Request):
    # Accept JSON payload, validate inputs, enqueue background job, return job_id
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "invalid JSON"}, status=400)

    obj_path = data.get("obj_path")
    params = data.get("params", {})

    # Validate that the model path exists locally
    if not obj_path or not os.path.exists(obj_path):
        return web.json_response({"error": "obj_path not found"}, status=400)

    # Create a unique job identifier and an output path
    job_id = str(uuid.uuid4())
    out_path = str(VIDEOS_DIR / f"{pathlib.Path(obj_path).stem}_{job_id}.mp4")

    # Initialize job metadata
    jobs[job_id] = {"status": "queued", "result_path": out_path, "params": params}

    # Schedule the blocking render in a process without blocking the event loop
    loop = asyncio.get_running_loop()

    async def run():
        jobs[job_id]["status"] = "running"
        try:
            await loop.run_in_executor(executor, render_obj_to_mp4, obj_path, out_path, params)
            jobs[job_id]["status"] = "finished"
        except Exception as e:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = f"{e}\n{traceback.format_exc()}"

    asyncio.create_task(run())
    return web.json_response({"job_id": job_id, "status": "queued"})

async def get_status(request: web.Request):
    # Return job status (queued|running|finished|failed)
    job_id = request.match_info["job_id"]
    job = jobs.get(job_id)
    if not job:
        return web.json_response({"error": "job not found"}, status=404)
    return web.json_response({"job_id": job_id, "status": job["status"], "error": job.get("error")})

async def get_result(request: web.Request):
    # Stream MP4 when ready; otherwise report the current status
    job_id = request.match_info["job_id"]
    job = jobs.get(job_id)
    if not job:
        return web.json_response({"error": "job not found"}, status=404)
    if job["status"] != "finished":
        return web.json_response({"error": "not ready", "status": job["status"]}, status=409)
    return web.FileResponse(job["result_path"], headers={"Content-Type": "video/mp4"})

def make_app():
    # Create aiohttp app and register routes
    app = web.Application(client_max_size=1024**3)  # increase if you plan to accept uploads
    app.add_routes([
        web.get("/health", health),
        web.post("/render", submit_render),
        web.get("/status/{job_id}", get_status),
        web.get("/result/{job_id}", get_result),
    ])
    return app

if __name__ == "__main__":
    # Run the web service
    web.run_app(make_app(), host="0.0.0.0", port=8080)