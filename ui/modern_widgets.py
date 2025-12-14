"""
Modern Widgets untuk FilePermissionChecker
Custom widgets dengan glassmorphism dan animasi
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QProgressBar, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy, QHeaderView
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, pyqtProperty,
    QTimer, QSize, QPoint, QRect
)
from PyQt5.QtGui import (
    QColor, QFont, QPainter, QPainterPath, QBrush,
    QLinearGradient, QPen, QIcon
)


class GlassCard(QFrame):
    """Container dengan glassmorphism effect"""
    
    def __init__(self, parent=None, blur_radius: int = 20):
        super().__init__(parent)
        self.blur_radius = blur_radius
        self.setObjectName("glassCard")
        self._setup_style()
        self._setup_shadow()
    
    def _setup_style(self):
        self.setStyleSheet("""
            QFrame#glassCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.08),
                    stop:1 rgba(255, 255, 255, 0.03));
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 16px;
            }
        """)
    
    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(self.blur_radius)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)


class ModernButton(QPushButton):
    """Gradient button dengan hover animations"""
    
    STYLES = {
        'primary': {
            'gradient': ['#667eea', '#764ba2'],
            'hover': ['#7c8ff5', '#8b5fbf'],
            'pressed': ['#5a6fd6', '#6a4192']
        },
        'success': {
            'gradient': ['#10b981', '#059669'],
            'hover': ['#34d399', '#10b981'],
            'pressed': ['#059669', '#047857']
        },
        'warning': {
            'gradient': ['#f59e0b', '#d97706'],
            'hover': ['#fbbf24', '#f59e0b'],
            'pressed': ['#d97706', '#b45309']
        },
        'danger': {
            'gradient': ['#ef4444', '#dc2626'],
            'hover': ['#f87171', '#ef4444'],
            'pressed': ['#dc2626', '#b91c1c']
        },
        'secondary': {
            'gradient': ['rgba(102, 126, 234, 0.3)', 'rgba(118, 75, 162, 0.3)'],
            'hover': ['rgba(102, 126, 234, 0.5)', 'rgba(118, 75, 162, 0.5)'],
            'pressed': ['rgba(102, 126, 234, 0.6)', 'rgba(118, 75, 162, 0.6)']
        }
    }
    
    def __init__(self, text: str = "", icon: str = None, 
                 style: str = "primary", parent=None):
        super().__init__(text, parent)
        self.button_style = style
        self._apply_style()
        self._setup_animation()
        self._setup_shadow()
        
        if icon:
            self.setIcon(QIcon(icon))
            self.setIconSize(QSize(18, 18))
    
    def _apply_style(self):
        style_config = self.STYLES.get(self.button_style, self.STYLES['primary'])
        grad = style_config['gradient']
        hover = style_config['hover']
        pressed = style_config['pressed']
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {grad[0]}, stop:1 {grad[1]});
                border: none;
                border-radius: 10px;
                padding: 12px 28px;
                color: white;
                font-weight: 600;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {hover[0]}, stop:1 {hover[1]});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {pressed[0]}, stop:1 {pressed[1]});
            }}
            QPushButton:disabled {{
                background: rgba(100, 100, 120, 0.3);
                color: #64748b;
            }}
        """)
    
    def _setup_animation(self):
        self._scale = 1.0
    
    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(102, 126, 234, 100))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def enterEvent(self, event):
        super().enterEvent(event)
        shadow = self.graphicsEffect()
        if shadow:
            shadow.setBlurRadius(25)
            shadow.setOffset(0, 6)
    
    def leaveEvent(self, event):
        super().leaveEvent(event)
        shadow = self.graphicsEffect()
        if shadow:
            shadow.setBlurRadius(15)
            shadow.setOffset(0, 4)


