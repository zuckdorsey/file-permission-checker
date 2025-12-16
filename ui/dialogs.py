"""
Dialog Modern untuk FilePermissionChecker
Antarmuka yang ditingkatkan dengan glassmorphism dan animasi
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QGridLayout, QDialogButtonBox,
    QTextEdit, QComboBox, QRadioButton, QButtonGroup, QFrame,
    QWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont


class ModernDialog(QDialog):
    """Kelas dasar untuk dialog modern"""
    
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self._apply_base_style()
    
    def _apply_base_style(self):
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-radius: 15px;
            }
            QLabel {
                color: #e2e8f0;
            }
            QLineEdit {
                background: rgba(15, 15, 26, 0.8);
                border: 2px solid rgba(102, 126, 234, 0.3);
                border-radius: 8px;
                padding: 12px 16px;
                color: #e2e8f0;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(102, 126, 234, 0.8);
            }
            QCheckBox {
                color: #e2e8f0;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid rgba(102, 126, 234, 0.4);
                background: rgba(15, 15, 26, 0.8);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: 2px solid #667eea;
            }
            QGroupBox {
                background: rgba(37, 37, 64, 0.5);
                border: 1px solid rgba(102, 126, 234, 0.25);
                border-radius: 12px;
                margin-top: 20px;
                padding: 20px 15px 15px 15px;
                font-weight: 600;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                top: 5px;
                padding: 5px 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 0.4), stop:1 rgba(118, 75, 162, 0.4));
                border-radius: 8px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7c8ff5, stop:1 #8b5fbf);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a6fd6, stop:1 #6a4192);
            }
        """)


