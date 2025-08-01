from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import api
from api.core.assistant_factory import (
    assistant_factory,
)  # This will initialize assistants at import

app = FastAPI(title="API Agent Platform", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/v1")

# Print assistant IDs at startup for verification
print("Initialized assistants:", assistant_factory.assistants)


@app.get("/")
def read_root():
    return {"message": "Welcome to the API Agent Platform!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