class AnimatedProgressBar(QProgressBar):
    """Progress bar dengan glow effect dan animasi"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(True)
        self.setMinimumHeight(28)
        self._glow_opacity = 0.5
        self._setup_style()
        
        # Glow animation
        self._glow_timer = QTimer(self)
        self._glow_timer.timeout.connect(self._animate_glow)
        self._glow_direction = 1
    
    def _setup_style(self):
        self.setStyleSheet("""
            QProgressBar {
                background: rgba(15, 15, 26, 0.8);
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 14px;
                text-align: center;
                color: #ffffff;
                font-weight: 600;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #667eea);
                border-radius: 13px;
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
    """Risk level badges dengan pill style"""
    
    RISK_STYLES = {
        'High': {
            'bg_start': 'rgba(239, 68, 68, 0.25)',
            'bg_end': 'rgba(220, 38, 38, 0.25)',
            'border': 'rgba(239, 68, 68, 0.5)',
            'text': '#fca5a5',
            'icon': '🔴'
        },
        'Medium': {
            'bg_start': 'rgba(245, 158, 11, 0.25)',
            'bg_end': 'rgba(217, 119, 6, 0.25)',
            'border': 'rgba(245, 158, 11, 0.5)',
            'text': '#fcd34d',
            'icon': '🟠'
        },
        'Low': {
            'bg_start': 'rgba(16, 185, 129, 0.25)',
            'bg_end': 'rgba(5, 150, 105, 0.25)',
            'border': 'rgba(16, 185, 129, 0.5)',
            'text': '#6ee7b7',
            'icon': '🟢'
        }
    }
    
    def __init__(self, risk_level: str = "Low", show_icon: bool = True, parent=None):
        super().__init__(parent)
        self.risk_level = risk_level
        self.show_icon = show_icon
        self._apply_style()
    
    def _apply_style(self):
        style = self.RISK_STYLES.get(self.risk_level, self.RISK_STYLES['Low'])
        
        text = f"{style['icon']} {self.risk_level}" if self.show_icon else self.risk_level
        self.setText(text)
        
        self.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {style['bg_start']}, stop:1 {style['bg_end']});
                border: 1px solid {style['border']};
                border-radius: 12px;
                padding: 5px 14px;
                color: {style['text']};
                font-weight: 600;
                font-size: 11px;
            }}
        """)
        
        self.setAlignment(Qt.AlignCenter)
    
    def set_risk_level(self, level: str):
        self.risk_level = level
        self._apply_style()


class ModernTableWidget(QTableWidget):
    """Styled table dengan modern aesthetics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
        self._setup_headers()
    
    def _setup_style(self):
        self.setStyleSheet("""
            QTableWidget {
                background: rgba(15, 15, 26, 0.7);
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 12px;
                gridline-color: rgba(102, 126, 234, 0.1);
                selection-background-color: rgba(102, 126, 234, 0.3);
            }
            QTableWidget::item {
                padding: 12px 10px;
                border-bottom: 1px solid rgba(102, 126, 234, 0.08);
            }
            QTableWidget::item:selected {
                background: rgba(102, 126, 234, 0.35);
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background: rgba(102, 126, 234, 0.18);
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(102, 126, 234, 0.25), stop:1 rgba(37, 37, 64, 0.8));
                border: none;
                border-bottom: 2px solid rgba(102, 126, 234, 0.4);
                border-right: 1px solid rgba(102, 126, 234, 0.15);
                padding: 14px 12px;
                color: #ffffff;
                font-weight: 700;
                font-size: 12px;
            }
            QHeaderView::section:hover {
                background: rgba(102, 126, 234, 0.4);
            }
        """)
        
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
    
    def _setup_headers(self):
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setMinimumSectionSize(80)


class RiskTableWidgetItem(QTableWidgetItem):
    """Table widget item dengan warna berdasarkan risk level - ENHANCED"""
    
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
        self.setTextAlignment(Qt.AlignCenter)
        
        font = QFont('Segoe UI', 10)
        font.setBold(True)
        self.setFont(font)


class StatCard(GlassCard):
    """Statistics card untuk dashboard"""
    
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
        
        # Header with icon
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
        
        # Value
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 700;
            color: {self.color};
        """)
        layout.addWidget(self.value_label)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 13px;
            color: #94a3b8;
            font-weight: 500;
        """)
        layout.addWidget(title_label)
        
        self.setMinimumSize(180, 140)
    
    def set_value(self, value: str):
        self.value = value
        self.value_label.setText(value)


class ToastNotification(QFrame):
    """Toast notification widget"""
    
    TYPES = {
        'success': {
            'bg': 'rgba(16, 185, 129, 0.9)',
            'icon': '✅'
        },
        'error': {
            'bg': 'rgba(239, 68, 68, 0.9)',
            'icon': '❌'
        },
        'warning': {
            'bg': 'rgba(245, 158, 11, 0.9)',
            'icon': '⚠️'
        },
        'info': {
            'bg': 'rgba(102, 126, 234, 0.9)',
            'icon': 'ℹ️'
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
                border-radius: 10px;
                padding: 15px 20px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(config['icon'])
        icon_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(icon_label)
        
        # Message
        msg_label = QLabel(self.message)
        msg_label.setStyleSheet("""
            color: white;
            font-weight: 600;
            font-size: 13px;
        """)
        layout.addWidget(msg_label)
        
        self.setFixedHeight(50)
        self.setMinimumWidth(250)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
    
    def _setup_animation(self):
        self._opacity = 1.0
        
        # Auto-hide timer
        self._hide_timer = QTimer(self)
        self._hide_timer.timeout.connect(self._fade_out)
        self._hide_timer.setSingleShot(True)
    
    def show(self):
        super().show()
        self._hide_timer.start(self.duration)
    
    def _fade_out(self):
        self.hide()


class LoadingSpinner(QWidget):
    """Animated loading spinner"""
    
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
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center
        cx = self.width() / 2
        cy = self.height() / 2
        radius = min(cx, cy) - 4
        
        # Draw arc
        pen = QPen()
        pen.setWidth(4)
        pen.setCapStyle(Qt.RoundCap)
        
        # Gradient effect with rotation
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
    """Modern styled line edit with floating label"""
    
    def __init__(self, placeholder: str = "", parent=None):
        from PyQt5.QtWidgets import QLineEdit
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
                color: #e2e8f0;
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


# Export all widgets
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
