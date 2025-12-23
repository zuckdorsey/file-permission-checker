from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QGridLayout, QDialogButtonBox,
    QTextEdit, QComboBox, QRadioButton, QButtonGroup, QFrame,
    QWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont


class ModernDialog(QDialog):
    """Base dialog with minimalist dark theme"""
    
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self._apply_base_style()
    
    def _apply_base_style(self):
        self.setStyleSheet("""
            QDialog {
                background:
                border: 1px solid
                border-radius: 8px;
            }
            QLabel {
                color:
            }
            QLineEdit {
                background:
                border: 1px solid
                border-radius: 6px;
                padding: 10px 14px;
                color:
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid
            }
            QLineEdit:hover {
                border: 1px solid
            }
            QCheckBox {
                color:
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid
                background:
            }
            QCheckBox::indicator:hover {
                border: 1px solid
            }
            QCheckBox::indicator:checked {
                background:
                border: 1px solid
            }
            QGroupBox {
                background:
                border: 1px solid
                border-radius: 6px;
                margin-top: 16px;
                padding: 16px 12px 12px 12px;
                font-weight: 500;
                color:
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                top: 4px;
                padding: 4px 10px;
                background:
                border-radius: 4px;
                color:
                font-size: 12px;
            }
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
            QPushButton:pressed {
                background:
            }
            QPushButton:disabled {
                background:
                color:
            }
        """)


