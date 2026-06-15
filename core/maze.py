"""Maze generation using DFS Recursive Backtracker."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Self

# Cell values
WALL = 1
PATH = 0
VISITED = 2  # For generation animation
CURRENT = 3  # For generation animation


@dataclass(slots=True)
class Maze:
    """Maze with DFS Recursive Backtracker generation."""

    width: int
    height: int
    seed: int | None = None

    # Internal state
    grid: list[list[int]] = field(init=False, default_factory=list)
    start: tuple[int, int] = field(init=False, default=(1, 1))
    end: tuple[int, int] = field(init=False, default=(0, 0))
    generation_steps: list[list[tuple[int, int]]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        """Initialize maze grid."""
        # Ensure odd dimensions for proper maze structure
        self.width = self.width if self.width % 2 == 1 else self.width + 1
        self.height = self.height if self.height % 2 == 1 else self.height + 1

        # Clamp to bounds
        self.width = max(15, min(101, self.width))
        self.height = max(15, min(101, self.height))

        if self.seed is not None:
            random.seed(self.seed)

        self.grid = [[WALL for _ in range(self.width)] for _ in range(self.height)]
        self.start = (1, 1)
        self.end = (self.width - 2, self.height - 2)
        self.generation_steps = []

    def generate(self) -> Self:
        """Generate maze using DFS Recursive Backtracker."""
        stack: list[tuple[int, int]] = [self.start]
        self.grid[self.start[1]][self.start[0]] = PATH
        self._record_step([self.start])

        while stack:
            current = stack[-1]
            x, y = current

            # Find unvisited neighbors (2 cells away)
            neighbors = self._get_unvisited_neighbors(x, y)

            if neighbors:
                nx, ny = random.choice(neighbors)
                # Carve path between current and neighbor
                wx, wy = (x + nx) // 2, (y + ny) // 2
                self.grid[wy][wx] = PATH
                self.grid[ny][nx] = PATH
                self._record_step([(wx, wy), (nx, ny)])
                stack.append((nx, ny))
            else:
                stack.pop()
                if stack:
                    self._record_step([stack[-1]])

        # Ensure start and end are paths
        self.grid[self.start[1]][self.start[0]] = PATH
        self.grid[self.end[1]][self.end[0]] = PATH

        return self

    def _get_unvisited_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """Get unvisited neighbor cells (2 steps away)."""
        neighbors = []
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # N, E, S, W

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 < nx < self.width - 1
                    and 0 < ny < self.height - 1
                    and self.grid[ny][nx] == WALL):
                neighbors.append((nx, ny))

        return neighbors

    def _record_step(self, cells: list[tuple[int, int]]) -> None:
        """Record a generation step for animation."""
        self.generation_steps.append(cells.copy())

    def to_json(self) -> list[list[int]]:
        """Return maze grid as JSON-serializable list."""
        return [row.copy() for row in self.grid]

    @classmethod
    def from_grid(cls, grid: list[list[int]]) -> Self:
        """Create maze from existing grid."""
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0
        maze = cls(width, height)
        maze.grid = [row.copy() for row in grid]
        maze.start = (1, 1)
        maze.end = (width - 2, height - 2)
        return maze

