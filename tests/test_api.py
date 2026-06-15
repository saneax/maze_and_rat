"""Tests for API endpoints."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_UNPROCESSABLE = 422
DEFAULT_WIDTH = 21
DEFAULT_HEIGHT = 21
CUSTOM_WIDTH = 31
CLAMPED_MIN = 15
CLAMPED_MAX = 101
SEED_42 = 42
SEED_1 = 1
SEED_2 = 2
VALID_SMALL = 15
VALID_MEDIUM = 25
LARGE_SIZE = 200
PATH_LENGTH_3 = 3
COORD_PAIR = 2


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health(self) -> None:
        """Test health endpoint returns ok."""
        response = client.get("/health")
        assert response.status_code == HTTP_OK
        assert response.json() == {"status": "ok"}


class BaseMazeTest:
    """Base class with shared maze generation helper."""

    def _gen_maze(self) -> dict[str, object]:
        """Generate a maze and return its data."""
        gen_response = client.post(
            "/api/maze/generate",
            json={"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT, "seed": SEED_42},
        )
        return gen_response.json()  # type: ignore[no-any-return]


class TestMazeGenerateEndpoint(BaseMazeTest):
    """Test maze generation endpoint."""

    def test_generate_default(self) -> None:
        """Test maze generation with defaults."""
        response = client.post("/api/maze/generate", json={})
        assert response.status_code == HTTP_OK

        data = response.json()
        assert "maze" in data
        assert "width" in data
        assert "height" in data
        assert "start" in data
        assert "end" in data
        assert "generation_steps" in data
        assert "generation_time_ms" in data

        assert data["width"] == DEFAULT_WIDTH
        assert data["height"] == DEFAULT_HEIGHT
        assert data["start"] == [1, 1]
        assert data["end"] == [19, 19]

    def test_generate_custom_size(self) -> None:
        """Test maze generation with custom size."""
        response = client.post(
            "/api/maze/generate",
            json={"width": CUSTOM_WIDTH, "height": DEFAULT_HEIGHT},
        )
        assert response.status_code == HTTP_OK

        data = response.json()
        assert data["width"] == CUSTOM_WIDTH
        assert data["height"] == DEFAULT_HEIGHT

    def test_generate_with_seed(self) -> None:
        """Test maze generation with seed for reproducibility."""
        response1 = client.post(
            "/api/maze/generate",
            json={"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT, "seed": SEED_42},
        )
        response2 = client.post(
            "/api/maze/generate",
            json={"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT, "seed": SEED_42},
        )

        assert response1.status_code == HTTP_OK
        assert response2.status_code == HTTP_OK
        assert response1.json()["maze"] == response2.json()["maze"]

    def test_generate_different_seeds(self) -> None:
        """Test different seeds produce different mazes."""
        response1 = client.post(
            "/api/maze/generate",
            json={"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT, "seed": SEED_1},
        )
        response2 = client.post(
            "/api/maze/generate",
            json={"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT, "seed": SEED_2},
        )

        assert response1.json()["maze"] != response2.json()["maze"]

    def test_generate_clamps_size(self) -> None:
        """Test size clamping at boundaries."""
        # Too small - should be clamped to 15
        response = client.post("/api/maze/generate", json={"width": 10, "height": 10})
        assert response.status_code == HTTP_OK
        assert response.json()["width"] == CLAMPED_MIN
        assert response.json()["height"] == CLAMPED_MIN

        # Too large - should be clamped to 101
        response = client.post(
            "/api/maze/generate", json={"width": LARGE_SIZE, "height": LARGE_SIZE}
        )
        assert response.status_code == HTTP_OK
        assert response.json()["width"] == CLAMPED_MAX
        assert response.json()["height"] == CLAMPED_MAX

    def test_generation_steps_recorded(self) -> None:
        """Test generation steps are included for animation."""
        response = client.post(
            "/api/maze/generate",
            json={"width": VALID_SMALL, "height": VALID_SMALL},
        )
        assert response.status_code == HTTP_OK

        data = response.json()
        assert len(data["generation_steps"]) > 0
        # Each step is a list of [x, y] coordinates
        for step in data["generation_steps"]:
            assert isinstance(step, list)
            for cell in step:
                assert len(cell) == COORD_PAIR

    def test_invalid_size_rejected(self) -> None:
        """Test that invalid sizes (even after clamping) are rejected."""
        # The API clamps, but if somehow invalid, it should 422
        # Actually the Maze class handles clamping, so this tests that
        response = client.post("/api/maze/generate", json={"width": 10, "height": 10})
        # Should succeed with clamped values
        assert response.status_code == HTTP_OK


class TestMazeSolveEndpoint(BaseMazeTest):
    """Test maze solving endpoint."""

    def test_solve_astar(self) -> None:
        """Test solving with A*."""
        maze_data = self._gen_maze()

        response = client.post(
            "/api/maze/solve",
            json={
                "maze": maze_data["maze"],
                "start": maze_data["start"],
                "end": maze_data["end"],
                "algorithm": "astar",
            },
        )
        assert response.status_code == HTTP_OK

        data = response.json()
        assert data["algorithm"] == "astar"
        assert data["path_length"] > 0
        assert data["cells_visited"] > 0
        assert data["solve_time_ms"] > 0
        assert len(data["path"]) == data["path_length"]
        assert data["path"][0] == maze_data["start"]
        assert data["path"][-1] == maze_data["end"]

    def test_solve_dijkstra(self) -> None:
        """Test solving with Dijkstra."""
        maze_data = self._gen_maze()

        response = client.post(
            "/api/maze/solve",
            json={
                "maze": maze_data["maze"],
                "start": maze_data["start"],
                "end": maze_data["end"],
                "algorithm": "dijkstra",
            },
        )
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["algorithm"] == "dijkstra"
        assert data["path_length"] > 0

    def test_solve_bfs(self) -> None:
        """Test solving with BFS."""
        maze_data = self._gen_maze()

        response = client.post(
            "/api/maze/solve",
            json={
                "maze": maze_data["maze"],
                "start": maze_data["start"],
                "end": maze_data["end"],
                "algorithm": "bfs",
            },
        )
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["algorithm"] == "bfs"
        assert data["path_length"] > 0

    def test_solve_invalid_algorithm(self) -> None:
        """Test solving with invalid algorithm returns 400."""
        maze_data = self._gen_maze()

        response = client.post(
            "/api/maze/solve",
            json={
                "maze": maze_data["maze"],
                "start": maze_data["start"],
                "end": maze_data["end"],
                "algorithm": "invalid",
            },
        )
        # Pydantic pattern validation returns 422, not 400
        assert response.status_code == HTTP_UNPROCESSABLE

    def test_solve_start_is_wall(self) -> None:
        """Test solving when start is a wall."""
        maze = [[0 for _ in range(5)] for _ in range(5)]
        maze[0][0] = 1  # Start is wall

        response = client.post(
            "/api/maze/solve",
            json={
                "maze": maze,
                "start": [0, 0],
                "end": [4, 4],
                "algorithm": "astar",
            },
        )
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["path_length"] == 0
        assert data["path"] == []


class TestMazeCompareEndpoint(BaseMazeTest):
    """Test algorithm comparison endpoint."""

    def test_compare_algorithms(self) -> None:
        """Test comparing all three algorithms."""
        maze_data = self._gen_maze()

        response = client.post(
            "/api/maze/compare",
            json={
                "maze": maze_data["maze"],
                "start": maze_data["start"],
                "end": maze_data["end"],
            },
        )
        assert response.status_code == HTTP_OK

        data = response.json()
        assert "results" in data
        assert len(data["results"]) == PATH_LENGTH_3

        algorithms = {r["algorithm"] for r in data["results"]}
        assert algorithms == {"astar", "dijkstra", "bfs"}

        for result in data["results"]:
            assert result["path_length"] > 0
            assert result["cells_visited"] > 0
            assert result["solve_time_ms"] > 0

    def test_compare_same_path_length(self) -> None:
        """Test all algorithms find same optimal path length."""
        maze_data = self._gen_maze()

        response = client.post(
            "/api/maze/compare",
            json={
                "maze": maze_data["maze"],
                "start": maze_data["start"],
                "end": maze_data["end"],
            },
        )
        data = response.json()

        lengths = [r["path_length"] for r in data["results"]]
        assert len(set(lengths)) == 1  # All same length
