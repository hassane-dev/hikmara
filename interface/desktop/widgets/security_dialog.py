from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

class SecurityConsentDialog(QDialog):
    def __init__(self, parent=None, module="", action="", parameters=None):
        super().__init__(parent)
        self.setWindowTitle("Security Policy Consent")
        self.approved = False
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Module '{module}' wants to execute '{action}'"))
        btn_layout = QHBoxLayout()
        approve = QPushButton("Approve")
        approve.clicked.connect(self.accept_action)
        deny = QPushButton("Deny")
        deny.clicked.connect(self.reject)
        btn_layout.addWidget(deny)
        btn_layout.addWidget(approve)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def accept_action(self):
        self.approved = True
        self.accept()
