import uvicorn

config = {
    "host": "0.0.0.0",
    "port": 8000,
}

if __name__ == "__main__":
    uvicorn.run("kerani.api:app", **config)
