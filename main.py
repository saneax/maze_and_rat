"""Maze & Rat Web Game - FastAPI backend."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.maze import router as maze_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Maze & Rat Game",
    description="Procedural maze generation with algorithmic pathfinding",
    version="0.1.0",
    lifespan=lifespan,
)

# API routes
app.include_router(maze_router, prefix="/api")

# Static files - serve frontend from /static
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root() -> FileResponse:
    """Serve the main HTML page."""
    return FileResponse(static_dir / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
