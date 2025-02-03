class GraphingCalculator {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.equations = new Map();
        this.scale = 50; // pixels per unit
        this.offsetX = this.canvas.width / 2;
        this.offsetY = this.canvas.height / 2;
        
        this.setupCanvas();
        this.setupEventListeners();
    }

    setupCanvas() {
        // Handle high DPI displays
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = this.canvas.clientWidth * dpr;
        this.canvas.height = this.canvas.clientHeight * dpr;
        this.ctx.scale(dpr, dpr);
        
        // Set canvas style
        this.ctx.lineWidth = 2;
        this.ctx.lineCap = 'round';
    }

    setupEventListeners() {
        let isDragging = false;
        let lastX = 0;
        let lastY = 0;

        this.canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            lastX = e.clientX;
            lastY = e.clientY;
        });

        this.canvas.addEventListener('mousemove', (e) => {
            if (isDragging) {
                this.offsetX += e.clientX - lastX;
                this.offsetY += e.clientY - lastY;
                lastX = e.clientX;
                lastY = e.clientY;
                this.draw();
            }
        });

        this.canvas.addEventListener('mouseup', () => {
            isDragging = false;
        });

        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
            this.scale *= zoomFactor;
            this.draw();
        });
    }

    addEquation(id, equation) {
        this.equations.set(id, equation);
        this.draw();
    }

    removeEquation(id) {
        this.equations.delete(id);
        this.draw();
    }

    evaluateEquation(equation, x) {
        // Create a safe evaluation context
        const context = { x: x, Math: Math };
        try {
            return Function('x', 'Math', `return ${equation}`)(x, Math);
        } catch (e) {
            return NaN;
        }
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawGrid();
        this.drawAxes();
        this.drawEquations();
    }

    drawGrid() {
        const gridSize = this.scale / 5;
        this.ctx.strokeStyle = '#eee';
        this.ctx.lineWidth = 0.5;

        // Vertical lines
        for (let x = this.offsetX % gridSize; x < this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        // Horizontal lines
        for (let y = this.offsetY % gridSize; y < this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    drawAxes() {
        this.ctx.strokeStyle = '#000';
        this.ctx.lineWidth = 1;

        // X-axis
        this.ctx.beginPath();
        this.ctx.moveTo(0, this.offsetY);
        this.ctx.lineTo(this.canvas.width, this.offsetY);
        this.ctx.stroke();

        // Y-axis
        this.ctx.beginPath();
        this.ctx.moveTo(this.offsetX, 0);
        this.ctx.lineTo(this.offsetX, this.canvas.height);
        this.ctx.stroke();
    }

    drawEquations() {
        this.equations.forEach((equation, id) => {
            this.ctx.strokeStyle = this.getColor(id);
            this.ctx.beginPath();
            
            const startX = (-this.offsetX) / this.scale;
            const endX = (this.canvas.width - this.offsetX) / this.scale;
            const step = 1 / this.scale;

            let lastY = null;
            
            for (let x = startX; x <= endX; x += step) {
                const y = this.evaluateEquation(equation, x);
                const screenX = x * this.scale + this.offsetX;
                const screenY = -y * this.scale + this.offsetY;

                if (lastY === null || Math.abs(screenY - lastY) < 1000) {
                    if (lastY === null) {
                        this.ctx.moveTo(screenX, screenY);
                    } else {
                        this.ctx.lineTo(screenX, screenY);
                    }
                    lastY = screenY;
                } else {
                    this.ctx.moveTo(screenX, screenY);
                    lastY = screenY;
                }
            }
            
            this.ctx.stroke();
        });
    }

    getColor(id) {
        const colors = ['#2d70b3', '#388c46', '#fa7e19', '#cf256d', '#6042a6'];
        return colors[id % colors.length];
    }
} 