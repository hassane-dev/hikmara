import re
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt

class ChatBubble(QFrame):
    """Elegant message bubble with distinct user (aligned right) and assistant (aligned left) styles."""
    def __init__(self, sender: str, text: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.sender = sender
        self.text = text
        self.init_ui()

    def _parse_markdown_to_html(self, raw_text: str) -> str:
        """Lightweight robust markdown, code, list, and LaTeX equation parser."""
        html = raw_text

        # 1. Heading formatting
        html = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

        # 2. Bold and Italic formatting
        html = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", html)
        html = re.sub(r"\*(.*?)\*", r"<i>\1</i>", html)

        # 3. Code blocks formatting
        html = re.sub(r"```[a-zA-Z0-9]*\n(.*?)\n```", r"<pre style='background-color: #2d2d2d; color: #a9dc76; padding: 8px; border-radius: 4px;'><code>\1</code></pre>", html, flags=re.DOTALL)
        html = re.sub(r"`(.*?)`", r"<code style='background-color: #2d2d2d; color: #fc9867; padding: 2px 4px; border-radius: 2px;'>\1</code>", html)

        # 4. Bullet lists formatting
        html = re.sub(r"^\s*[\*\-]\s+(.*?)$", r"<li>\1</li>", html, flags=re.MULTILINE)

        # 5. LaTeX equations formatting placeholders (e.g. Delta, Pi, Root)
        html = html.replace("\\Delta", "&Delta;")
        html = html.replace("\\pi", "&pi;")
        html = html.replace("\\sqrt", "&radic;")

        # Convert linebreaks to <br/> safely
        html = html.replace("\n", "<br/>")
        return html

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(main_layout)

        # Message Container Frame
        bubble_frame = QFrame()
        bubble_layout = QVBoxLayout()
        bubble_frame.setLayout(bubble_layout)

        # Parse message content
        html_content = self._parse_markdown_to_html(self.text)

        # Title/Sender label with timestamp
        sender_title = "Vous" if self.sender == "user" else "Hikmara AI"
        title_label = QLabel(f"<b>{sender_title}</b>")
        title_label.setStyleSheet("color: #aaaaaa; font-size: 10px;")
        bubble_layout.addWidget(title_label)

        # Content text label
        text_label = QLabel()
        text_label.setWordWrap(True)
        text_label.setTextFormat(Qt.TextFormat.RichText)
        text_label.setText(html_content)
        bubble_layout.addWidget(text_label)

        # Style based on sender
        if self.sender == "user":
            bubble_frame.setStyleSheet("""
                QFrame {
                    background-color: #0e639c;
                    color: #ffffff;
                    border-radius: 12px;
                    border: 1px solid #1177bb;
                    padding: 8px;
                }
            """)
            main_layout.addStretch()
            main_layout.addWidget(bubble_frame)
        else:
            bubble_frame.setStyleSheet("""
                QFrame {
                    background-color: #252526;
                    color: #ffffff;
                    border-radius: 12px;
                    border: 1px solid #3c3c3c;
                    padding: 8px;
                }
            """)
            main_layout.addWidget(bubble_frame)
            main_layout.addStretch()


class VirtualChatList(QScrollArea):
    """Scrollable viewport representing chat messages as individual clean speech bubbles."""
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setStyleSheet("background-color: transparent; border: none;")

        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.addStretch()
        self.container.setLayout(self.container_layout)
        self.setWidget(self.container)

    def append_message(self, sender: str, text: str):
        """Creates and appends a clean ChatBubble into the chat list."""
        bubble = ChatBubble(sender, text)
        # Insert before the last stretch spacer
        self.container_layout.insertWidget(self.container_layout.count() - 1, bubble)

    def clear(self):
        """Clears all chat bubbles from the list viewport."""
        while self.container_layout.count() > 1:
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
