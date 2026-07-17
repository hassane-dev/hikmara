import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.bootstrap import bootstrap_application
from app.application import global_hikmara_application

def main():
    # Bootstrap offline layers
    bootstrap_application()

    # Determine execution mode (headless vs GUI)
    headless_arg = "--headless" in sys.argv
    headless_env = os.environ.get("HIKMARA_HEADLESS") == "1"

    if headless_arg or headless_env:
        print("Starting Hikmara AI in headless offline mode...")
        # Run central application structures
        global_hikmara_application.initialize_and_run()
        print("Hikmara AI successfully started in headless offline mode!")
        sys.exit(0)

    print("Starting Hikmara AI with PyQt6 GUI...")
    # Run central application structures
    global_hikmara_application.initialize_and_run()

    from PyQt6.QtWidgets import QApplication
    from interface.desktop.main_window import HikmaraMainWindow
    from PyQt6.QtCore import QTimer

    app = QApplication(sys.argv)
    window = HikmaraMainWindow()
    window.show()

    # If running offscreen, set a timer to exit cleanly after 2 seconds
    # so automated headless verification doesn't hang forever.
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        print("Offscreen platform detected. Scheduling clean auto-exit in 2 seconds...")
        QTimer.singleShot(2000, app.quit)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
