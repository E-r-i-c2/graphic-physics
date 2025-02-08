from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal

class EditableEquation(QWidget):
    equation_changed = pyqtSignal(str, str)  # old_eq, new_eq
    delete_requested = pyqtSignal(str)  # equation
    
    def __init__(self, equation, parent=None):
        super().__init__(parent)
        self.equation = equation
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Equation editor
        self.editor = QLineEdit(equation)
        self.editor.returnPressed.connect(self.update_equation)
        
        # Delete button
        self.delete_button = QPushButton("×")
        self.delete_button.setFixedSize(20, 20)
        self.delete_button.clicked.connect(self.request_delete)
        
        layout.addWidget(self.editor)
        layout.addWidget(self.delete_button)
        
    def update_equation(self):
        new_eq = self.editor.text().strip()
        if new_eq and new_eq != self.equation:
            old_eq = self.equation
            self.equation = new_eq
            self.equation_changed.emit(old_eq, new_eq)
    
    def request_delete(self):
        self.delete_requested.emit(self.equation) 