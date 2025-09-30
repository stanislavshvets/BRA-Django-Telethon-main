import uvicorn

if __name__ == "__main__":
    uvicorn.run("MyDjangoBot.asgi:application", reload=True)
