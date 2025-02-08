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
        
        # Connect mouse events for panning
        self.mpl_connect('button_press_event', self.on_mouse_press)
        self.mpl_connect('button_release_event', self.on_mouse_release)
        self.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.mpl_connect('scroll_event', self.on_scroll)
        
        self.dragging = False
        self.last_mouse_pos = None
        self.current_equations = []
        
        # Add keyboard shortcuts for zoom
        self.zoom_factor = 1.2
        
        def zoom_in(event):
            self.zoom(self.zoom_factor)
        
        def zoom_out(event):
            self.zoom(1/self.zoom_factor)
        
        self.mpl_connect('key_press_event', lambda event: 
            zoom_in(event) if event.key == '+' or event.key == '=' else 
            zoom_out(event) if event.key == '-' or event.key == '_' else None)
        
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
            self.last_mouse_pos = (event.xdata, event.ydata)
            
    def on_mouse_release(self, event):
        self.dragging = False
        self.last_mouse_pos = None
        
    def on_mouse_move(self, event):
        if self.dragging and event.xdata and event.ydata and self.last_mouse_pos:
            # Calculate the movement delta
            dx = self.last_mouse_pos[0] - event.xdata
            dy = self.last_mouse_pos[1] - event.ydata
            
            # Update the view limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            self.ax.set_xlim(xlim[0] + dx, xlim[1] + dx)
            self.ax.set_ylim(ylim[0] + dy, ylim[1] + dy)
            
            # Update last position
            self.last_mouse_pos = (event.xdata, event.ydata)
            
            # Redraw
            self.draw_idle()
    
    def on_scroll(self, event):
        # Reduce zoom sensitivity
        factor = 1.05 if event.button == 'up' else 1/1.05  # Changed from 1.1 to 1.05
        
        if event.xdata is None or event.ydata is None:
            return
        
        # Get current axis limits
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        # Calculate new width and height
        xwidth = (xlim[1] - xlim[0]) * factor
        ywidth = (ylim[1] - ylim[0]) * factor
        
        # Set new limits while maintaining aspect ratio
        size = max(xwidth, ywidth)
        self.ax.set_xlim([event.xdata - size/2, event.xdata + size/2])
        self.ax.set_ylim([event.ydata - size/2, event.ydata + size/2])
        
        self.draw_idle()
    
    def draw_zoom_box(self):
        if not hasattr(self, 'current_equations'):
            self.current_equations = []
        
        self.ax.clear()
        self.setup_plot()
        self.plot_current_equations()
        
        if self.drag_start and self.drag_end and None not in (self.drag_start + self.drag_end):
            x = [self.drag_start[0], self.drag_end[0], self.drag_end[0], self.drag_start[0], self.drag_start[0]]
            y = [self.drag_start[1], self.drag_start[1], self.drag_end[1], self.drag_end[1], self.drag_start[1]]
            self.ax.plot(x, y, 'k--', alpha=0.5)
        
        self.draw_idle()
    
    def plot_current_equations(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        # Use wider range for x values to ensure lines extend beyond view
        margin = (xlim[1] - xlim[0]) * 0.5
        x = np.linspace(xlim[0] - margin, xlim[1] + margin, 2000)
        
        colors = ['#2d70b3', '#388c46', '#fa7e19', '#e6123d', '#6042a6', '#000000']
        
        for i, equation in enumerate(self.current_equations):
            try:
                if equation.startswith('x='):  # Handle vertical lines specially
                    x_val = float(equation[2:])
                    if xlim[0] <= x_val <= xlim[1]:
                        color = colors[i % len(colors)]
                        self.ax.axvline(x=x_val, color=color, linewidth=2)
                else:
                    result = parse_equation(equation, x)
                    if result is not None:
                        color = colors[i % len(colors)]
                        if isinstance(result, list):  # Multiple y values (e.g., for circles)
                            if len(result) == 3:  # Circle with custom x values
                                y_pos, y_neg, x_custom = result
                                self.ax.plot(x_custom, y_pos, color=color, linewidth=2)
                                self.ax.plot(x_custom, y_neg, color=color, linewidth=2)
                            else:  # Other multi-valued functions
                                for y_part in result:
                                    self.ax.plot(x, y_part, color=color, linewidth=2)
                        else:
                            self.ax.plot(x, result, color=color, linewidth=2)
            except Exception as e:
                print(f"Error plotting equation {equation}: {e}")
    
    def plot_equations(self, equations):
        self.current_equations = equations
        self.ax.clear()
        self.setup_plot()
        self.plot_current_equations()
        self.draw_idle()
    
    def zoom_to_box(self):
        if (self.drag_start and self.drag_end and 
            None not in (self.drag_start + self.drag_end) and
            self.drag_start != self.drag_end):
            
            x_min = min(self.drag_start[0], self.drag_end[0])
            x_max = max(self.drag_start[0], self.drag_end[0])
            y_min = min(self.drag_start[1], self.drag_end[1])
            y_max = max(self.drag_start[1], self.drag_end[1])
            
            # Ensure minimum zoom box size
            if abs(x_max - x_min) < 0.1 or abs(y_max - y_min) < 0.1:
                return
            
            # Add a small margin
            margin = 0.05
            dx = (x_max - x_min) * margin
            dy = (y_max - y_min) * margin
            
            # Set new limits while maintaining aspect ratio
            center_x = (x_max + x_min) / 2
            center_y = (y_max + y_min) / 2
            
            width = (x_max - x_min) * (1 + 2 * margin)
            height = (y_max - y_min) * (1 + 2 * margin)
            
            # Make the box square to maintain aspect ratio
            size = max(width, height)
            
            self.ax.set_xlim(center_x - size/2, center_x + size/2)
            self.ax.set_ylim(center_y - size/2, center_y + size/2)
        
        self.drag_start = None
        self.drag_end = None
        self.draw_idle()
    
    def zoom(self, factor):
        # Get current axis center
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        xcenter = (xlim[1] + xlim[0]) / 2
        ycenter = (ylim[1] + ylim[0]) / 2
        
        # Calculate new width and height
        xwidth = (xlim[1] - xlim[0]) / factor
        ywidth = (ylim[1] - ylim[0]) / factor
        
        # Set new limits
        self.ax.set_xlim([xcenter - xwidth/2, xcenter + xwidth/2])
        self.ax.set_ylim([ycenter - ywidth/2, ycenter + ywidth/2])
        
        self.draw_idle() 