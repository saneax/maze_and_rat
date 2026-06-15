"""Pathfinding algorithms: A*, Dijkstra, BFS."""

from __future__ import annotations

import heapq
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field

# Cell values
WALL = 1
PATH = 0


@dataclass(slots=True)
class PathResult:
    """Result of pathfinding."""

    path: list[tuple[int, int]] = field(default_factory=list)
    visited: list[tuple[int, int]] = field(default_factory=list)
    success: bool = False


class Pathfinder(ABC):
    """Abstract base class for pathfinding algorithms."""

    @abstractmethod
    def find_path(
        self,
        grid: list[list[int]],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> PathResult:
        """Find path from start to end."""
        pass

    def _reconstruct_path(
        self,
        came_from: dict[tuple[int, int], tuple[int, int]],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> list[tuple[int, int]]:
        """Reconstruct path from came_from dict."""
        if end not in came_from and start != end:
            return []

        path = [end]
        current = end
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def _get_neighbors(
        self, x: int, y: int, grid: list[list[int]]
    ) -> list[tuple[int, int]]:
        """Get valid neighbor positions (4-directional)."""
        neighbors = []
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height
                    and grid[ny][nx] == PATH):
                neighbors.append((nx, ny))

        return neighbors


class AStar(Pathfinder):
    """A* pathfinding with Manhattan heuristic."""

    def heuristic(self, a: tuple[int, int], b: tuple[int, int]) -> int:
        """Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(
        self,
        grid: list[list[int]],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> PathResult:
        """Find path using A* algorithm."""
        if grid[start[1]][start[0]] == WALL or grid[end[1]][end[0]] == WALL:
            return PathResult(success=False)

        open_set: list[tuple[int, int, tuple[int, int]]] = []
        heapq.heappush(open_set, (0, 0, start))

        came_from: dict[tuple[int, int], tuple[int, int]] = {}
        g_score: dict[tuple[int, int], int] = {start: 0}
        f_score: dict[tuple[int, int], int] = {start: self.heuristic(start, end)}
        visited: list[tuple[int, int]] = []
        visited_set: set[tuple[int, int]] = set()

        while open_set:
            _, current_g, current = heapq.heappop(open_set)

            if current in visited_set:
                continue

            visited_set.add(current)
            visited.append(current)

            if current == end:
                path = self._reconstruct_path(came_from, start, end)
                return PathResult(path=path, visited=visited, success=True)

            for neighbor in self._get_neighbors(current[0], current[1], grid):
                if neighbor in visited_set:
                    continue

                tentative_g = current_g + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], tentative_g, neighbor))

        return PathResult(path=[], visited=visited, success=False)


class Dijkstra(Pathfinder):
    """Dijkstra's algorithm (uniform cost search)."""

    def find_path(
        self,
        grid: list[list[int]],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> PathResult:
        """Find path using Dijkstra's algorithm."""
        if grid[start[1]][start[0]] == WALL or grid[end[1]][end[0]] == WALL:
            return PathResult(success=False)

        open_set: list[tuple[int, tuple[int, int]]] = []
        heapq.heappush(open_set, (0, start))

        came_from: dict[tuple[int, int], tuple[int, int]] = {}
        dist: dict[tuple[int, int], int] = {start: 0}
        visited: list[tuple[int, int]] = []
        visited_set: set[tuple[int, int]] = set()

        while open_set:
            current_dist, current = heapq.heappop(open_set)

            if current in visited_set:
                continue

            visited_set.add(current)
            visited.append(current)

            if current == end:
                path = self._reconstruct_path(came_from, start, end)
                return PathResult(path=path, visited=visited, success=True)

            for neighbor in self._get_neighbors(current[0], current[1], grid):
                if neighbor in visited_set:
                    continue

                new_dist = current_dist + 1

                if neighbor not in dist or new_dist < dist[neighbor]:
                    came_from[neighbor] = current
                    dist[neighbor] = new_dist
                    heapq.heappush(open_set, (new_dist, neighbor))

        return PathResult(path=[], visited=visited, success=False)


class BFS(Pathfinder):
    """Breadth-First Search for unweighted grids."""

    def find_path(
        self,
        grid: list[list[int]],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> PathResult:
        """Find path using BFS."""
        if grid[start[1]][start[0]] == WALL or grid[end[1]][end[0]] == WALL:
            return PathResult(success=False)

        queue: deque[tuple[int, int]] = deque([start])
        came_from: dict[tuple[int, int], tuple[int, int]] = {}
        visited: list[tuple[int, int]] = []
        visited_set: set[tuple[int, int]] = {start}

        while queue:
            current = queue.popleft()
            visited.append(current)

            if current == end:
                path = self._reconstruct_path(came_from, start, end)
                return PathResult(path=path, visited=visited, success=True)

            for neighbor in self._get_neighbors(current[0], current[1], grid):
                if neighbor not in visited_set:
                    visited_set.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)

        return PathResult(path=[], visited=visited, success=False)
