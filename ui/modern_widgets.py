r"""╔══════════════════════════════════════════════════════════════════╗
║    ____                 _                      _                  ║
║   |  _ \  _____   _____| | ___  _ __   ___  __| |                ║
║   | | | |/ _ \ \ / / _ \ |/ _ \| '_ \ / _ \/ _` |               ║
║   | |_| |  __/\ V /  __/ | (_) | |_) |  __/ (_| |               ║
║   |____/ \___| \_/ \___|_|\___/| .__/ \___|\__,_|               ║
║                                 |_|                               ║
╠══════════════════════════════════════════════════════════════════╣
║  by zuckdorsey • 2025                                         ║
║  https://github.com/zuckdorsey                                                       ║
╚══════════════════════════════════════════════════════════════════╝"""

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QProgressBar, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy, QHeaderView
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, pyqtProperty,
    QTimer, QSize, QPoint, QRect
)
from PyQt6.QtGui import (
    QColor, QFont, QPainter, QPainterPath, QBrush,
    QLinearGradient, QPen, QIcon
)


class GlassCard(QFrame):
    """Minimalist card component"""
    
    def __init__(self, parent=None, blur_radius: int = 10):
        super().__init__(parent)
        self.blur_radius = blur_radius
        self.setObjectName("glassCard")
        self._setup_style()
        self._setup_shadow()
    
    def _setup_style(self):
        self.setStyleSheet("""
            QFrame#glassCard {
                background: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 8px;
            }
        """)
    
    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(self.blur_radius)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class ModernButton(QPushButton):
    """Minimalist flat button with distinct styles"""
    
    STYLES = {
        'primary': {
            'bg': '#333333',
            'hover': '#404040',
            'pressed': '#4a4a4a',
            'border': '#404040'
        },
        'success': {
            'bg': '#166534',
            'hover': '#15803d',
            'pressed': '#14532d',
            'border': '#15803d'
        },
        'warning': {
            'bg': '#854d0e',
            'hover': '#a16207',
            'pressed': '#713f12',
            'border': '#a16207'
        },
        'danger': {
            'bg': '#991b1b',
            'hover': '#b91c1c',
            'pressed': '#7f1d1d',
            'border': '#b91c1c'
        },
        'secondary': {
            'bg': '#1f1f1f',
            'hover': '#262626',
            'pressed': '#2a2a2a',
            'border': '#333333'
        },
        'encrypt': {
            'bg': '#166534',
            'hover': '#15803d',
            'pressed': '#14532d',
            'border': '#22c55e'
        },
        'decrypt': {
            'bg': '#1e40af',
            'hover': '#1d4ed8',
            'pressed': '#1e3a8a',
            'border': '#3b82f6'
        }
    }
    
    def __init__(self, text: str = "", icon: str = None, 
                 style: str = "primary", parent=None):
        super().__init__(text, parent)
        self.button_style = style
        self.update_style()
        
        if icon:
            self.setIcon(QIcon(icon))
            self.setIconSize(QSize(16, 16))
    
    def update_style(self, style: str = None):
        if style:
            self.button_style = style
        style_config = self.STYLES.get(self.button_style, self.STYLES['primary'])
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {style_config['bg']};
                border: 1px solid {style_config['border']};
                border-radius: 6px;
                padding: 10px 20px;
                color:
                font-weight: 500;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {style_config['hover']};
            }}
            QPushButton:pressed {{
                background: {style_config['pressed']};
            }}
            QPushButton:disabled {{
                background:
                color:
                border: 1px solid
            }}
        """)
    
    def enterEvent(self, event):
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        super().leaveEvent(event)


class AnimatedProgressBar(QProgressBar):
    """Minimalist progress bar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(True)
        self.setMinimumHeight(24)
        self._glow_opacity = 0.5
        self._setup_style()
        
        self._glow_timer = QTimer(self)
        self._glow_timer.timeout.connect(self._animate_glow)
        self._glow_direction = 1
    
    def _setup_style(self):
        self.setStyleSheet("""
            QProgressBar {
                background:
                border: 1px solid
                border-radius: 4px;
                text-align: center;
                color:
                font-weight: 500;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background:
                border-radius: 3px;
            }
        """)
    
    def _animate_glow(self):
        self._glow_opacity += 0.05 * self._glow_direction
        if self._glow_opacity >= 1.0:
            self._glow_direction = -1
        elif self._glow_opacity <= 0.3:
            self._glow_direction = 1
        self.update()
    
    def start_glow_animation(self):
        self._glow_timer.start(50)
    
    def stop_glow_animation(self):
        self._glow_timer.stop()
        self._glow_opacity = 0.5
    
    def setValue(self, value):
        super().setValue(value)
        if value > 0 and value < 100:
            self.start_glow_animation()
        else:
            self.stop_glow_animation()


