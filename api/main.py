from fastapi import FastAPI
from api.routes import chat
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Chat API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; restrict to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(chat.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Chat API!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