class PasswordDialog(ModernDialog):
    """Minimalist password dialog"""
    
    def __init__(self, parent=None, title="Enter Password"):
        super().__init__(parent, title)
        self.setMinimumWidth(380)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        header = QLabel(self.windowTitle())
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color:
            margin-bottom: 8px;
        """)
        layout.addWidget(header)
        
        pass_label = QLabel("Password")
        pass_label.setStyleSheet("font-weight: 500; color: #a3a3a3; font-size: 12px;")
        layout.addWidget(pass_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setMinimumHeight(40)
        layout.addWidget(self.password_input)
        
        confirm_label = QLabel("Confirm Password")
        confirm_label.setStyleSheet("font-weight: 500; color: #a3a3a3; font-size: 12px;")
        layout.addWidget(confirm_label)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirm your password")
        self.confirm_input.setMinimumHeight(40)
        layout.addWidget(self.confirm_input)
        
        self.show_password = QCheckBox("Show password")
        self.show_password.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password)
        
        layout.addSpacing(8)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background:
                border: 1px solid
                color:
            }
            QPushButton:hover {
                background:
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Confirm")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
    
    def toggle_password_visibility(self, checked):
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.password_input.setEchoMode(mode)
        self.confirm_input.setEchoMode(mode)
    
    def get_password(self):
        return self.password_input.text()
    
    def get_confirm_password(self):
        return self.confirm_input.text()
    
    def passwords_match(self):
        return self.password_input.text() == self.confirm_input.text()


class AdvancedPermissionDialog(ModernDialog):
    """Minimalist advanced permission dialog"""
    
    def __init__(self, parent=None, file_count: int = 1):
        super().__init__(parent, "Permission Settings")
        self.setMinimumWidth(560)
        self.file_count = file_count
        
        self.permission_history = []
        self.current_history_index = -1
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        header_layout = QHBoxLayout()
        
        header = QLabel("Permission Settings")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color:
        """)
        header_layout.addWidget(header)
        
        file_count_badge = QLabel(f"{self.file_count} file(s)")
        file_count_badge.setStyleSheet("""
            background:
            padding: 4px 12px;
            border-radius: 4px;
            color:
            font-weight: 500;
            font-size: 12px;
        """)
        header_layout.addWidget(file_count_badge)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        self.visual_editor_group = QGroupBox("Visual Editor")
        visual_layout = QGridLayout()
        visual_layout.setSpacing(12)
        
        visual_layout.addWidget(QLabel(""), 0, 0)
        
        read_header = QLabel("Read")
        read_header.setStyleSheet("font-weight: 500; color: #4ade80;")
        visual_layout.addWidget(read_header, 0, 1, Qt.AlignmentFlag.AlignCenter)
        
        write_header = QLabel("Write")
        write_header.setStyleSheet("font-weight: 500; color: #fbbf24;")
        visual_layout.addWidget(write_header, 0, 2, Qt.AlignmentFlag.AlignCenter)
        
        exec_header = QLabel("Execute")
        exec_header.setStyleSheet("font-weight: 500; color: #f87171;")
        visual_layout.addWidget(exec_header, 0, 3, Qt.AlignmentFlag.AlignCenter)
        
        user_label = QLabel("Owner")
        user_label.setStyleSheet("font-weight: 500;")
        visual_layout.addWidget(user_label, 1, 0)
        
        self.user_read = QCheckBox()
        self.user_read.setChecked(True)
        self.user_write = QCheckBox()
        self.user_write.setChecked(True)
        self.user_execute = QCheckBox()
        
        visual_layout.addWidget(self.user_read, 1, 1, Qt.AlignmentFlag.AlignCenter)
        visual_layout.addWidget(self.user_write, 1, 2, Qt.AlignmentFlag.AlignCenter)
        visual_layout.addWidget(self.user_execute, 1, 3, Qt.AlignmentFlag.AlignCenter)
        
        group_label = QLabel("Group")
        group_label.setStyleSheet("font-weight: 500;")
        visual_layout.addWidget(group_label, 2, 0)
        
        self.group_read = QCheckBox()
        self.group_read.setChecked(True)
        self.group_write = QCheckBox()
        self.group_execute = QCheckBox()
        
        visual_layout.addWidget(self.group_read, 2, 1, Qt.AlignmentFlag.AlignCenter)
        visual_layout.addWidget(self.group_write, 2, 2, Qt.AlignmentFlag.AlignCenter)
        visual_layout.addWidget(self.group_execute, 2, 3, Qt.AlignmentFlag.AlignCenter)
        
        others_label = QLabel("Others")
        others_label.setStyleSheet("font-weight: 500;")
        visual_layout.addWidget(others_label, 3, 0)
        
        self.others_read = QCheckBox()
        self.others_read.setChecked(True)
        self.others_write = QCheckBox()
        self.others_execute = QCheckBox()
        
        visual_layout.addWidget(self.others_read, 3, 1, Qt.AlignmentFlag.AlignCenter)
        visual_layout.addWidget(self.others_write, 3, 2, Qt.AlignmentFlag.AlignCenter)
        visual_layout.addWidget(self.others_execute, 3, 3, Qt.AlignmentFlag.AlignCenter)
        
        self.visual_editor_group.setLayout(visual_layout)
        layout.addWidget(self.visual_editor_group)
        
        for checkbox in [self.user_read, self.user_write, self.user_execute,
                        self.group_read, self.group_write, self.group_execute,
                        self.others_read, self.others_write, self.others_execute]:
            checkbox.stateChanged.connect(self.update_permission_from_visual)
        
        octal_group = QGroupBox("Octal Permission")
        octal_layout = QHBoxLayout()
        
        octal_layout.addWidget(QLabel("Permission:"))
        self.permission_input = QLineEdit("644")
        self.permission_input.setPlaceholderText("e.g., 644, 755, 600")
        self.permission_input.setMaximumWidth(120)
        self.permission_input.textChanged.connect(self.update_visual_from_permission)
        octal_layout.addWidget(self.permission_input)
        
        self.symbolic_label = QLabel("rw-r--r--")
        self.symbolic_label.setStyleSheet("""
            background:
            padding: 6px 12px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 500;
            color:
        """)
        octal_layout.addWidget(self.symbolic_label)
        octal_layout.addStretch()
        
        octal_group.setLayout(octal_layout)
        layout.addWidget(octal_group)
        
        presets_group = QGroupBox("Quick Presets")
        presets_layout = QGridLayout()
        presets_layout.setSpacing(8)
        
        presets = [
            ("644 - Regular", "644"),
            ("755 - Executable", "755"),
            ("600 - Private", "600"),
            ("640 - Group Read", "640"),
            ("750 - Group Exec", "750"),
            ("777 - Full Access", "777"),
            ("444 - Read Only", "444"),
            ("711 - Exec Only", "711")
        ]
        
        for i, (label, perm) in enumerate(presets):
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton {
                    background:
                    border: 1px solid
                    color:
                    padding: 8px 12px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background:
                    color:
                }
            """)
            btn.clicked.connect(lambda checked, p=perm: self.set_permission(p))
            presets_layout.addWidget(btn, i // 4, i % 4)
        
        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)
        
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        options_layout.setSpacing(8)
        
        self.backup_checkbox = QCheckBox("Create backup before changes")
        self.backup_checkbox.setChecked(True)
        options_layout.addWidget(self.backup_checkbox)
        
        self.encrypt_checkbox = QCheckBox("Encrypt files after changes")
        options_layout.addWidget(self.encrypt_checkbox)
        
        self.verify_checkbox = QCheckBox("Verify integrity with hash")
        self.verify_checkbox.setChecked(True)
        options_layout.addWidget(self.verify_checkbox)
        
        self.recursive_checkbox = QCheckBox("Apply recursively to subdirectories")
        options_layout.addWidget(self.recursive_checkbox)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        btn_layout = QHBoxLayout()
        
        preview_btn = QPushButton("Preview")
        preview_btn.setStyleSheet("""
            QPushButton {
                background:
                border: 1px solid
                color:
            }
            QPushButton:hover {
                background:
            }
        """)
        preview_btn.clicked.connect(self.preview)
        btn_layout.addWidget(preview_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background:
                border: 1px solid
                color:
            }
            QPushButton:hover {
                background:
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.accept)
        btn_layout.addWidget(apply_btn)
        
        layout.addLayout(btn_layout)
        
        self.update_visual_from_permission("644")
    
    def update_permission_from_visual(self):
        user = (4 if self.user_read.isChecked() else 0) + \
               (2 if self.user_write.isChecked() else 0) + \
               (1 if self.user_execute.isChecked() else 0)
        
        group = (4 if self.group_read.isChecked() else 0) + \
                (2 if self.group_write.isChecked() else 0) + \
                (1 if self.group_execute.isChecked() else 0)
        
        others = (4 if self.others_read.isChecked() else 0) + \
                 (2 if self.others_write.isChecked() else 0) + \
                 (1 if self.others_execute.isChecked() else 0)
        
        permission = f"{user}{group}{others}"
        
        self.permission_input.blockSignals(True)
        self.permission_input.setText(permission)
        self.permission_input.blockSignals(False)
        
        self.symbolic_label.setText(self.get_symbolic_permission(permission))
        self.add_to_history(permission)
    
    def update_visual_from_permission(self, permission: str):
        if len(permission) != 3 or not permission.isdigit():
            return
        
        try:
            for checkbox in [self.user_read, self.user_write, self.user_execute,
                           self.group_read, self.group_write, self.group_execute,
                           self.others_read, self.others_write, self.others_execute]:
                checkbox.blockSignals(True)
            
            user = int(permission[0])
            group = int(permission[1])
            others = int(permission[2])
            
            self.user_read.setChecked(bool(user & 4))
            self.user_write.setChecked(bool(user & 2))
            self.user_execute.setChecked(bool(user & 1))
            
            self.group_read.setChecked(bool(group & 4))
            self.group_write.setChecked(bool(group & 2))
            self.group_execute.setChecked(bool(group & 1))
            
            self.others_read.setChecked(bool(others & 4))
            self.others_write.setChecked(bool(others & 2))
            self.others_execute.setChecked(bool(others & 1))
            
            self.symbolic_label.setText(self.get_symbolic_permission(permission))
            
        finally:
            for checkbox in [self.user_read, self.user_write, self.user_execute,
                           self.group_read, self.group_write, self.group_execute,
                           self.others_read, self.others_write, self.others_execute]:
                checkbox.blockSignals(False)
    
    def set_permission(self, permission: str):
        self.permission_input.setText(permission)
        self.update_visual_from_permission(permission)
        self.add_to_history(permission)
    
    def add_to_history(self, permission: str):
        if self.permission_history and self.permission_history[-1] == permission:
            return
        
        self.permission_history = self.permission_history[:self.current_history_index + 1]
        self.permission_history.append(permission)
        self.current_history_index = len(self.permission_history) - 1
    
    def preview(self):
        permission = self.permission_input.text()
        symbolic = self.get_symbolic_permission(permission)
        
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Preview")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(f"""
📋 Operation Preview

