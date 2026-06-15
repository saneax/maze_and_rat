// Maze & Rat Game - Frontend Application

const canvas = document.getElementById('mazeCanvas');
const ctx = canvas.getContext('2d');

const compareCanvas1 = document.getElementById('compareCanvas1');
const compareCanvas2 = document.getElementById('compareCanvas2');
const compareCanvas3 = document.getElementById('compareCanvas3');
const compareCtx1 = compareCanvas1.getContext('2d');
const compareCtx2 = compareCanvas2.getContext('2d');
const compareCtx3 = compareCanvas3.getContext('2d');

const comparisonContainer = document.getElementById('comparisonContainer');
const compareStats = document.getElementById('compareStats');

const mazeWidthInput = document.getElementById('mazeWidth');
const mazeHeightInput = document.getElementById('mazeHeight');
const speedInput = document.getElementById('speed');
const seedInput = document.getElementById('seed');
const widthValue = document.getElementById('widthValue');
const heightValue = document.getElementById('heightValue');
const speedValue = document.getElementById('speedValue');

const newMazeBtn = document.getElementById('newMazeBtn');
const solveBtn = document.getElementById('solveBtn');
const compareBtn = document.getElementById('compareBtn');
const exportBtn = document.getElementById('exportBtn');

const pathLengthEl = document.getElementById('pathLength');
const cellsVisitedEl = document.getElementById('cellsVisited');
const genTimeEl = document.getElementById('genTime');
const solveTimeEl = document.getElementById('solveTime');
const algorithmEl = document.getElementById('algorithm');

let currentMaze = null;
let currentStart = null;
let currentEnd = null;
let generationSteps = [];
let animationFrameId = null;
let isAnimating = false;
let cellSize = 20;
let animationDelay = 50; // ms, adjusted by speed slider

// Colors
const COLORS = {
    wall: '#1a1a2e',
    path: '#0f0f23',
    start: '#4ade80',
    end: '#f87171',
    visited: '#60a5fa',
    current: '#fbbf24',
    pathFound: '#22c55e',
    gridLine: '#2a2a4a'
};

// Initialize event listeners
function init() {
    mazeWidthInput.addEventListener('input', updateWidthValue);
    mazeHeightInput.addEventListener('input', updateHeightValue);
    speedInput.addEventListener('input', updateSpeedValue);
    newMazeBtn.addEventListener('click', generateMaze);
    solveBtn.addEventListener('click', solveMaze);
    compareBtn.addEventListener('click', compareAlgorithms);
    exportBtn.addEventListener('click', exportPNG);

    updateWidthValue();
    updateHeightValue();
    updateSpeedValue();

    generateMaze();
}

function updateWidthValue() {
    widthValue.textContent = mazeWidthInput.value;
}

function updateHeightValue() {
    heightValue.textContent = mazeHeightInput.value;
}

function updateSpeedValue() {
    const speed = parseInt(speedInput.value);
    speedValue.textContent = `${speed}x`;
    animationDelay = Math.max(1, 100 / speed);
}

function setLoading(loading) {
    newMazeBtn.disabled = loading;
    solveBtn.disabled = loading;
    compareBtn.disabled = loading;
    exportBtn.disabled = loading;
    if (loading) {
        newMazeBtn.textContent = 'Generating...';
    } else {
        newMazeBtn.textContent = 'New Maze';
    }
}

