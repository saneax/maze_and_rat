# Maze & Rat Web Game

A web-based maze game where a **rat algorithmically finds its way out** of a procedurally generated maze. Watch the maze build itself cell by cell, then watch the rat solve it using A*, Dijkstra, or BFS pathfinding algorithms.

![Maze & Rat Demo](https://img.shields.io/badge/Status-Complete-brightgreen) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Quick Start

### Option 1: Run with Python (Development)

```bash
# 1. Clone/navigate to project
cd maze_and_rat

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Run the server
python main.py
```

**Open your browser:** http://localhost:8000

---

### Option 2: Run with Docker (Production/Deployment)

```bash
# 1. Build and start
docker compose up -d --build

# 2. Check it's running
docker compose logs -f

# 3. Open browser
# http://localhost:8000
```

**Stop the container:**
```bash
docker compose down
```

---

## How to Play / Use

### The Interface

When you open the game, you'll see:

```
┌─────────────────────────────────────────────────────┐
│  Maze & Rat          (title)                        │
│  DFS Maze Generation • A* Pathfinding              │
├─────────────────────────────────────────────────────┤
│  Width:  [==========●----]  21     Height: [====●-] 21  │
│  Speed:  [========●------]  10x    Seed: [________]    │
│  [New Maze]  [Solve (A*)]  [Compare]  [Export PNG]   │
├─────────────────────────────────────────────────────┤
│                    MAZE CANVAS                      │
│  ████████████████████████████████████████          │
│  ██  █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █     │
│  ████████████████████████████████████████          │
│          (green = start, red = end)               │
├─────────────────────────────────────────────────────┤
│  Path: 85  |  Visited: 99  |  Gen: 0.1ms  |  Solve: 0.1ms  │
│  Algorithm: A*                                    │
└─────────────────────────────────────────────────────┘
```

### Step-by-Step Usage

1. **Generate a Maze** → Click **`New Maze`** (or it auto-generates on load)
   - Watch the maze build itself in real-time (blue = carving paths)
   - Adjust **Width/Height** sliders before generating (odd numbers work best)

2. **Solve with A*** → Click **`Solve (A*)`**
   - Blue cells = algorithm exploring
   - Green path = optimal solution found
   - Statistics update automatically

3. **Compare Algorithms** → Click **`Compare Algorithms`**
   - See A*, Dijkstra, and BFS side-by-side
   - Compare path lengths, cells visited, and solve times
   - All three find the same optimal path length!

4. **Export** → Click **`Export PNG`**
   - Downloads the current maze as a PNG image

5. **Customize**
   - **Speed slider**: 1x (slow) to 50x (instant)
   - **Seed input**: Enter a number for reproducible mazes
   - **Size sliders**: 15×15 to 101×101 (auto-adjusted to odd)

---

## Testing

### Run All Tests
```bash
# With Python
pytest tests/ -v

# With Docker
docker compose run --rm maze-and-rat pytest tests/ -v
```

### Test Categories
```bash
# Maze generation tests (14 tests)
pytest tests/test_maze.py -v

# Pathfinding algorithm tests (17 tests)
pytest tests/test_pathfinder.py -v

# API endpoint tests (15 tests)
pytest tests/test_api.py -v
```

### Code Quality Checks
```bash
# Linting
ruff check .

# Type checking (strict)
mypy --strict .

# Format code
ruff format .
```

**All 46 tests should pass**, mypy should report no issues, and ruff should be clean.

---

## API Reference

The backend exposes a REST API at `http://localhost:8000/api`

### Generate Maze
```bash
POST /api/maze/generate
Content-Type: application/json

{
  "width": 21,      // 15-101 (auto-clamped to odd)
  "height": 21,     // 15-101 (auto-clamped to odd)
  "seed": 42        // optional, for reproducibility
}
```

**Response:**
```json
{
  "maze": [[1,0,1,...], ...],      // 2D grid (1=wall, 0=path)
  "width": 21,
  "height": 21,
  "start": [1, 1],
  "end": [19, 19],
  "generation_steps": [[[1,1]], [[2,1],[3,1]], ...],  // for animation
  "generation_time_ms": 0.14
}
```

### Solve Maze
```bash
POST /api/maze/solve
Content-Type: application/json

{
  "maze": [[1,0,1,...], ...],
  "start": [1, 1],
  "end": [19, 19],
  "algorithm": "astar"  // "astar" | "dijkstra" | "bfs"
}
```

**Response:**
```json
{
  "path": [[1,1], [2,1], [3,1], ...],  // solution path
  "visited": [[1,1], [2,1], [1,2], ...],  // cells explored
  "path_length": 85,
  "cells_visited": 99,
  "solve_time_ms": 0.11,
  "algorithm": "astar"
}
```

### Compare Algorithms
```bash
POST /api/maze/compare
Content-Type: application/json

{
  "maze": [[1,0,1,...], ...],
  "start": [1, 1],
  "end": [19, 19]
}
```

**Response:** Runs all 3 algorithms, returns array of results.

### Health Check
```bash
GET /health
# Returns: {"status": "ok"}
```

---

## Project Structure

```
maze_and_rat/
├── main.py                 # FastAPI app entry point
├── pyproject.toml          # Dependencies & tool config
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Multi-service orchestration
├── .dockerignore           # Build context exclusions
├── README.md               # This file
│
├── api/                    # REST API layer
│   ├── __init__.py
│   └── maze.py             # /api/maze/* endpoints
│
├── core/                   # Pure algorithm implementations
│   ├── __init__.py
│   ├── maze.py             # DFS Recursive Backtracker
│   └── pathfinder.py       # A*, Dijkstra, BFS
│
├── static/                 # Frontend (served by FastAPI)
│   ├── index.html          # Main HTML page
│   ├── style.css           # Responsive dark theme
│   └── app.js              # Canvas rendering & animation
│
└── tests/                  # Unit & integration tests
    ├── __init__.py
    ├── test_maze.py        # Maze generation tests
    ├── test_pathfinder.py  # Pathfinding algorithm tests
    └── test_api.py         # API endpoint tests
```

---

## Implementation Details

### Maze Generation: DFS Recursive Backtracker
- Creates **perfect mazes** (no loops, single path between any two cells)
- Starts at (1,1), carves paths 2 cells at a time
- Records every step for smooth animation playback
- Dimensions auto-clamped: 15-101, forced odd

### Pathfinding Algorithms

| Algorithm | Heuristic | Optimality | Use Case |
|-----------|-----------|------------|----------|
| **A*** | Manhattan distance | Optimal | Default, fastest for games |
| **Dijkstra** | None (uniform cost) | Optimal | When all edges equal weight |
| **BFS** | None (queue) | Optimal (unweighted) | Simplest, good baseline |

All three guarantee the **same optimal path length** on unweighted grids.

### Frontend Architecture
- **Single HTML page** with vanilla JavaScript (no framework)
- **HTML5 Canvas** for high-performance rendering
- **Step-by-step animation** using `requestAnimationFrame` + `setTimeout`
- **Responsive design** works on mobile (stacked controls) and desktop
- **Color coding**: 🟫 walls, ⬛ paths, 🟢 start, 🔴 end, 🔵 visited, 🟢 solution

---

## Configuration

### Environment Variables (Docker)
```yaml
environment:
  - PYTHONUNBUFFERED=1  # Ensure logs appear immediately
```

### Port Configuration
- **Default**: 8000
- **Change in docker-compose.yml**: `ports: - "YOUR_PORT:8000"`
- **Change in Python**: `uvicorn main:app --port YOUR_PORT`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -e ".[dev]"` |
| Port 8000 in use | Change port in `docker-compose.yml` or `main.py` |
| Tests fail | Ensure you're in project root, run `pytest tests/ -v` |
| Maze looks wrong | Try odd dimensions (21×21, 31×31) |
| Animation too fast/slow | Adjust speed slider (1-50x) |
| Docker build fails | Check Docker daemon is running, try `docker system prune` |

---

## Development

### Adding Features
1. **Backend**: Add to `core/` (algorithms) or `api/` (endpoints)
2. **Frontend**: Edit `static/app.js` and `static/style.css`
3. **Tests**: Add to `tests/` following existing patterns
4. **Quality**: Run `ruff check . && mypy --strict . && pytest tests/`

### Code Style
- **Ruff** for linting/formatting (100 char line length)
- **mypy --strict** for type safety
- **Type hints** required on all functions
- **Dataclasses with slots** for performance

---

## License

MIT License - Feel free to use, modify, and distribute.

---

## Credits

Built with:
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Vanilla JS + Canvas** - Zero-dependency frontend

---

**Enjoy watching the rat escape the maze!** 🐀🏃‍♂️