🔢 Permission: {permission} ({symbolic})
📁 Files: {self.file_count} file(s)

⚙️ Options:
• Backup: {'✅ Yes' if self.backup_checkbox.isChecked() else '❌ No'}
• Encrypt: {'✅ Yes' if self.encrypt_checkbox.isChecked() else '❌ No'}
• Verify: {'✅ Yes' if self.verify_checkbox.isChecked() else '❌ No'}
• Recursive: {'✅ Yes' if self.recursive_checkbox.isChecked() else '❌ No'}

⚠️ Note: Changes cannot be undone automatically.
        """)
        msg.exec()
    
    def get_symbolic_permission(self, permission: str) -> str:
        if len(permission) != 3:
            return "Invalid"
        
        symbolic = ""
        for digit in permission:
            num = int(digit)
            symbolic += 'r' if num & 4 else '-'
            symbolic += 'w' if num & 2 else '-'
            symbolic += 'x' if num & 1 else '-'
        
        return symbolic
    
    def get_settings(self) -> dict:
        return {
            'permission': self.permission_input.text(),
            'backup': self.backup_checkbox.isChecked(),
            'encrypt': self.encrypt_checkbox.isChecked(),
            'verify': self.verify_checkbox.isChecked(),
            'recursive': self.recursive_checkbox.isChecked()
        }


class SettingsDialog(ModernDialog):
    """Minimalist settings dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Settings")
        self.setMinimumWidth(450)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        header = QLabel("Settings")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color:
            margin-bottom: 8px;
        """)
        layout.addWidget(header)
        
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        
        self.dark_mode = QCheckBox("Dark Mode")
        self.dark_mode.setChecked(True)
        theme_layout.addWidget(self.dark_mode)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        scan_group = QGroupBox("Scan")
        scan_layout = QGridLayout()
        scan_layout.setSpacing(10)
        
        scan_layout.addWidget(QLabel("Max files to scan:"), 0, 0)
        self.max_files = QLineEdit("10000")
        self.max_files.setMinimumHeight(36)
        scan_layout.addWidget(self.max_files, 0, 1)
        
        scan_layout.addWidget(QLabel("Cache duration (sec):"), 1, 0)
        self.cache_duration = QLineEdit("300")
        self.cache_duration.setMinimumHeight(36)
        scan_layout.addWidget(self.cache_duration, 1, 1)
        
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)
        
        security_group = QGroupBox("Security")
        security_layout = QGridLayout()
        security_layout.setSpacing(10)
        
        security_layout.addWidget(QLabel("Session timeout (min):"), 0, 0)
        self.session_timeout = QLineEdit("30")
        self.session_timeout.setMinimumHeight(36)
        security_layout.addWidget(self.session_timeout, 0, 1)
        
        security_layout.addWidget(QLabel("Max login attempts:"), 1, 0)
        self.max_attempts = QLineEdit("5")
        self.max_attempts.setMinimumHeight(36)
        security_layout.addWidget(self.max_attempts, 1, 1)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        backup_group = QGroupBox("Backup")
        backup_layout = QGridLayout()
        backup_layout.setSpacing(10)
        
        backup_layout.addWidget(QLabel("Max backups:"), 0, 0)
        self.max_backups = QLineEdit("50")
        self.max_backups.setMinimumHeight(36)
        backup_layout.addWidget(self.max_backups, 0, 1)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background:
                border: 1px solid
                color:
            }
            QPushButton:hover {
                background:
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def get_settings(self):
        return {
            'dark_mode': self.dark_mode.isChecked(),
            'max_files': int(self.max_files.text() or 10000),
            'cache_duration': int(self.cache_duration.text() or 300),
            'session_timeout': int(self.session_timeout.text() or 30),
            'max_attempts': int(self.max_attempts.text() or 5),
            'max_backups': int(self.max_backups.text() or 50)
        }
    
    def set_settings(self, settings):
        self.dark_mode.setChecked(settings.get('dark_mode', True))
        self.max_files.setText(str(settings.get('max_files', 10000)))
        self.cache_duration.setText(str(settings.get('cache_duration', 300)))
        self.session_timeout.setText(str(settings.get('session_timeout', 30)))
        self.max_attempts.setText(str(settings.get('max_attempts', 5)))
        self.max_backups.setText(str(settings.get('max_backups', 50)))


class ConfirmationDialog(ModernDialog):
    """
    Confirmation dialog for high-risk actions.
    
    Used for:
    - Permanent file deletion after encryption
    - Mass permission changes
    - Clearing quarantine folder
    - Deleting backups
    """
    
    SEVERITY_STYLES = {
        'warning': {
            'icon': '!',
            'color': '#f59e0b',
            'bg': 'rgba(245, 158, 11, 0.15)'
        },
        'danger': {
            'icon': '✕',
            'color': '#ef4444',
            'bg': 'rgba(239, 68, 68, 0.15)'
        },
        'info': {
            'icon': 'i',
            'color': '#3b82f6',
            'bg': 'rgba(59, 130, 246, 0.15)'
        }
    }
    
    def __init__(self, parent=None, title="Confirm Action", 
                 message="Are you sure?", details="", 
                 severity="warning", confirm_text="Confirm"):
        super().__init__(parent, title)
        self.message = message
        self.details = details
        self.severity = severity
        self.confirm_text = confirm_text
        self.setMinimumWidth(420)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        style = self.SEVERITY_STYLES.get(self.severity, self.SEVERITY_STYLES['warning'])
        
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(style['icon'])
        icon_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {style['color']};
            background: {style['bg']};
            border-radius: 20px;
            min-width: 40px;
            max-width: 40px;
            min-height: 40px;
            max-height: 40px;
            qproperty-alignment: AlignCenter;
        """)
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(self.windowTitle())
        title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {style['color']};
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        msg_label = QLabel(self.message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("""
            color:
            font-size: 14px;
            line-height: 1.5;
        """)
        layout.addWidget(msg_label)
        
        if self.details:
            details_label = QLabel(self.details)
            details_label.setWordWrap(True)
            details_label.setStyleSheet(f"""
                color:
                font-size: 12px;
                background: {style['bg']};
                border: 1px solid {style['color']}40;
                border-radius: 6px;
                padding: 12px;
            """)
            layout.addWidget(details_label)
        
        if self.severity == 'danger':
            self.confirm_checkbox = QCheckBox("I understand this action cannot be undone")
            self.confirm_checkbox.setStyleSheet(f"color: {style['color']};")
            layout.addWidget(self.confirm_checkbox)
        else:
            self.confirm_checkbox = None
        
        layout.addSpacing(8)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background:
                border: 1px solid
                color:
                min-width: 80px;
            }
            QPushButton:hover {
                background:
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        confirm_btn = QPushButton(self.confirm_text)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background: {style['color']};
                border: none;
                color:
                font-weight: 600;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background: {style['color']}dd;
            }}
            QPushButton:disabled {{
                background:
                color:
            }}
        """)
        confirm_btn.clicked.connect(self._handle_confirm)
        self.confirm_btn = confirm_btn
        
        if self.confirm_checkbox:
            confirm_btn.setEnabled(False)
            self.confirm_checkbox.toggled.connect(confirm_btn.setEnabled)
        
        btn_layout.addWidget(confirm_btn)
        layout.addLayout(btn_layout)
    
    def _handle_confirm(self):
        if self.confirm_checkbox and not self.confirm_checkbox.isChecked():
            return
        self.accept()
    
    @staticmethod
    def confirm_deletion(parent, file_count: int = 1):
        """Show confirmation for permanent file deletion."""
        dialog = ConfirmationDialog(
            parent=parent,
            title="Permanent Deletion",
            message=f"Are you sure you want to permanently delete {file_count} file(s)?",
            details="This action cannot be undone. The files will be removed from the quarantine folder permanently.",
            severity="danger",
            confirm_text="Delete Permanently"
        )
        return dialog.exec() == QDialog.DialogCode.Accepted
    
    @staticmethod
    def confirm_mass_permission_change(parent, file_count: int, new_permission: str):
        """Show confirmation for mass permission changes."""
        dialog = ConfirmationDialog(
            parent=parent,
            title="Mass Permission Change",
            message=f"You are about to change permissions on {file_count} file(s) to {new_permission}.",
            details="Make sure you have a backup before proceeding. Some system files may become inaccessible.",
            severity="warning",
            confirm_text="Apply Changes"
        )
        return dialog.exec() == QDialog.DialogCode.Accepted
    
    @staticmethod
    def confirm_clear_quarantine(parent, file_count: int):
        """Show confirmation for clearing quarantine."""
        dialog = ConfirmationDialog(
            parent=parent,
            title="Clear Quarantine",
            message=f"Delete all {file_count} files from quarantine?",
            details="These are original files that were encrypted. Only delete if you have verified the encrypted versions work correctly.",
            severity="danger",
            confirm_text="Clear Quarantine"
        )
        return dialog.exec() == QDialog.DialogCode.Accepted