async function generateMaze() {
    if (isAnimating) return;

    setLoading(true);
    hideComparison();

    try {
        const seed = seedInput.value ? parseInt(seedInput.value) : undefined;
        const body = {
            width: parseInt(mazeWidthInput.value),
            height: parseInt(mazeHeightInput.value)
        };
        if (seed !== undefined) body.seed = seed;

        const response = await fetch('/api/maze/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!response.ok) throw new Error('Failed to generate maze');

        const data = await response.json();
        currentMaze = data.maze;
        currentStart = data.start;
        currentEnd = data.end;
        generationSteps = data.generation_steps;

        updateStats({
            pathLength: '-',
            cellsVisited: '-',
            genTime: data.generation_time_ms.toFixed(1),
            solveTime: '-',
            algorithm: '-'
        });

        // Calculate cell size based on canvas and maze dimensions
        const maxCanvasSize = Math.min(window.innerWidth - 40, 800);
        cellSize = Math.floor(maxCanvasSize / Math.max(data.width, data.height));
        cellSize = Math.max(4, Math.min(cellSize, 30));

        resizeCanvas(canvas, data.width, data.height);
        await animateGeneration(data);
        drawMaze(currentMaze, currentStart, currentEnd);

    } catch (error) {
        console.error('Error generating maze:', error);
        alert('Failed to generate maze');
    } finally {
        setLoading(false);
    }
}

async function animateGeneration(data) {
    isAnimating = true;
    const grid = data.maze.map(row => [...row]);

    for (const step of generationSteps) {
        if (!isAnimating) break;

        for (const [x, y] of step) {
            if (y < grid.length && x < grid[0].length) {
                grid[y][x] = 0; // PATH
            }
        }

        drawMaze(grid, data.start, data.end);
        await sleep(animationDelay);
    }

    isAnimating = false;
}

async function solveMaze() {
    if (!currentMaze || isAnimating) return;

    setLoading(true);
    hideComparison();

    try {
        const response = await fetch('/api/maze/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                maze: currentMaze,
                start: currentStart,
                end: currentEnd,
                algorithm: 'astar'
            })
        });

        if (!response.ok) throw new Error('Failed to solve maze');

        const data = await response.json();
        await animateSolution(data.path, data.visited);
        updateStats({
            pathLength: data.path_length,
            cellsVisited: data.cells_visited,
            genTime: genTimeEl.textContent,
            solveTime: data.solve_time_ms.toFixed(1),
            algorithm: 'A*'
        });

    } catch (error) {
        console.error('Error solving maze:', error);
        alert('Failed to solve maze');
    } finally {
        setLoading(false);
    }
}

async function animateSolution(path, visited) {
    isAnimating = true;
    const grid = currentMaze.map(row => [...row]);

    // Animate visited cells
    for (const [x, y] of visited) {
        if (!isAnimating) break;
        if (grid[y] && grid[y][x] === 0) {
            grid[y][x] = 3; // VISITED marker
        }
        drawMaze(grid, currentStart, currentEnd);
        await sleep(animationDelay / 2);
    }

    // Animate path
    for (const [x, y] of path) {
        if (!isAnimating) break;
        if (grid[y] && grid[y][x] !== 1) {
            grid[y][x] = 4; // PATH_FOUND marker
        }
        drawMaze(grid, currentStart, currentEnd);
        await sleep(animationDelay);
    }

    isAnimating = false;
}

async function compareAlgorithms() {
    if (!currentMaze || isAnimating) return;

    setLoading(true);

    try {
        const response = await fetch('/api/maze/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                maze: currentMaze,
                start: currentStart,
                end: currentEnd
            })
        });

        if (!response.ok) throw new Error('Failed to compare algorithms');

        const data = await response.json();
        showComparison(data.results);

    } catch (error) {
        console.error('Error comparing algorithms:', error);
        alert('Failed to compare algorithms');
    } finally {
        setLoading(false);
    }
}

function showComparison(results) {
    comparisonContainer.classList.remove('hidden');
    compareStats.classList.remove('hidden');
    canvas.style.display = 'none';

    const canvases = [compareCanvas1, compareCanvas2, compareCanvas3];
    const contexts = [compareCtx1, compareCtx2, compareCtx3];

    results.forEach((result, i) => {
        const algo = result.algorithm;
        const ctx = contexts[i];
        const c = canvases[i];

        // Update stats
        const statEl = compareStats.querySelector(`[data-algo="${algo}"]`);
        if (statEl) {
            statEl.querySelector('.c-length').textContent = result.path_length;
            statEl.querySelector('.c-visited').textContent = result.cells_visited;
            statEl.querySelector('.c-time').textContent = result.solve_time_ms.toFixed(1);
        }

        // Draw maze with path
        resizeCanvas(c, currentMaze[0].length, currentMaze.length);
        drawMazeOnContext(ctx, currentMaze, currentStart, currentEnd, result.path, result.visited);
    });
}

function hideComparison() {
    comparisonContainer.classList.add('hidden');
    compareStats.classList.add('hidden');
    canvas.style.display = 'block';
}

