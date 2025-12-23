r"""╔══════════════════════════════════════════════════════════════════╗
║    ____                 _                      _                  ║
║   |  _ \  _____   _____| | ___  _ __   ___  __| |                ║
║   | | | |/ _ \ \ / / _ \ |/ _ \| '_ \ / _ \/ _` |               ║
║   | |_| |  __/\ V /  __/ | (_) | |_) |  __/ (_| |               ║
║   |____/ \___| \_/ \___|_|\___/| .__/ \___|\ __,_|               ║
║                                 |_|                               ║
╠══════════════════════════════════════════════════════════════════╣
║  by zuckdorsey • 2025                                         ║
║  https://github.com/zuckdorsey                                                       ║
╚══════════════════════════════════════════════════════════════════╝"""

import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor, QLinearGradient

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.main_window import FilePermissionChecker

class ModernSplashScreen(QSplashScreen):    
    def __init__(self):
        pixmap = QPixmap(480, 320)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(13, 13, 13))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 480, 320, 12, 12)

        painter.setPen(QColor(31, 31, 31))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(1, 1, 478, 318, 12, 12)

        painter.setPen(QColor(229, 229, 229))
        title_font = QFont('Inter', 22, QFont.DemiBold)
        if not title_font.exactMatch():
            title_font = QFont('Segoe UI', 22, QFont.DemiBold)
        painter.setFont(title_font)
        painter.drawText(0, 110, 480, 40, Qt.AlignCenter, "File Permission Checker")

        subtitle_font = QFont('Inter', 12)
        if not subtitle_font.exactMatch():
            subtitle_font = QFont('Segoe UI', 12)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(115, 115, 115))
        painter.drawText(0, 155, 480, 24, Qt.AlignCenter, "Scan • Analyze • Secure")

        version_font = QFont('Inter', 10)
        if not version_font.exactMatch():
            version_font = QFont('Segoe UI', 10)
        painter.setFont(version_font)
        painter.setPen(QColor(82, 82, 82))
        painter.drawText(0, 190, 480, 20, Qt.AlignCenter, "v2.0")

        painter.setBrush(QColor(26, 26, 26))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(140, 240, 200, 4, 2, 2)

        painter.end()

        super().__init__(pixmap)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        self._progress = 0
        self._loading_steps = [
            "Initializing...",
            "Loading modules...",
            "Preparing database...",
            "Setting up security...",
            "Loading interface...",
            "Almost ready..."
        ]

    def showMessage(self, message: str):
        super().showMessage(
            message,
            Qt.AlignBottom | Qt.AlignHCenter,
            QColor(115, 115, 115)
        )

def load_styles(app: QApplication):
    style_path = os.path.join(os.path.dirname(__file__), 'style.qss')

    if os.path.exists(style_path):
        with open(style_path, 'r') as f:
            app.setStyleSheet(f.read())
    else:
        app.setStyleSheet("""
            QMainWindow { background-color:
            QWidget { color:
            QPushButton {
                background:
                border: 1px solid
                border-radius: 6px;
                padding: 10px 20px;
                color:
                font-weight: 500;
            }
            QPushButton:hover {
                background:
            }
        """)

def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("File Permission Checker")
    app.setApplicationVersion("2.0.0")

    splash = ModernSplashScreen()
    splash.show()
    app.processEvents()

    import time
    
    splash.showMessage("Initializing...")
    app.processEvents()
    time.sleep(0.4)
    
    splash.showMessage("Loading modules...")
    app.processEvents()
    time.sleep(0.3)

    load_styles(app)
    
    splash.showMessage("Preparing database...")
    app.processEvents()
    time.sleep(0.3)
    
    splash.showMessage("Setting up security...")
    app.processEvents()
    time.sleep(0.3)

    splash.showMessage("Loading interface...")
    app.processEvents()
    time.sleep(0.4)

    window = FilePermissionChecker()
    
    splash.showMessage("Ready!")
    app.processEvents()
    time.sleep(0.3)
    
    window.show()
    splash.finish(window)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
