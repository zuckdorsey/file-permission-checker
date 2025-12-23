from PyQt6.QtWidgets import QLabel, QProgressBar, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont


class StatusLabel(QLabel):
    
    STATUS_STYLES = {
        'info': {
            'color': '#667eea',
            'bg': 'rgba(102, 126, 234, 0.15)',
            'border': 'rgba(102, 126, 234, 0.3)'
        },
        'success': {
            'color': '#10b981',
            'bg': 'rgba(16, 185, 129, 0.15)',
            'border': 'rgba(16, 185, 129, 0.3)'
        },
        'warning': {
            'color': '#f59e0b',
            'bg': 'rgba(245, 158, 11, 0.15)',
            'border': 'rgba(245, 158, 11, 0.3)'
        },
        'error': {
            'color': '#ef4444',
            'bg': 'rgba(239, 68, 68, 0.15)',
            'border': 'rgba(239, 68, 68, 0.3)'
        },
        'default': {
            'color': '#e2e8f0',
            'bg': 'rgba(100, 100, 120, 0.15)',
            'border': 'rgba(100, 100, 120, 0.3)'
        }
    }
    
    def __init__(self, text="", status="info"):
        super().__init__(text)
        self.status = status
        self._apply_style()
    
    def _apply_style(self):
        style = self.STATUS_STYLES.get(self.status, self.STATUS_STYLES['default'])
        
        self.setStyleSheet(f"""
            QLabel {{
                color: {style['color']};
                background: {style['bg']};
                border: 1px solid {style['border']};
                font-weight: 600;
                padding: 8px 14px;
                border-radius: 8px;
            }}
        """)
    
    def set_status(self, status: str):
        self.status = status
        self._apply_style()


class ColoredProgressBar(QProgressBar):
    
    def __init__(self):
        super().__init__()
        self.setTextVisible(True)
        self.setMinimumHeight(24)
        self._setup_base_style()
    
    def _setup_base_style(self):
        self.setStyleSheet("""
            QProgressBar {
                background: rgba(15, 15, 26, 0.8);
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 12px;
                text-align: center;
                color:
                font-weight: 600;
                font-size: 11px;
            }
        """)
    
    def setValue(self, value):
        super().setValue(value)
        self.update_color()
    
    def update_color(self):
        value = self.value()
        
        if value < 30:
            color_start = "#ef4444"
            color_end = "#dc2626"
        elif value < 70:
            color_start = "#f59e0b"
            color_end = "#d97706"
        else:
            color_start = "#10b981"
            color_end = "#059669"
        
        self.setStyleSheet(f"""
            QProgressBar {{
                background: rgba(15, 15, 26, 0.8);
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 12px;
                text-align: center;
                color:
                font-weight: 600;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color_start}, stop:1 {color_end});
                border-radius: 11px;
            }}
        """)


class RiskTableWidgetItem(QTableWidgetItem):
    """
    Risk level display with Secure status for properly configured files.
    
    Risk Levels:
    - High: Sensitive file with loose permissions (RED)
    - Medium: Moderately sensitive file needing review (YELLOW)
    - Low: Standard file with acceptable permissions (GREEN)
    - Secure: Sensitive file with proper strict permissions (BRIGHT GREEN)
    """
    
    RISK_COLORS = {
        'High': {
            'bg': QColor(239, 68, 68, 50),
            'fg': QColor(252, 165, 165),
            'label': 'High Risk'
        },
        'Medium': {
            'bg': QColor(245, 158, 11, 50),
            'fg': QColor(252, 211, 77),
            'label': 'Medium'
        },
        'Low': {
            'bg': QColor(16, 185, 129, 50),
            'fg': QColor(110, 231, 183),
            'label': 'Low'
        },
        'Secure': {
            'bg': QColor(34, 197, 94, 70),
            'fg': QColor(134, 239, 172),
            'label': 'Secure'
        }
    }
    
    def __init__(self, text: str, risk_level: str = "Low"):
        display_text = self.RISK_COLORS.get(risk_level, self.RISK_COLORS['Low']).get('label', text)
        super().__init__(display_text)
        self.risk_level = risk_level
        self._apply_style()
    
    def _apply_style(self):
        colors = self.RISK_COLORS.get(self.risk_level, self.RISK_COLORS['Low'])
        
        self.setBackground(colors['bg'])
        self.setForeground(colors['fg'])
        self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        font = QFont('Segoe UI', 10)
        font.setBold(True)
        self.setFont(font)
    
    def set_risk_level(self, level: str):
        self.risk_level = level
        label = self.RISK_COLORS.get(level, self.RISK_COLORS['Low']).get('label', level)
        self.setText(label)
        self._apply_style()


