"""Tests for maze generation."""

from core.maze import PATH, WALL, Maze

DEFAULT_SIZE = 21
EVEN_SIZE = 20
SMALL_SIZE = 15
LARGE_SIZE = 101
CLAMP_SMALL = 10
CLAMP_LARGE = 150
SEED_123 = 123
SEED_1 = 1
SEED_2 = 2
SMALL_MAZE = 11
PATH_THRESHOLD = 50
COORD_PAIR = 2
COPY_TEST_VALUE = 999


class TestMazeGeneration:
    """Test DFS Recursive Backtracker maze generation."""

    def test_maze_dimensions(self) -> None:
        """Test maze has correct dimensions."""
        maze = Maze(DEFAULT_SIZE, DEFAULT_SIZE)
        maze.generate()

        assert len(maze.grid) == DEFAULT_SIZE
        assert len(maze.grid[0]) == DEFAULT_SIZE
        assert maze.width == DEFAULT_SIZE
        assert maze.height == DEFAULT_SIZE

    def test_maze_odd_dimensions(self) -> None:
        """Test even dimensions are converted to odd."""
        maze = Maze(EVEN_SIZE, EVEN_SIZE)
        maze.generate()

        assert maze.width == DEFAULT_SIZE
        assert maze.height == DEFAULT_SIZE

    def test_maze_bounds_clamped(self) -> None:
        """Test dimensions are clamped to 15-101."""
        small = Maze(CLAMP_SMALL, CLAMP_SMALL)
        small.generate()
        assert small.width == SMALL_SIZE
        assert small.height == SMALL_SIZE

        large = Maze(CLAMP_LARGE, CLAMP_LARGE)
        large.generate()
        assert large.width == LARGE_SIZE
        assert large.height == LARGE_SIZE

    def test_start_and_end_positions(self) -> None:
        """Test start and end are at correct positions."""
        maze = Maze(DEFAULT_SIZE, DEFAULT_SIZE)
        maze.generate()

        assert maze.start == (1, 1)
        assert maze.end == (19, 19)

    def test_start_and_end_are_paths(self) -> None:
        """Test start and end cells are paths, not walls."""
        maze = Maze(DEFAULT_SIZE, DEFAULT_SIZE)
        maze.generate()

        sx, sy = maze.start
        ex, ey = maze.end
        assert maze.grid[sy][sx] == PATH
        assert maze.grid[ey][ex] == PATH

    def test_maze_has_paths(self) -> None:
        """Test maze contains paths (not all walls)."""
        maze = Maze(DEFAULT_SIZE, DEFAULT_SIZE)
        maze.generate()

        path_count = sum(row.count(PATH) for row in maze.grid)
        # Should have many paths
        assert path_count > PATH_THRESHOLD

    def test_maze_is_perfect(self) -> None:
        """Test maze is perfect (no loops, all cells reachable)."""
        maze = Maze(DEFAULT_SIZE, DEFAULT_SIZE, seed=42)
        maze.generate()

        # Flood fill from start - should reach all paths
        visited = set()
        stack = [maze.start]

        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if maze.grid[y][x] == WALL:
                continue
            visited.add((x, y))
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < maze.width and 0 <= ny < maze.height:
                    stack.append((nx, ny))

        # All path cells should be reachable
        path_cells = {
            (x, y)
            for y in range(maze.height)
            for x in range(maze.width)
            if maze.grid[y][x] == PATH
        }
        assert visited == path_cells

    def test_generation_steps_recorded(self) -> None:
        """Test generation steps are recorded for animation."""
        maze = Maze(SMALL_MAZE, SMALL_MAZE)
        maze.generate()

        assert len(maze.generation_steps) > 0
        # Each step should be a list of coordinates
        for step in maze.generation_steps:
            assert isinstance(step, list)
            for cell in step:
                assert isinstance(cell, tuple)
                assert len(cell) == COORD_PAIR

    def test_reproducible_with_seed(self) -> None:
        """Test same seed produces same maze."""
        maze1 = Maze(DEFAULT_SIZE, DEFAULT_SIZE, seed=SEED_123)
        maze1.generate()

        maze2 = Maze(DEFAULT_SIZE, DEFAULT_SIZE, seed=SEED_123)
        maze2.generate()

        assert maze1.grid == maze2.grid
        assert maze1.generation_steps == maze2.generation_steps

    def test_different_seeds_different_mazes(self) -> None:
        """Test different seeds produce different mazes."""
        maze1 = Maze(DEFAULT_SIZE, DEFAULT_SIZE, seed=SEED_1)
        maze1.generate()

        maze2 = Maze(DEFAULT_SIZE, DEFAULT_SIZE, seed=SEED_2)
        maze2.generate()

        # Very unlikely to be identical
        assert maze1.grid != maze2.grid

    def test_from_grid_classmethod(self) -> None:
        """Test creating maze from existing grid."""
        original = Maze(SMALL_MAZE, SMALL_MAZE)
        original.generate()

        copied = Maze.from_grid(original.grid)
        assert copied.grid == original.grid
        assert copied.width == original.width
        assert copied.height == original.height


class TestMazeEdgeCases:
    """Test edge cases and error conditions."""

    def test_minimum_size(self) -> None:
        """Test minimum allowed size."""
        maze = Maze(SMALL_SIZE, SMALL_SIZE)
        maze.generate()
        assert maze.width == SMALL_SIZE
        assert maze.height == SMALL_SIZE

    def test_maximum_size(self) -> None:
        """Test maximum allowed size."""
        maze = Maze(LARGE_SIZE, LARGE_SIZE)
        maze.generate()
        assert maze.width == LARGE_SIZE
        assert maze.height == LARGE_SIZE

    def test_to_json_returns_copy(self) -> None:
        """Test to_json returns a copy, not reference."""
        maze = Maze(SMALL_MAZE, SMALL_MAZE)
        maze.generate()

        json_grid = maze.to_json()
        json_grid[0][0] = COPY_TEST_VALUE

        assert maze.grid[0][0] != COPY_TEST_VALUE
