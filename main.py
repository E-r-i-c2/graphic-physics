import sys
from PyQt6.QtWidgets import QApplication
from graphing_window import GraphingWindow

def main():
    app = QApplication(sys.argv)
    window = GraphingWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 