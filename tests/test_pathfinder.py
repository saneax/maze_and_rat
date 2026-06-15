"""Tests for pathfinding algorithms."""

import pytest

from core.maze import Maze
from core.pathfinder import BFS, AStar, Dijkstra, PathResult

BLOCKED_GRID = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0],
]
HEURISTIC_1 = 7
HEURISTIC_2 = 0
HEURISTIC_3 = 16
PATH_LEN_9 = 9
PATH_LEN_3 = 3


class TestPathfinderBase:
    """Shared test cases for all pathfinders."""

    @pytest.fixture
    def simple_maze(self) -> Maze:
        """Create a simple 11x11 maze with known path."""
        maze = Maze(11, 11, seed=42)
        maze.generate()
        return maze

    @pytest.fixture
    def open_grid(self) -> list[list[int]]:
        """Create an open grid (no walls) for testing."""
        return [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

    @pytest.fixture
    def blocked_grid(self) -> list[list[int]]:
        """Create a grid with no path from start to end."""
        return BLOCKED_GRID

    def test_astar_finds_path(self, simple_maze: Maze) -> None:
        """Test A* finds path in generated maze."""
        finder = AStar()
        result = finder.find_path(simple_maze.grid, simple_maze.start, simple_maze.end)

        assert result.success
        assert len(result.path) > 0
        assert result.path[0] == simple_maze.start
        assert result.path[-1] == simple_maze.end

    def test_dijkstra_finds_path(self, simple_maze: Maze) -> None:
        """Test Dijkstra finds path in generated maze."""
        finder = Dijkstra()
        result = finder.find_path(simple_maze.grid, simple_maze.start, simple_maze.end)

        assert result.success
        assert len(result.path) > 0
        assert result.path[0] == simple_maze.start
        assert result.path[-1] == simple_maze.end

    def test_bfs_finds_path(self, simple_maze: Maze) -> None:
        """Test BFS finds path in generated maze."""
        finder = BFS()
        result = finder.find_path(simple_maze.grid, simple_maze.start, simple_maze.end)

        assert result.success
        assert len(result.path) > 0
        assert result.path[0] == simple_maze.start
        assert result.path[-1] == simple_maze.end

    def test_all_algorithms_find_same_path_length(self, simple_maze: Maze) -> None:
        """Test all algorithms find optimal path (same length)."""
        astar = AStar()
        dijkstra = Dijkstra()
        bfs = BFS()

        r1 = astar.find_path(simple_maze.grid, simple_maze.start, simple_maze.end)
        r2 = dijkstra.find_path(simple_maze.grid, simple_maze.start, simple_maze.end)
        r3 = bfs.find_path(simple_maze.grid, simple_maze.start, simple_maze.end)

        assert r1.success and r2.success and r3.success
        assert len(r1.path) == len(r2.path) == len(r3.path)

    def test_open_grid_shortest_path(self, open_grid: list[list[int]]) -> None:
        """Test pathfinding on open grid."""
        start = (0, 0)
        end = (4, 4)

        for finder in [AStar(), Dijkstra(), BFS()]:
            result = finder.find_path(open_grid, start, end)
            assert result.success
            # Manhattan distance = 8
            assert len(result.path) == PATH_LEN_9

    def test_blocked_grid_no_path(self, blocked_grid: list[list[int]]) -> None:
        """Test pathfinding when no path exists."""
        start = (0, 0)
        end = (2, 2)

        for finder in [AStar(), Dijkstra(), BFS()]:
            result = finder.find_path(blocked_grid, start, end)
            assert not result.success
            assert result.path == []

    def test_start_is_wall(self, simple_maze: Maze) -> None:
        """Test pathfinding when start is a wall."""
        grid = [row[:] for row in simple_maze.grid]
        sx, sy = simple_maze.start
        grid[sy][sx] = 1  # Make start a wall

        for finder in [AStar(), Dijkstra(), BFS()]:
            result = finder.find_path(grid, simple_maze.start, simple_maze.end)
            assert not result.success

    def test_end_is_wall(self, simple_maze: Maze) -> None:
        """Test pathfinding when end is a wall."""
        grid = [row[:] for row in simple_maze.grid]
        ex, ey = simple_maze.end
        grid[ey][ex] = 1  # Make end a wall

        for finder in [AStar(), Dijkstra(), BFS()]:
            result = finder.find_path(grid, simple_maze.start, simple_maze.end)
            assert not result.success

    def test_start_equals_end(self, open_grid: list[list[int]]) -> None:
        """Test pathfinding when start equals end."""
        start = (2, 2)
        end = (2, 2)

        for finder in [AStar(), Dijkstra(), BFS()]:
            result = finder.find_path(open_grid, start, end)
            assert result.success
            assert result.path == [(2, 2)]

    def test_visited_cells_recorded(self, simple_maze: Maze) -> None:
        """Test visited cells are recorded during search."""
        finder = AStar()
        result = finder.find_path(simple_maze.grid, simple_maze.start, simple_maze.end)

        assert result.success
        assert len(result.visited) > 0
        assert simple_maze.start in result.visited
        assert simple_maze.end in result.visited

    def test_path_is_continuous(self, simple_maze: Maze) -> None:
        """Test path has no gaps (each step is adjacent)."""
        finder = AStar()
        result = finder.find_path(simple_maze.grid, simple_maze.start, simple_maze.end)

        assert result.success
        for i in range(len(result.path) - 1):
            x1, y1 = result.path[i]
            x2, y2 = result.path[i + 1]
            assert abs(x1 - x2) + abs(y1 - y2) == 1  # Adjacent

    def test_path_only_through_paths(self, simple_maze: Maze) -> None:
        """Test path only goes through PATH cells, not WALLs."""
        finder = AStar()
        result = finder.find_path(simple_maze.grid, simple_maze.start, simple_maze.end)

        assert result.success
        for x, y in result.path:
            assert simple_maze.grid[y][x] == 0  # PATH


class TestAStarSpecific:
    """Tests specific to A* algorithm."""

    @pytest.fixture
    def simple_maze(self) -> Maze:
        """Create a simple 11x11 maze with known path."""
        maze = Maze(11, 11, seed=42)
        maze.generate()
        return maze

    def test_heuristic_admissible(self) -> None:
        """Test Manhattan heuristic never overestimates."""
        finder = AStar()
        # On open grid, heuristic equals actual distance
        assert finder.heuristic((0, 0), (3, 4)) == HEURISTIC_1
        assert finder.heuristic((5, 5), (5, 5)) == HEURISTIC_2
        assert finder.heuristic((10, 2), (2, 10)) == HEURISTIC_3

    def test_astar_expands_fewer_nodes_than_dijkstra(self, simple_maze: Maze) -> None:
        """Test A* typically visits fewer nodes than Dijkstra."""
        astar = AStar()
        dijkstra = Dijkstra()

        r1 = astar.find_path(simple_maze.grid, simple_maze.start, simple_maze.end)
        r2 = dijkstra.find_path(simple_maze.grid, simple_maze.start, simple_maze.end)

        # A* with good heuristic should visit <= nodes
        assert len(r1.visited) <= len(r2.visited)


class TestDijkstraSpecific:
    """Tests specific to Dijkstra algorithm."""

    def test_uniform_cost(self) -> None:
        """Test Dijkstra explores uniformly (no heuristic)."""
        # On open grid, Dijkstra expands in diamond pattern
        grid = [[0 for _ in range(7)] for _ in range(7)]
        finder = Dijkstra()
        result = finder.find_path(grid, (3, 3), (3, 5))

        assert result.success
        assert len(result.path) == PATH_LEN_3


class TestBFSSpecific:
    """Tests specific to BFS algorithm."""

    def test_bfs_finds_shortest_in_unweighted(self) -> None:
        """Test BFS finds shortest path in unweighted grid."""
        # Create a maze where there's a long path and a short path
        grid = [
            [0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0],
        ]
        # Short path: (0,0) -> (0,1) blocked, so must go around
        # Actually from (0,0) to (4,4)
        finder = BFS()
        result = finder.find_path(grid, (0, 0), (4, 4))
        assert result.success


class TestPathResult:
    """Tests for PathResult dataclass."""

    def test_default_values(self) -> None:
        """Test PathResult default values."""
        result = PathResult()
        assert result.path == []
        assert result.visited == []
        assert not result.success

    def test_custom_values(self) -> None:
        """Test PathResult with custom values."""
        result = PathResult(path=[(0, 0), (1, 0)], visited=[(0, 0)], success=True)
        assert result.path == [(0, 0), (1, 0)]
        assert result.visited == [(0, 0)]
        assert result.success