class PasswordDialog(ModernDialog):
    """Dialog untuk memasukkan password dengan antarmuka modern"""
    
    def __init__(self, parent=None, title="Enter Password"):
        super().__init__(parent, title)
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("🔐 " + self.windowTitle())
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 10px;
        """)
        layout.addWidget(header)
        
        # Password input
        pass_label = QLabel("Password:")
        pass_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(pass_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setMinimumHeight(45)
        layout.addWidget(self.password_input)
        
        # Confirm password
        confirm_label = QLabel("Confirm Password:")
        confirm_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(confirm_label)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Confirm your password")
        self.confirm_input.setMinimumHeight(45)
        layout.addWidget(self.confirm_input)
        
        # Show password checkbox
        self.show_password = QCheckBox("👁️ Show password")
        self.show_password.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password)
        
        layout.addSpacing(10)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100, 100, 120, 0.3);
                color: #e2e8f0;
            }
            QPushButton:hover {
                background: rgba(100, 100, 120, 0.5);
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Confirm")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
    
    def toggle_password_visibility(self, checked):
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.password_input.setEchoMode(mode)
        self.confirm_input.setEchoMode(mode)
    
    def get_password(self):
        return self.password_input.text()
    
    def get_confirm_password(self):
        return self.confirm_input.text()
    
    def passwords_match(self):
        return self.password_input.text() == self.confirm_input.text()


class AdvancedPermissionDialog(ModernDialog):
    """Dialog untuk mengubah hak akses dengan antarmuka modern"""
    
    def __init__(self, parent=None, file_count: int = 1):
        super().__init__(parent, "Advanced Permission Settings")
        self.setMinimumWidth(600)
        self.file_count = file_count
        
        self.permission_history = []
        self.current_history_index = -1
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        header = QLabel(f"🔧 Permission Settings")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
        """)
        header_layout.addWidget(header)
        
        file_count_badge = QLabel(f"📁 {self.file_count} file(s)")
        file_count_badge.setStyleSheet("""
            background: rgba(102, 126, 234, 0.3);
            padding: 6px 14px;
            border-radius: 12px;
            color: #667eea;
            font-weight: 600;
        """)
        header_layout.addWidget(file_count_badge)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Visual Permission Editor
        self.visual_editor_group = QGroupBox("📊 Visual Permission Editor")
        visual_layout = QGridLayout()
        visual_layout.setSpacing(15)
        
        # Headers
        visual_layout.addWidget(QLabel(""), 0, 0)
        
        read_header = QLabel("Read")
        read_header.setStyleSheet("font-weight: 600; color: #10b981;")
        visual_layout.addWidget(read_header, 0, 1, Qt.AlignCenter)
        
        write_header = QLabel("Write")
        write_header.setStyleSheet("font-weight: 600; color: #f59e0b;")
        visual_layout.addWidget(write_header, 0, 2, Qt.AlignCenter)
        
        exec_header = QLabel("Execute")
        exec_header.setStyleSheet("font-weight: 600; color: #ef4444;")
        visual_layout.addWidget(exec_header, 0, 3, Qt.AlignCenter)
        
        # User permissions
        user_label = QLabel("👤 Owner")
        user_label.setStyleSheet("font-weight: 600;")
        visual_layout.addWidget(user_label, 1, 0)
        
        self.user_read = QCheckBox()
        self.user_read.setChecked(True)
        self.user_write = QCheckBox()
        self.user_write.setChecked(True)
        self.user_execute = QCheckBox()
        
        visual_layout.addWidget(self.user_read, 1, 1, Qt.AlignCenter)
        visual_layout.addWidget(self.user_write, 1, 2, Qt.AlignCenter)
        visual_layout.addWidget(self.user_execute, 1, 3, Qt.AlignCenter)
        
        # Group permissions
        group_label = QLabel("👥 Group")
        group_label.setStyleSheet("font-weight: 600;")
        visual_layout.addWidget(group_label, 2, 0)
        
        self.group_read = QCheckBox()
        self.group_read.setChecked(True)
        self.group_write = QCheckBox()
        self.group_execute = QCheckBox()
        
        visual_layout.addWidget(self.group_read, 2, 1, Qt.AlignCenter)
        visual_layout.addWidget(self.group_write, 2, 2, Qt.AlignCenter)
        visual_layout.addWidget(self.group_execute, 2, 3, Qt.AlignCenter)
        
        # Others permissions
        others_label = QLabel("🌐 Others")
        others_label.setStyleSheet("font-weight: 600;")
        visual_layout.addWidget(others_label, 3, 0)
        
        self.others_read = QCheckBox()
        self.others_read.setChecked(True)
        self.others_write = QCheckBox()
        self.others_execute = QCheckBox()
        
        visual_layout.addWidget(self.others_read, 3, 1, Qt.AlignCenter)
        visual_layout.addWidget(self.others_write, 3, 2, Qt.AlignCenter)
        visual_layout.addWidget(self.others_execute, 3, 3, Qt.AlignCenter)
        
        self.visual_editor_group.setLayout(visual_layout)
        layout.addWidget(self.visual_editor_group)
        
        # Connect signals
        for checkbox in [self.user_read, self.user_write, self.user_execute,
                        self.group_read, self.group_write, self.group_execute,
                        self.others_read, self.others_write, self.others_execute]:
            checkbox.stateChanged.connect(self.update_permission_from_visual)
        
        # Octal Input
        octal_group = QGroupBox("🔢 Octal Permission")
        octal_layout = QHBoxLayout()
        
        octal_layout.addWidget(QLabel("Permission:"))
        self.permission_input = QLineEdit("644")
        self.permission_input.setPlaceholderText("e.g., 644, 755, 600")
        self.permission_input.setMaximumWidth(150)
        self.permission_input.textChanged.connect(self.update_visual_from_permission)
        octal_layout.addWidget(self.permission_input)
        
        self.symbolic_label = QLabel("rw-r--r--")
        self.symbolic_label.setStyleSheet("""
            background: rgba(102, 126, 234, 0.2);
            padding: 8px 16px;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
        """)
        octal_layout.addWidget(self.symbolic_label)
        octal_layout.addStretch()
        
        octal_group.setLayout(octal_layout)
        layout.addWidget(octal_group)
        
        # Presets
        presets_group = QGroupBox("⚡ Quick Presets")
        presets_layout = QGridLayout()
        presets_layout.setSpacing(10)
        
        presets = [
            ("644 - Regular Files", "644", "#667eea"),
            ("755 - Executable/Dirs", "755", "#10b981"),
            ("600 - Private Files", "600", "#ef4444"),
            ("640 - Group Readable", "640", "#f59e0b"),
            ("750 - Group Executable", "750", "#8b5cf6"),
            ("777 - Full Access ⚠️", "777", "#ef4444"),
            ("444 - Read Only", "444", "#94a3b8"),
            ("711 - Execute Only", "711", "#06b6d4")
        ]
        
        for i, (label, perm, color) in enumerate(presets):
            btn = QPushButton(label)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2);
                    border: 1px solid {color};
                    color: {color};
                    padding: 10px 15px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.4);
                }}
            """)
            btn.clicked.connect(lambda checked, p=perm: self.set_permission(p))
            presets_layout.addWidget(btn, i // 4, i % 4)
        
        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)
        
        # CIA Options
        cia_group = QGroupBox("🛡️ Security & Backup Options")
        cia_layout = QVBoxLayout()
        cia_layout.setSpacing(12)
        
        self.backup_checkbox = QCheckBox("📁 Create backup before changes")
        self.backup_checkbox.setChecked(True)
        cia_layout.addWidget(self.backup_checkbox)
        
        self.encrypt_checkbox = QCheckBox("🔒 Encrypt files after changes")
        cia_layout.addWidget(self.encrypt_checkbox)
        
        self.verify_checkbox = QCheckBox("✅ Verify integrity with hash")
        self.verify_checkbox.setChecked(True)
        cia_layout.addWidget(self.verify_checkbox)
        
        self.recursive_checkbox = QCheckBox("📂 Apply recursively to subdirectories")
        cia_layout.addWidget(self.recursive_checkbox)
        
        cia_group.setLayout(cia_layout)
        layout.addWidget(cia_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        preview_btn = QPushButton("👁️ Preview")
        preview_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100, 100, 120, 0.3);
                color: #e2e8f0;
            }
            QPushButton:hover {
                background: rgba(100, 100, 120, 0.5);
            }
        """)
        preview_btn.clicked.connect(self.preview)
        btn_layout.addWidget(preview_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100, 100, 120, 0.3);
                color: #e2e8f0;
            }
            QPushButton:hover {
                background: rgba(100, 100, 120, 0.5);
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("✅ Apply")
        apply_btn.clicked.connect(self.accept)
        btn_layout.addWidget(apply_btn)
        
        layout.addLayout(btn_layout)
        
        # Initialize
        self.update_visual_from_permission("644")
    
    def update_permission_from_visual(self):
        """Perbarui izin oktal dari editor visual"""
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
        
        # Block signals to avoid loop
        self.permission_input.blockSignals(True)
        self.permission_input.setText(permission)
        self.permission_input.blockSignals(False)
        
        self.symbolic_label.setText(self.get_symbolic_permission(permission))
        self.add_to_history(permission)
    
    def update_visual_from_permission(self, permission: str):
        """Perbarui editor visual dari izin oktal"""
        if len(permission) != 3 or not permission.isdigit():
            return
        
        try:
            # Block signals
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
        """Atur izin dari preset"""
        self.permission_input.setText(permission)
        self.update_visual_from_permission(permission)
        self.add_to_history(permission)
    
    def add_to_history(self, permission: str):
        """Tambahkan izin ke riwayat"""
        if self.permission_history and self.permission_history[-1] == permission:
            return
        
        self.permission_history = self.permission_history[:self.current_history_index + 1]
        self.permission_history.append(permission)
        self.current_history_index = len(self.permission_history) - 1
    
    def preview(self):
        """Pratinjau perubahan"""
        permission = self.permission_input.text()
        symbolic = self.get_symbolic_permission(permission)
        
        from PyQt5.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Preview")
        msg.setIcon(QMessageBox.Information)
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
        msg.exec_()
    
    def get_symbolic_permission(self, permission: str) -> str:
        """Konversi oktal ke simbolik"""
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
        """Dapatkan semua pengaturan"""
        return {
            'permission': self.permission_input.text(),
            'backup': self.backup_checkbox.isChecked(),
            'encrypt': self.encrypt_checkbox.isChecked(),
            'verify': self.verify_checkbox.isChecked(),
            'recursive': self.recursive_checkbox.isChecked()
        }


class SettingsDialog(ModernDialog):
    """Dialog untuk pengaturan aplikasi"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Settings")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("⚙️ Application Settings")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 10px;
        """)
        layout.addWidget(header)
        
        # Theme settings
        theme_group = QGroupBox("🎨 Theme")
        theme_layout = QVBoxLayout()
        
        self.dark_mode = QCheckBox("🌙 Dark Mode")
        self.dark_mode.setChecked(True)
        theme_layout.addWidget(self.dark_mode)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Scan settings
        scan_group = QGroupBox("🔍 Scan Settings")
        scan_layout = QGridLayout()
        scan_layout.setSpacing(12)
        
        scan_layout.addWidget(QLabel("Max files to scan:"), 0, 0)
        self.max_files = QLineEdit("10000")
        self.max_files.setMinimumHeight(40)
        scan_layout.addWidget(self.max_files, 0, 1)
        
        scan_layout.addWidget(QLabel("Cache duration (seconds):"), 1, 0)
        self.cache_duration = QLineEdit("300")
        self.cache_duration.setMinimumHeight(40)
        scan_layout.addWidget(self.cache_duration, 1, 1)
        
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)
        
        # Security settings
        security_group = QGroupBox("🔒 Security Settings")
        security_layout = QGridLayout()
        security_layout.setSpacing(12)
        
        security_layout.addWidget(QLabel("Session timeout (minutes):"), 0, 0)
        self.session_timeout = QLineEdit("30")
        self.session_timeout.setMinimumHeight(40)
        security_layout.addWidget(self.session_timeout, 0, 1)
        
        security_layout.addWidget(QLabel("Max login attempts:"), 1, 0)
        self.max_attempts = QLineEdit("5")
        self.max_attempts.setMinimumHeight(40)
        security_layout.addWidget(self.max_attempts, 1, 1)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # Backup settings
        backup_group = QGroupBox("💾 Backup Settings")
        backup_layout = QGridLayout()
        backup_layout.setSpacing(12)
        
        backup_layout.addWidget(QLabel("Max backups:"), 0, 0)
        self.max_backups = QLineEdit("50")
        self.max_backups.setMinimumHeight(40)
        backup_layout.addWidget(self.max_backups, 0, 1)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100, 100, 120, 0.3);
                color: #e2e8f0;
            }
            QPushButton:hover {
                background: rgba(100, 100, 120, 0.5);
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Save")
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