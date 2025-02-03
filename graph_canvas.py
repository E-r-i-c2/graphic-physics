from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import numpy as np
from equation_parser import parse_equation

class GraphCanvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure(figsize=(8, 8), facecolor='white')
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.setup_plot()
        
        # Enable pan/zoom
        self.setup_interactions()
        
    def setup_interactions(self):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        
        # Connect mouse events
        self.mpl_connect('button_press_event', self.on_mouse_press)
        self.mpl_connect('button_release_event', self.on_mouse_release)
        self.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.mpl_connect('scroll_event', self.on_scroll)
        
        self.dragging = False
        self.last_x = None
        self.last_y = None
        
    def setup_plot(self):
        self.ax.grid(True, alpha=0.3)
        self.ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)
        self.ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)
        self.ax.set_aspect('equal')
        
        # Remove borders
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        
        # Set initial view limits
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        
    def on_mouse_press(self, event):
        if event.button == 1:  # Left click
            self.dragging = True
            self.last_x = event.xdata
            self.last_y = event.ydata
            
    def on_mouse_release(self, event):
        self.dragging = False
        
    def on_mouse_move(self, event):
        if self.dragging and event.xdata and event.ydata:
            dx = self.last_x - event.xdata
            dy = self.last_y - event.ydata
            
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            self.ax.set_xlim(xlim[0] + dx, xlim[1] + dx)
            self.ax.set_ylim(ylim[0] + dy, ylim[1] + dy)
            
            self.last_x = event.xdata
            self.last_y = event.ydata
            self.draw_idle()
            
    def on_scroll(self, event):
        # Zoom factor
        factor = 1.2 if event.button == 'up' else 1/1.2
        
        # Get current axis limits
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        # Calculate new limits
        xwidth = (xlim[1] - xlim[0]) * factor
        ywidth = (ylim[1] - ylim[0]) * factor
        
        # Set new limits
        self.ax.set_xlim([event.xdata - xwidth/2, event.xdata + xwidth/2])
        self.ax.set_ylim([event.ydata - ywidth/2, event.ydata + ywidth/2])
        
        self.draw_idle()
    
    def plot_equations(self, equations):
        self.ax.clear()
        self.setup_plot()
        
        xlim = self.ax.get_xlim()
        x = np.linspace(xlim[0], xlim[1], 2000)  # Increased resolution
        
        colors = ['#2d70b3', '#388c46', '#fa7e19', '#e6123d', '#6042a6', '#000000']
        
        for i, equation in enumerate(equations):
            try:
                y = parse_equation(equation, x)
                if y is not None:
                    color = colors[i % len(colors)]
                    self.ax.plot(x, y, color=color, linewidth=2)
            except Exception as e:
                print(f"Error plotting equation {equation}: {e}")
        
        self.draw_idle() 