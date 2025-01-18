from fastapi import FastAPI
from api.routes import chat

app = FastAPI(title="Chat API", version="1.0")

app.include_router(chat.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Chat API!"}
