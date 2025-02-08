from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLineEdit, QPushButton, QListWidget,
                           QLabel, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from graph_canvas import GraphCanvas
from editable_equation import EditableEquation
import numpy as np

class EquationWidget(QFrame):
    def __init__(self, equation, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QHBoxLayout(self)
        self.equation_label = QLabel(equation)
        self.delete_button = QPushButton("×")
        self.delete_button.setFixedSize(20, 20)
        
        layout.addWidget(self.equation_label)
        layout.addWidget(self.delete_button)

class GraphingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphing Calculator")
        self.setMinimumSize(1000, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel for equations
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Equation input
        self.equation_input = QLineEdit()
        self.equation_input.setPlaceholderText("Enter equation (e.g., y=2x+1)")
        self.equation_input.returnPressed.connect(self.add_equation)
        
        # Instructions
        instructions = QLabel("• Type an equation (e.g., y=x^2)\n"
                            "• Press Enter to add\n"
                            "• Double-click to remove\n"
                            "• Drag to pan, scroll to zoom")
        instructions.setStyleSheet("color: gray;")
        
        # Replace QVBoxLayout with QWidget and QVBoxLayout
        equation_widget = QWidget()
        self.equation_list = QVBoxLayout(equation_widget)
        self.equation_list.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Add scroll area for equations
        scroll = QScrollArea()
        scroll.setWidget(equation_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Update left panel layout
        left_layout.addWidget(self.equation_input)
        left_layout.addWidget(instructions)
        left_layout.addWidget(scroll)
        
        # Graph canvas
        self.graph_canvas = GraphCanvas()
        
        # Add panels to main layout
        layout.addWidget(left_panel, 1)
        layout.addWidget(self.graph_canvas, 4)
        
        # Store equations in a list instead of dict
        self.equations = []
        self.equation_widgets = []
        
        # Style
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
    
    def add_equation(self):
        equation = self.equation_input.text().strip()
        if equation:
            # Create editable equation widget
            eq_widget = EditableEquation(equation, self)
            eq_widget.equation_changed.connect(self.update_equation)
            eq_widget.delete_requested.connect(self.remove_equation)
            
            self.equations.append(equation)
            self.equation_widgets.append(eq_widget)
            self.equation_list.addWidget(eq_widget)
            self.equation_input.clear()
            self.graph_canvas.plot_equations(self.equations)
    
    def update_equation(self, old_eq, new_eq):
        if old_eq in self.equations:
            index = self.equations.index(old_eq)
            self.equations[index] = new_eq
            self.graph_canvas.plot_equations(self.equations)
    
    def remove_equation(self, equation):
        if equation in self.equations:
            index = self.equations.index(equation)
            self.equations.pop(index)
            widget = self.equation_widgets.pop(index)
            self.equation_list.removeWidget(widget)
            widget.deleteLater()
            self.graph_canvas.plot_equations(self.equations) 