class InfoBadge(QLabel):
    
    BADGE_TYPES = {
        'primary': '#667eea',
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        'info': '#0ea5e9'
    }
    
    def __init__(self, text: str = "", badge_type: str = "primary", parent=None):
        super().__init__(text, parent)
        self.badge_type = badge_type
        self._apply_style()
    
    def _apply_style(self):
        color = self.BADGE_TYPES.get(self.badge_type, self.BADGE_TYPES['primary'])
        
        self.setStyleSheet(f"""
            QLabel {{
                background: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2);
                border: 1px solid {color};
                border-radius: 10px;
                padding: 4px 12px;
                color: {color};
                font-weight: 600;
                font-size: 11px;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def set_type(self, badge_type: str):
        self.badge_type = badge_type
        self._apply_style()


class PermissionDisplay(QLabel):
    
    def __init__(self, octal: str = "644", parent=None):
        super().__init__(parent)
        self.octal = octal
        self._update_display()
    
    def _update_display(self):
        symbolic = self._to_symbolic(self.octal)
        colored = self._colorize_symbolic(symbolic)
        
        self.setText(colored)
        self.setStyleSheet("""
            QLabel {
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
                font-size: 13px;
                font-weight: 600;
                background: rgba(15, 15, 26, 0.6);
                padding: 8px 14px;
                border-radius: 8px;
                border: 1px solid rgba(102, 126, 234, 0.3);
            }
        """)
    
    def _to_symbolic(self, octal: str) -> str:
        if len(octal) != 3:
            return "--- --- ---"
        
        symbolic = ""
        for digit in octal:
            num = int(digit)
            symbolic += 'r' if num & 4 else '-'
            symbolic += 'w' if num & 2 else '-'
            symbolic += 'x' if num & 1 else '-'
            symbolic += ' '
        
        return symbolic.strip()
    
    def _colorize_symbolic(self, symbolic: str) -> str:
        colored = ""
        for char in symbolic:
            if char == 'r':
                colored += "<span style='color: #10b981'>r</span>"
            elif char == 'w':
                colored += "<span style='color: #f59e0b'>w</span>"
            elif char == 'x':
                colored += "<span style='color: #ef4444'>x</span>"
            elif char == '-':
                colored += "<span style='color: #64748b'>-</span>"
            else:
                colored += char
        
        return colored
    
    def set_permission(self, octal: str):
        self.octal = octal
        self._update_display()


class FileIcon(QLabel):
    
    ICONS = {
        'directory': '📁',
        'file': '📄',
        'image': '🖼️',
        'audio': '🎵',
        'video': '🎬',
        'code': '💻',
        'archive': '📦',
        'document': '📝',
        'executable': '⚙️',
        'config': '🔧',
        'secret': '🔐'
    }
    
    def __init__(self, file_type: str = "file", parent=None):
        super().__init__(parent)
        self.file_type = file_type
        self._update_icon()
    
    def _update_icon(self):
        icon = self.ICONS.get(self.file_type, self.ICONS['file'])
        self.setText(icon)
        self.setStyleSheet("""
            font-size: 18px;
        """)
    
    def set_type(self, file_type: str):
        self.file_type = file_type
        self._update_icon()