class PillBadge(QLabel):
    """Minimalist risk badges"""
    
    RISK_STYLES = {
        'High': {
            'bg': 'rgba(239, 68, 68, 0.15)',
            'border': 'rgba(239, 68, 68, 0.3)',
            'text': '#fca5a5'
        },
        'Medium': {
            'bg': 'rgba(251, 191, 36, 0.15)',
            'border': 'rgba(251, 191, 36, 0.3)',
            'text': '#fcd34d'
        },
        'Low': {
            'bg': 'rgba(74, 222, 128, 0.15)',
            'border': 'rgba(74, 222, 128, 0.3)',
            'text': '#86efac'
        }
    }
    
    def __init__(self, risk_level: str = "Low", show_icon: bool = False, parent=None):
        super().__init__(parent)
        self.risk_level = risk_level
        self.show_icon = show_icon
        self._apply_style()
    
    def _apply_style(self):
        style = self.RISK_STYLES.get(self.risk_level, self.RISK_STYLES['Low'])
        
        self.setText(self.risk_level)
        
        self.setStyleSheet(f"""
            QLabel {{
                background: {style['bg']};
                border: 1px solid {style['border']};
                border-radius: 4px;
                padding: 4px 10px;
                color: {style['text']};
                font-weight: 500;
                font-size: 11px;
            }}
        """)
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def set_risk_level(self, level: str):
        self.risk_level = level
        self._apply_style()