function drawMaze(maze, start, end) {
    drawMazeOnContext(ctx, maze, start, end, null, null);
}

function drawMazeOnContext(ctx, maze, start, end, path, visited) {
    const height = maze.length;
    const width = maze[0].length;

    ctx.clearRect(0, 0, width * cellSize, height * cellSize);

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const cell = maze[y][x];
            const px = x * cellSize;
            const py = y * cellSize;

            let color = COLORS.path;
            if (cell === 1) color = COLORS.wall;

            ctx.fillStyle = color;
            ctx.fillRect(px, py, cellSize, cellSize);

            // Draw grid lines for clarity
            if (cellSize > 6) {
                ctx.strokeStyle = COLORS.gridLine;
                ctx.lineWidth = 0.5;
                ctx.strokeRect(px, py, cellSize, cellSize);
            }
        }
    }

    // Draw visited cells
    if (visited) {
        ctx.fillStyle = COLORS.visited;
        for (const [x, y] of visited) {
            if (maze[y] && maze[y][x] === 0) {
                const px = x * cellSize;
                const py = y * cellSize;
                const padding = Math.max(1, cellSize * 0.15);
                ctx.fillRect(px + padding, py + padding, cellSize - 2 * padding, cellSize - 2 * padding);
            }
        }
    }

    // Draw path
    if (path) {
        ctx.fillStyle = COLORS.pathFound;
        for (const [x, y] of path) {
            if (maze[y] && maze[y][x] !== 1) {
                const px = x * cellSize;
                const py = y * cellSize;
                const padding = Math.max(1, cellSize * 0.1);
                ctx.fillRect(px + padding, py + padding, cellSize - 2 * padding, cellSize - 2 * padding);
            }
        }
    }

    // Draw start
    if (start) {
        const [sx, sy] = start;
        const px = sx * cellSize;
        const py = sy * cellSize;
        const padding = Math.max(2, cellSize * 0.2);
        ctx.fillStyle = COLORS.start;
        ctx.beginPath();
        ctx.arc(px + cellSize / 2, py + cellSize / 2, (cellSize - 2 * padding) / 2, 0, Math.PI * 2);
        ctx.fill();
    }

    // Draw end
    if (end) {
        const [ex, ey] = end;
        const px = ex * cellSize;
        const py = ey * cellSize;
        const padding = Math.max(2, cellSize * 0.2);
        ctx.fillStyle = COLORS.end;
        ctx.beginPath();
        ctx.arc(px + cellSize / 2, py + cellSize / 2, (cellSize - 2 * padding) / 2, 0, Math.PI * 2);
        ctx.fill();
    }
}

function resizeCanvas(canvas, width, height) {
    canvas.width = width * cellSize;
    canvas.height = height * cellSize;
}

function updateStats(stats) {
    pathLengthEl.textContent = stats.pathLength;
    cellsVisitedEl.textContent = stats.cellsVisited;
    genTimeEl.textContent = `${stats.genTime}ms`;
    solveTimeEl.textContent = `${stats.solveTime}ms`;
    algorithmEl.textContent = stats.algorithm;
}

function exportPNG() {
    if (!currentMaze) return;

    // Create a high-res canvas for export
    const exportCanvas = document.createElement('canvas');
    const exportCtx = exportCanvas.getContext('2d');
    const exportCellSize = 20;
    exportCanvas.width = currentMaze[0].length * exportCellSize;
    exportCanvas.height = currentMaze.length * exportCellSize;

    drawMazeOnContext(exportCtx, currentMaze, currentStart, currentEnd, null, null);

    const link = document.createElement('a');
    link.download = `maze-${Date.now()}.png`;
    link.href = exportCanvas.toDataURL('image/png');
    link.click();
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Handle window resize
window.addEventListener('resize', () => {
    if (currentMaze) {
        const maxCanvasSize = Math.min(window.innerWidth - 40, 800);
        cellSize = Math.floor(maxCanvasSize / Math.max(currentMaze[0].length, currentMaze.length));
        cellSize = Math.max(4, Math.min(cellSize, 30));
        resizeCanvas(canvas, currentMaze[0].length, currentMaze.length);
        drawMaze(currentMaze, currentStart, currentEnd);
    }
});

// Initialize on load
document.addEventListener('DOMContentLoaded', init);