# main.py

from fastapi import FastAPI
from api.v1.router import router as api_v1_router

# Create the FastAPI app instance
app = FastAPI(
    title="Intelligent Query-Retrieval System",
    description="An LLM-powered system to process documents and answer questions.",
    version="1.0.0"
)

# Include the API router with a prefix
# The final endpoint will be http://localhost:8000/api/v1/hackrx/run
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Intelligent Query-Retrieval System API."}

# To run the app, use the command: uvicorn main:app --reload