class ModernTableWidget(QTableWidget):
    """Minimalist table with readable text"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
        self._setup_headers()
    
    def _setup_style(self):
        self.setStyleSheet("""
            QTableWidget {
                background:
                border: 1px solid
                border-radius: 6px;
                gridline-color:
                selection-background-color:
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid
                color:
            }
            QTableWidget::item:selected {
                background:
                color:
            }
            QTableWidget::item:hover {
                background:
            }
            QHeaderView::section {
                background:
                border: none;
                border-bottom: 1px solid
                border-right: 1px solid
                padding: 10px 8px;
                color:
                font-weight: 600;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:hover {
                background:
            }
        """)
        
        self.setAlternatingRowColors(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
    
    def _setup_headers(self):
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setMinimumSectionSize(80)


class RiskTableWidgetItem(QTableWidgetItem):
    
    COLORS = {
        'High': {
            'bg': QColor(239, 68, 68, 60),
            'fg': QColor(252, 165, 165)
        },
        'Medium': {
            'bg': QColor(245, 158, 11, 60),
            'fg': QColor(252, 211, 77)
        },
        'Low': {
            'bg': QColor(16, 185, 129, 60),
            'fg': QColor(110, 231, 183)
        }
    }
    
    def __init__(self, text: str, risk_level: str = "Low"):
        super().__init__(text)
        self.risk_level = risk_level
        self._apply_style()
    
    def _apply_style(self):
        colors = self.COLORS.get(self.risk_level, self.COLORS['Low'])
        
        self.setBackground(colors['bg'])
        self.setForeground(colors['fg'])
        self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        font = QFont('Segoe UI', 10)
        font.setBold(True)
        self.setFont(font)


class StatCard(GlassCard):
    
    def __init__(self, title: str, value: str = "0", 
                 icon: str = "📊", color: str = "#667eea", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"""
            font-size: 24px;
            background: rgba(102, 126, 234, 0.2);
            border-radius: 10px;
            padding: 8px;
        """)
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 700;
            color: {self.color};
        """)
        layout.addWidget(self.value_label)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 13px;
            color:
            font-weight: 500;
        """)
        layout.addWidget(title_label)
        
        self.setMinimumSize(180, 140)
    
    def set_value(self, value: str):
        self.value = value
        self.value_label.setText(value)


class ToastNotification(QFrame):
    """Minimalist toast notification with visible text"""
    
    TYPES = {
        'success': {
            'bg': '#166534',
            'border': '#15803d',
            'icon': '✓'
        },
        'error': {
            'bg': '#991b1b',
            'border': '#b91c1c',
            'icon': '✕'
        },
        'warning': {
            'bg': '#854d0e',
            'border': '#a16207',
            'icon': '!'
        },
        'info': {
            'bg': '#1e3a5f',
            'border': '#2563eb',
            'icon': 'i'
        }
    }
    
    def __init__(self, message: str, toast_type: str = "info", 
                 duration: int = 3000, parent=None):
        super().__init__(parent)
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        self._setup_ui()
        self._setup_animation()
    
    def _setup_ui(self):
        config = self.TYPES.get(self.toast_type, self.TYPES['info'])
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {config['bg']};
                border: 1px solid {config['border']};
                border-radius: 6px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)
        
        icon_label = QLabel(config['icon'])
        icon_label.setStyleSheet("""
            color:
            font-size: 14px;
            font-weight: 700;
            background: transparent;
        """)
        layout.addWidget(icon_label)
        
        msg_label = QLabel(self.message)
        msg_label.setStyleSheet("""
            color:
            font-weight: 500;
            font-size: 13px;
            background: transparent;
        """)
        layout.addWidget(msg_label)
        
        self.setFixedHeight(44)
        self.setMinimumWidth(220)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
    
    def _setup_animation(self):
        self._opacity = 1.0
        
        self._hide_timer = QTimer(self)
        self._hide_timer.timeout.connect(self._fade_out)
        self._hide_timer.setSingleShot(True)
    
    def show(self):
        super().show()
        self._hide_timer.start(self.duration)
    
    def _fade_out(self):
        self.hide()


class LoadingSpinner(QWidget):
    
    def __init__(self, size: int = 40, parent=None):
        super().__init__(parent)
        self._size = size
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        
        self.setFixedSize(size, size)
    
    def _rotate(self):
        self._angle = (self._angle + 10) % 360
        self.update()
    
    def start(self):
        self._timer.start(30)
    
    def stop(self):
        self._timer.stop()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx = self.width() / 2
        cy = self.height() / 2
        radius = min(cx, cy) - 4
        
        pen = QPen()
        pen.setWidth(4)
        pen.setCapStyle(Qt.RoundCap)
        
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(102, 126, 234))
        gradient.setColorAt(1, QColor(118, 75, 162))
        pen.setBrush(QBrush(gradient))
        
        painter.setPen(pen)
        painter.translate(cx, cy)
        painter.rotate(self._angle)
        painter.translate(-cx, -cy)
        
        rect = QRect(int(cx - radius), int(cy - radius), 
                     int(radius * 2), int(radius * 2))
        painter.drawArc(rect, 0, 270 * 16)


class ModernLineEdit(QWidget):
    
    def __init__(self, placeholder: str = "", parent=None):
        from PyQt6.QtWidgets import QLineEdit
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setStyleSheet("""
            QLineEdit {
                background: rgba(15, 15, 26, 0.8);
                border: 2px solid rgba(102, 126, 234, 0.3);
                border-radius: 10px;
                padding: 14px 18px;
                color:
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(102, 126, 234, 0.8);
                background: rgba(15, 15, 26, 0.95);
            }
            QLineEdit:hover {
                border: 2px solid rgba(102, 126, 234, 0.5);
            }
        """)
        layout.addWidget(self.line_edit)
    
    def text(self):
        return self.line_edit.text()
    
    def setText(self, text):
        self.line_edit.setText(text)
    
    def setPlaceholderText(self, text):
        self.line_edit.setPlaceholderText(text)
    
    def setEchoMode(self, mode):
        self.line_edit.setEchoMode(mode)


__all__ = [
    'GlassCard',
    'ModernButton', 
    'AnimatedProgressBar',
    'PillBadge',
    'ModernTableWidget',
    'RiskTableWidgetItem',
    'StatCard',
    'ToastNotification',
    'LoadingSpinner',
    'ModernLineEdit'
]
