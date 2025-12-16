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
        pixmap = QPixmap(550, 350)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, 550, 350)
        gradient.setColorAt(0, QColor(15, 15, 26))
        gradient.setColorAt(0.5, QColor(26, 26, 46))
        gradient.setColorAt(1, QColor(22, 33, 62))

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 550, 350, 20, 20)

        gradient2 = QLinearGradient(0, 0, 550, 0)
        gradient2.setColorAt(0, QColor(102, 126, 234, 80))
        gradient2.setColorAt(1, QColor(118, 75, 162, 80))

        painter.setBrush(gradient2)
        painter.drawEllipse(380, -80, 250, 250)
        painter.drawEllipse(-80, 200, 200, 200)

        painter.setPen(QColor(255, 255, 255))

        title_font = QFont('Segoe UI', 26, QFont.Bold)
        painter.setFont(title_font)
        painter.drawText(0, 120, 550, 45, Qt.AlignCenter, " File Permission Checker")

        subtitle_font = QFont('Segoe UI', 13)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(148, 163, 184))
        painter.drawText(0, 170, 550, 25, Qt.AlignCenter, "Scan • Analyze • Fix Permissions")

        version_font = QFont('Segoe UI', 10)
        painter.setFont(version_font)
        painter.setPen(QColor(102, 126, 234))
        painter.drawText(0, 210, 550, 20, Qt.AlignCenter, "v2.0.0")

        painter.end()

        super().__init__(pixmap)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    def showMessage(self, message: str):
        super().showMessage(
            f"  {message}",
            Qt.AlignBottom | Qt.AlignHCenter,
            QColor(148, 163, 184)
        )

def load_styles(app: QApplication):
    style_path = os.path.join(os.path.dirname(__file__), 'style.qss')

    if os.path.exists(style_path):
        with open(style_path, 'r') as f:
            app.setStyleSheet(f.read())
    else:
        app.setStyleSheet("""
            QMainWindow { background-color: #1a1a2e; }
            QWidget { color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 
#764ba2);

                border: none; border-radius: 8px; padding: 10px 20px;
                color: white; font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 
#8b5fbf);

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

    splash.showMessage("Loading modules...")
    app.processEvents()

    load_styles(app)

    splash.showMessage("Initializing interface...")
    app.processEvents()

    window = FilePermissionChecker()
    window.show()

    splash.finish(window)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()