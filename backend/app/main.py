"""Article Downloader API — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routes import router

app = FastAPI(
    title="Article Downloader",
    description="Recursively download articles and their linked pages",
    version="1.0.0",
)

# CORS — allow the React dev server and any production origin
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Serve React build in production
frontend_build = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build")
if os.path.isdir(frontend_build):
    app.mount("/", StaticFiles(directory=frontend_build, html=True), name="frontend")


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
