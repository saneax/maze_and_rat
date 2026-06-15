"""Maze API endpoints."""

import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.maze import Maze
from core.pathfinder import BFS, AStar, Dijkstra, Pathfinder

router = APIRouter()


class MazeGenerateRequest(BaseModel):
    """Request model for maze generation."""

    width: int = Field(
        default=21, description="Maze width (odd number recommended, clamped to 15-101)"
    )
    height: int = Field(
        default=21, description="Maze height (odd number recommended, clamped to 15-101)"
    )
    seed: int | None = Field(default=None, description="Random seed for reproducibility")


class MazeGenerateResponse(BaseModel):
    """Response model for maze generation."""

    maze: list[list[int]]
    width: int
    height: int
    start: tuple[int, int]
    end: tuple[int, int]
    generation_steps: list[list[tuple[int, int]]]
    generation_time_ms: float


class MazeSolveRequest(BaseModel):
    """Request model for maze solving."""

    maze: list[list[int]]
    start: tuple[int, int]
    end: tuple[int, int]
    algorithm: str = Field(default="astar", pattern="^(astar|dijkstra|bfs)$")


class MazeSolveResponse(BaseModel):
    """Response model for maze solving."""

    path: list[tuple[int, int]]
    visited: list[tuple[int, int]]
    path_length: int
    cells_visited: int
    solve_time_ms: float
    algorithm: str


class MazeCompareRequest(BaseModel):
    """Request model for algorithm comparison."""

    maze: list[list[int]]
    start: tuple[int, int]
    end: tuple[int, int]


class AlgorithmResult(BaseModel):
    """Single algorithm result for comparison."""

    algorithm: str
    path: list[tuple[int, int]]
    visited: list[tuple[int, int]]
    path_length: int
    cells_visited: int
    solve_time_ms: float


class MazeCompareResponse(BaseModel):
    """Response model for algorithm comparison."""

    results: list[AlgorithmResult]


def get_pathfinder(algorithm: str) -> Pathfinder:
    """Get pathfinder instance by name."""
    match algorithm.lower():
        case "astar":
            return AStar()
        case "dijkstra":
            return Dijkstra()
        case "bfs":
            return BFS()
        case _:
            raise HTTPException(status_code=400, detail=f"Unknown algorithm: {algorithm}")


@router.post("/maze/generate", response_model=MazeGenerateResponse)
async def generate_maze(request: MazeGenerateRequest) -> MazeGenerateResponse:
    """Generate a new maze using DFS Recursive Backtracker."""
    start_time = time.perf_counter()

    maze = Maze(request.width, request.height, request.seed)
    maze.generate()

    generation_time = (time.perf_counter() - start_time) * 1000

    return MazeGenerateResponse(
        maze=maze.grid,
        width=maze.width,
        height=maze.height,
        start=maze.start,
        end=maze.end,
        generation_steps=maze.generation_steps,
        generation_time_ms=generation_time,
    )


@router.post("/maze/solve", response_model=MazeSolveResponse)
async def solve_maze(request: MazeSolveRequest) -> MazeSolveResponse:
    """Solve a maze using the specified algorithm."""
    pathfinder = get_pathfinder(request.algorithm)

    start_time = time.perf_counter()
    result = pathfinder.find_path(request.maze, request.start, request.end)
    solve_time = (time.perf_counter() - start_time) * 1000

    return MazeSolveResponse(
        path=result.path,
        visited=result.visited,
        path_length=len(result.path),
        cells_visited=len(result.visited),
        solve_time_ms=solve_time,
        algorithm=request.algorithm,
    )


@router.post("/maze/compare", response_model=MazeCompareResponse)
async def compare_algorithms(request: MazeCompareRequest) -> MazeCompareResponse:
    """Compare multiple pathfinding algorithms on the same maze."""
    algorithms = ["astar", "dijkstra", "bfs"]
    results = []

    for algo_name in algorithms:
        pathfinder = get_pathfinder(algo_name)

        start_time = time.perf_counter()
        result = pathfinder.find_path(request.maze, request.start, request.end)
        solve_time = (time.perf_counter() - start_time) * 1000

        results.append(
            AlgorithmResult(
                algorithm=algo_name,
                path=result.path,
                visited=result.visited,
                path_length=len(result.path),
                cells_visited=len(result.visited),
                solve_time_ms=solve_time,
            )
        )

    return MazeCompareResponse(results=results)
