import argparse, json, time, subprocess, sys, os, requests

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-obj", required=True)
    p.add_argument("-frames", type=int, default=120)
    p.add_argument("-angle", type=float, default=3.0)
    p.add_argument("-width", type=int, default=1024)
    p.add_argument("-height", type=int, default=1024)
    p.add_argument("-out", default="Videos/out.mp4")
    args = p.parse_args()

    r = requests.post("http://localhost:8080/render",
                      json={"obj_path": args.obj,
                            "params":{"frames": args.frames,
                                      "angle": args.angle,
                                      "width": args.width,
                                      "height": args.height}})
    r.raise_for_status()
    job_id = r.json()["job_id"]
    print("Queued:", job_id)

    while True:
        s = requests.get(f"http://localhost:8080/status/{job_id}").json()
        print("Status:", s["status"], end="\r")
        if s["status"] in ("finished", "failed"):
            print()
            if s["status"] == "failed":
                print("Error:\n", s.get("error"))
                sys.exit(1)
            break
        time.sleep(1)

    with requests.get(f"http://localhost:8080/result/{job_id}", stream=True) as g:
        g.raise_for_status()
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "wb") as f:
            for chunk in g.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    print("Saved to", args.out)

if __name__ == "__main__":
    main()
