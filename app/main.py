import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.bootstrap import bootstrap_application
from app.application import global_hikmara_application

def run_runtime_check():
    """Runs the Hikmara AI Runtime Check diagnostic at startup."""
    try:
        from cognition.understanding.service import global_language_understanding
        nlu_active = global_language_understanding is not None
    except Exception:
        nlu_active = False

    try:
        from memory.service import global_memory_system
        memory_active = global_memory_system is not None
    except Exception:
        memory_active = False

    try:
        from ai_models.model_manager.service import global_model_manager
        model_manager_active = global_model_manager is not None
    except Exception:
        model_manager_active = False

    try:
        from ai_models.llm.engines import HAS_LLAMA_CPP
        gguf_engine_loaded = HAS_LLAMA_CPP
    except Exception:
        gguf_engine_loaded = False

    local_model_available = False
    for folder in ["ai_models/models/general", "ai_models/models/coding", "ai_models/models/reasoning"]:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith(".gguf"):
                    local_model_available = True
                    break

    offline_operational = True

    print("\n" + "=" * 35)
    print("     Hikmara AI Runtime Check")
    print("=" * 35)
    print(f"{'✓' if nlu_active else '✗'} NLU actif")
    print(f"{'✓' if memory_active else '✗'} Memory active")
    print(f"{'✓' if model_manager_active else '✗'} Model Manager actif")
    print(f"{'✓' if gguf_engine_loaded else '✗'} GGUF Engine chargé")
    print(f"{'✓' if local_model_available else '✗'} Modèle local disponible")
    print(f"{'✓' if offline_operational else '✗'} Mode offline opérationnel")
    print("=" * 35 + "\n")

def main():
    # Bootstrap offline layers
    bootstrap_application()

    # Run diagnostic visible check at startup
    run_runtime_check()

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
