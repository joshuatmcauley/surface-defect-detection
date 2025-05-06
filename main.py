import sys
import os
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def main():
    """Main application entry point"""
    try:
        # Create application instance
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Start the application event loop
        return app.exec()
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())