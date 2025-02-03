from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLineEdit, QPushButton, QListWidget,
                           QLabel, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from graph_canvas import GraphCanvas
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
        
        # Equation list
        self.equation_list = QListWidget()
        self.equation_list.itemDoubleClicked.connect(self.remove_equation)
        
        # Add widgets to left panel
        left_layout.addWidget(self.equation_input)
        left_layout.addWidget(instructions)
        left_layout.addWidget(self.equation_list)
        
        # Graph canvas
        self.graph_canvas = GraphCanvas()
        
        # Add panels to main layout
        layout.addWidget(left_panel, 1)
        layout.addWidget(self.graph_canvas, 4)
        
        self.equations = []
        
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
            self.equations.append(equation)
            self.equation_list.addItem(equation)
            self.equation_input.clear()
            self.graph_canvas.plot_equations(self.equations)
    
    def remove_equation(self, item):
        equation = item.text()
        self.equations.remove(equation)
        self.equation_list.takeItem(self.equation_list.row(item))
        self.graph_canvas.plot_equations(self.equations) 