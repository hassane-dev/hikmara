import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.bootstrap import bootstrap_application
from app.application import global_hikmara_application

def main():
    # Bootstrap offline layers
    bootstrap_application()

    # Run central application structures
    global_hikmara_application.initialize_and_run()

    # If standard execution without UI parameters, let the user know success
    print("Hikmara AI successfully started in headless offline mode!")

if __name__ == "__main__":
    main()
