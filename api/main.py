from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import api

app = FastAPI(title="API Agent Platform", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to the API Agent Platform!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
