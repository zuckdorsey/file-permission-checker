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

import sys
import os
import json
import csv
import time
import hashlib
from datetime import datetime, date
from typing import List, Dict
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QHeaderView, QProgressBar,
    QStatusBar, QComboBox, QCheckBox, QGroupBox,
    QAbstractItemView, QShortcut, QGridLayout, QFrame, QApplication,
    QTabWidget, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QFont, QKeySequence, QDragEnterEvent, QDropEvent, QIcon

from core.scanner import ScanThread
from core.permission_fixer import PermissionFixer
from core.integrity import IntegrityManager
from core.database import init_database, log_scan
from core.encryption_manager import EncryptionWorker
from core.backup import BackupManager
from core.security import SecurityManager

from ui.modern_widgets import (
    GlassCard, ModernButton, AnimatedProgressBar,
    ModernTableWidget, RiskTableWidgetItem, ToastNotification,
    PillBadge
)
from ui.dialogs import AdvancedPermissionDialog
from utils.constants import CUSTOM_RULES
from utils.helpers import format_size


class FilePermissionChecker(QMainWindow):
    """Jendela utama aplikasi - Fitur Lengkap"""
    
    def __init__(self):
        super().__init__()
        self.all_files = []
        self.scan_cache = {}
        self.dark_mode = True
        
        self.permission_fixer = PermissionFixer()
        self.integrity_manager = IntegrityManager()
        self.backup_manager = BackupManager()
        self.security_manager = SecurityManager()
        
        self.db_conn = init_database()
        
        self.init_ui()
        self.setup_shortcuts()
        self.load_stylesheet()
        self.setAcceptDrops(True)
    
    def load_stylesheet(self):
        """Muat stylesheet modern"""
        try:
            style_path = os.path.join(os.path.dirname(__file__), '..', 'style.qss')
            if os.path.exists(style_path):
                with open(style_path, 'r') as f:
                    self.setStyleSheet(f.read())
            elif os.path.exists('style.qss'):
                with open('style.qss', 'r') as f:
                    self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Failed to load stylesheet: {e}")
    
    def init_ui(self):
        """Inisialisasi UI modern dengan Tab"""
        self.setWindowTitle(" File Permission Checker")
        self.setGeometry(100, 100, 1400, 850)
        self.setMinimumSize(1100, 650)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.init_header()
        main_layout.addWidget(self.header_widget)
        
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        self.init_sidebar()
        content_layout.addWidget(self.sidebar, 0)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid
                border-radius: 6px;
                background:
            }
            QTabBar::tab {
                background: transparent;
                color:
                padding: 10px 20px;
                border: none;
                border-bottom: 2px solid transparent;
                margin-right: 4px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                color:
                border-bottom: 2px solid
            }
            QTabBar::tab:hover:!selected {
                color:
            }
        """)
        
        self.init_scanner_tab()
        self.init_encryption_tab()
        self.init_backup_tab()
        
        content_layout.addWidget(self.tabs, 1)
        main_layout.addWidget(content_widget, 1)
        
        self.init_status_bar()
    
    def init_header(self):
        """Inisialisasi bilah header - minimalist design"""
        self.header_widget = QFrame()
        self.header_widget.setObjectName("headerBar")
        self.header_widget.setStyleSheet("""
            QFrame
                background:
                border-bottom: 1px solid
            }
        """)
        self.header_widget.setFixedHeight(60)
        
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        title_layout = QVBoxLayout()
        title_label = QLabel("File Permission Checker")
        title_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #e5e5e5;")
        subtitle_label = QLabel("Scan • Encrypt • Backup")
        subtitle_label.setStyleSheet("font-size: 11px; color: #525252;")
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.setSpacing(2)
        header_layout.addLayout(title_layout)
        
        header_layout.addStretch()
        
        scan_btn = ModernButton("Analyze Permissions", style="primary")
        scan_btn.setToolTip("Scan folder for permission vulnerabilities (Ctrl+S)")
        scan_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(0) or self.start_scan())
        header_layout.addWidget(scan_btn)
        
        self.fix_risky_btn = ModernButton("Harden Permissions", style="warning")
        self.fix_risky_btn.setToolTip("Apply permission hardening to risky files (Ctrl+F)")
        self.fix_risky_btn.clicked.connect(self.fix_permissions)
        header_layout.addWidget(self.fix_risky_btn)
        
        export_csv_btn = ModernButton("Export Report", style="secondary")
        export_csv_btn.setToolTip("Export scan results as CSV (Ctrl+E)")
        export_csv_btn.clicked.connect(lambda: self.export_results('csv'))
        header_layout.addWidget(export_csv_btn)
    
    def init_sidebar(self):
        """Inisialisasi sidebar dengan statistik"""
        self.sidebar = GlassCard()
        self.sidebar.setFixedWidth(240)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(12)
        
        stats_title = QLabel("Statistics")
        stats_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #e5e5e5; margin-bottom: 8px;")
        sidebar_layout.addWidget(stats_title)
        
        self.stat_total = self._create_stat_item("Total Files", "0", "#a3a3a3")
        sidebar_layout.addWidget(self.stat_total)
        
        self.stat_safe = self._create_stat_item("Low Risk", "0", "#4ade80")
        sidebar_layout.addWidget(self.stat_safe)
        
        self.stat_medium = self._create_stat_item("Medium Risk", "0", "#fbbf24")
        sidebar_layout.addWidget(self.stat_medium)
        
        self.stat_high = self._create_stat_item("High Risk", "0", "#f87171")
        sidebar_layout.addWidget(self.stat_high)
        
        sidebar_layout.addSpacing(12)
        
        self.stat_size = self._create_stat_item("Total Size", "0 B", "#a3a3a3")
        sidebar_layout.addWidget(self.stat_size)
        
        sidebar_layout.addStretch()
        
        version_label = QLabel("v2.0")
        version_label.setStyleSheet("color: #525252; font-size: 11px; text-align: center;")
        version_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(version_label)
    
    def _create_stat_item(self, title: str, value: str, color: str) -> QFrame:
        """Buat widget statistik mini - minimalist design"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background:
                border: 1px solid
                border-radius: 6px;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 11px; color: #737373; font-weight: 500;")
        text_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName(f"value_{title.lower().replace(' ', '_').replace('(', '').replace(')', '')}")
        value_label.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {color};")
        text_layout.addWidget(value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return frame
    
    
    def init_scanner_tab(self):
        """Inisialisasi Tab Pemindai"""
        scan_tab = QWidget()
        scan_layout = QVBoxLayout(scan_tab)
        scan_layout.setContentsMargins(5, 5, 5, 5)
        
        top_card = GlassCard()
        top_layout = QHBoxLayout(top_card)
        top_layout.setContentsMargins(20, 15, 20, 15)
        
        path_label = QLabel("📂 Folder:")
        path_label.setStyleSheet("font-weight: 600; color: #e2e8f0;")
        top_layout.addWidget(path_label)
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Drag folder here or click Browse...")
        self.path_input.setMinimumHeight(42)
        self.path_input.returnPressed.connect(self.start_scan)
        top_layout.addWidget(self.path_input, 1)
        
        browse_btn = ModernButton("Select Folder", style="secondary")
        browse_btn.setToolTip("Browse and select a folder to analyze")
        browse_btn.clicked.connect(self.browse_path)
        top_layout.addWidget(browse_btn)
        
        scan_btn = ModernButton("Analyze Folder", style="primary")
        scan_btn.setToolTip("Scan folder for permission vulnerabilities (Ctrl+S or F5)")
        scan_btn.clicked.connect(self.start_scan)
        top_layout.addWidget(scan_btn)
        
        scan_layout.addWidget(top_card)
        
        self.progress_bar = AnimatedProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(26)
        scan_layout.addWidget(self.progress_bar)
        
        self.file_table = ModernTableWidget()
        self.file_table.setColumnCount(8)
        self.file_table.setHorizontalHeaderLabels([
            "📄 Name", "📁 Path", "🔢 Mode", "🔣 Symbolic", 
            "⚠️ Risk", "🎯 Expected", "📊 Size", "📅 Modified"
        ])
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_table.setSelectionMode(QTableWidget.MultiSelection)
        self.file_table.setSortingEnabled(True)
        self.file_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.file_table.itemSelectionChanged.connect(self.update_selection_count)
        scan_layout.addWidget(self.file_table, 1)
        
        bottom_card = GlassCard()
        bottom_layout = QHBoxLayout(bottom_card)
        bottom_layout.setContentsMargins(20, 12, 20, 12)
        
        filter_label = QLabel("🔍 Filter:")
        filter_label.setStyleSheet("font-weight: 600;")
        bottom_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Files", "🔴 High Risk", "⚠️ Medium Risk", "✅ Low Risk"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        self.filter_combo.setMinimumWidth(140)
        bottom_layout.addWidget(self.filter_combo)
        
        bottom_layout.addSpacing(20)
        
        search_label = QLabel("🔎 Search:")
        search_label.setStyleSheet("font-weight: 600;")
        bottom_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files...")
        self.search_input.textChanged.connect(self.apply_filter)
        self.search_input.setMinimumWidth(200)
        bottom_layout.addWidget(self.search_input)
        
        bottom_layout.addStretch()
        
        self.selected_count_label = QLabel("Selected: 0")
        self.selected_count_label.setStyleSheet("color: #667eea; font-weight: 700; font-size: 13px;")
        bottom_layout.addWidget(self.selected_count_label)
        
        bottom_layout.addSpacing(15)
        
        self.fix_selected_btn = ModernButton("Harden Selected", style="warning")
        self.fix_selected_btn.setToolTip("Apply permission hardening to selected files (Ctrl+F)")
        self.fix_selected_btn.clicked.connect(self.fix_selected_permissions)
        bottom_layout.addWidget(self.fix_selected_btn)
        
        scan_layout.addWidget(bottom_card)
        
        self.tabs.addTab(scan_tab, "🔍 Permission Scanner")
    
    
    def init_encryption_tab(self):
        """Initialize enhanced encryption tab with folder support and password generator."""
        enc_tab = QWidget()
        layout = QVBoxLayout(enc_tab)
        layout.setContentsMargins(5, 5, 5, 5)
        
        ctrl_card = GlassCard()
        ctrl_layout = QVBoxLayout(ctrl_card)
        
        mode_layout = QHBoxLayout()
        self.enc_mode_btn = ModernButton("🔒 Encrypt Mode", style="encrypt")
        self.enc_mode_btn.setToolTip("Encrypt plaintext files to secure ciphertext")
        self.enc_mode_btn.setCheckable(True)
        self.enc_mode_btn.setChecked(True)
        self.enc_mode_btn.clicked.connect(lambda: self.toggle_enc_mode('encrypt'))
        
        self.dec_mode_btn = ModernButton("🔓 Decrypt Mode", style="secondary")
        self.dec_mode_btn.setToolTip("Decrypt .enc ciphertext files to plaintext")
        self.dec_mode_btn.setCheckable(True)
        self.dec_mode_btn.clicked.connect(lambda: self.toggle_enc_mode('decrypt'))
        
        mode_layout.addWidget(self.enc_mode_btn)
        mode_layout.addWidget(self.dec_mode_btn)
        mode_layout.addStretch()
        ctrl_layout.addLayout(mode_layout)
        
        ctrl_layout.addSpacing(10)
        
        pass_group = QFrame()
        pass_group.setStyleSheet("QFrame { background: rgba(30, 30, 40, 0.5); border-radius: 8px; padding: 8px; }")
        pass_group_layout = QVBoxLayout(pass_group)
        pass_group_layout.setSpacing(8)
        
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Password:")
        pass_label.setStyleSheet("font-weight: 600; color: #e5e5e5;")
        
        self.enc_pass_input = QLineEdit()
        self.enc_pass_input.setEchoMode(QLineEdit.Password)
        self.enc_pass_input.setPlaceholderText("Enter secure password...")
        self.enc_pass_input.textChanged.connect(self._update_password_strength)
        
        self.show_pass_btn = ModernButton("Show", style="secondary")
        self.show_pass_btn.setFixedWidth(60)
        self.show_pass_btn.setCheckable(True)
        self.show_pass_btn.clicked.connect(self._toggle_password_visibility)
        
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.enc_pass_input, 1)
        pass_layout.addWidget(self.show_pass_btn)
        pass_group_layout.addLayout(pass_layout)
        
        self.pass_tools_widget = QWidget()
        tools_layout = QHBoxLayout(self.pass_tools_widget)
        tools_layout.setContentsMargins(0, 0, 0, 0)
        
        generate_btn = ModernButton("Generate Secure Password", style="success")
        generate_btn.setToolTip("Generate a cryptographically secure random password")
        generate_btn.clicked.connect(self._generate_password)
        
        copy_btn = ModernButton("Copy to Clipboard", style="secondary")
        copy_btn.setToolTip("Copy password to clipboard")
        copy_btn.clicked.connect(self._copy_password)
        
        tools_layout.addWidget(generate_btn)
        tools_layout.addWidget(copy_btn)
        tools_layout.addStretch()
        
        self.pass_strength_label = QLabel("Strength: --")
        self.pass_strength_label.setStyleSheet("color: #a3a3a3; font-size: 12px;")
        tools_layout.addWidget(self.pass_strength_label)
        
        pass_group_layout.addWidget(self.pass_tools_widget)
        ctrl_layout.addWidget(pass_group)
        
        layout.addWidget(ctrl_card)
        
        list_card = GlassCard()
        list_layout = QVBoxLayout(list_card)
        list_label = QLabel("Files & Folders to Process:")
        list_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #e5e5e5;")
        list_layout.addWidget(list_label)
        
        self.enc_file_list = QListWidget()
        self.enc_file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.enc_file_list.itemSelectionChanged.connect(self._update_enc_file_count)
        list_layout.addWidget(self.enc_file_list)
        
        action_layout = QHBoxLayout()
        
        add_file_btn = ModernButton("Add Files", style="secondary")
        add_file_btn.setToolTip("Select individual files to add")
        add_file_btn.clicked.connect(self.enc_add_files)
        
        add_folder_btn = ModernButton("Add Folder", style="secondary")
        add_folder_btn.setToolTip("Add all files from a folder recursively")
        add_folder_btn.clicked.connect(self.enc_add_folder)
        
        remove_btn = ModernButton("Remove Selected", style="secondary")
        remove_btn.setToolTip("Remove selected items from queue")
        remove_btn.clicked.connect(self.enc_remove_files)
        
        clear_btn = ModernButton("Clear All", style="danger")
        clear_btn.setToolTip("Clear entire file queue")
        clear_btn.clicked.connect(lambda: self.enc_file_list.clear() or self._update_enc_file_count())
        
        self.enc_process_btn = ModernButton("🔒 Encrypt Files", style="encrypt")
        self.enc_process_btn.setToolTip("Begin encryption process")
        self.enc_process_btn.clicked.connect(self.enc_process)
        
        action_layout.addWidget(add_file_btn)
        action_layout.addWidget(add_folder_btn)
        action_layout.addWidget(remove_btn)
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.enc_process_btn)
        
        list_layout.addLayout(action_layout)
        layout.addWidget(list_card, 1)
        
        self.enc_progress = AnimatedProgressBar()
        self.enc_progress.setVisible(False)
        layout.addWidget(self.enc_progress)
        
        self.tabs.addTab(enc_tab, "Encryption")
    
    def toggle_enc_mode(self, mode):
        """Toggle encryption mode with distinct visual styles."""
        self.enc_mode_btn.setChecked(mode == 'encrypt')
        self.dec_mode_btn.setChecked(mode == 'decrypt')
        
        self.enc_mode_btn.update_style('encrypt' if mode == 'encrypt' else 'secondary')
        self.dec_mode_btn.update_style('decrypt' if mode == 'decrypt' else 'secondary')
        
        self.enc_process_btn.update_style('encrypt' if mode == 'encrypt' else 'decrypt')
        
        self.pass_tools_widget.setVisible(mode == 'encrypt')
        
        file_count = self.enc_file_list.count()
        if mode == 'encrypt':
            if file_count > 0:
                self.enc_process_btn.setText(f"🔒 Encrypt {file_count} Files")
            else:
                self.enc_process_btn.setText("🔒 Encrypt Files")
            self.enc_process_btn.setToolTip("Encrypt plaintext files to secure ciphertext format")
        else:
            if file_count > 0:
                self.enc_process_btn.setText(f"🔓 Decrypt {file_count} Files")
            else:
                self.enc_process_btn.setText("🔓 Decrypt Files")
            self.enc_process_btn.setToolTip("Decrypt .enc ciphertext files to original plaintext")
    
    def enc_add_files(self):
        """Add individual files to the encryption queue."""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Process")
        for f in files:
            if not self.enc_file_list.findItems(f, Qt.MatchExactly):
                self.enc_file_list.addItem(f)
        self._update_enc_file_count()
            
    def enc_remove_files(self):
        """Remove selected files from the queue."""
        for item in self.enc_file_list.selectedItems():
            self.enc_file_list.takeItem(self.enc_file_list.row(item))
        self._update_enc_file_count()
    
    def enc_add_folder(self):
        """Add all files from a folder recursively."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Process")
        if not folder:
            return
        
        file_count = 0
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if not file.startswith('.'):
                    filepath = os.path.join(root, file)
                    if not self.enc_file_list.findItems(filepath, Qt.MatchExactly):
                        self.enc_file_list.addItem(filepath)
                        file_count += 1
        
        self._update_enc_file_count()
        self.show_toast(f"Added {file_count} files from folder", "success")
    
    def _update_enc_file_count(self):
        """Update file count and process button label with mode indicator."""
        file_count = self.enc_file_list.count()
        mode = 'encrypt' if self.enc_mode_btn.isChecked() else 'decrypt'
        
        if mode == 'encrypt':
            if file_count > 0:
                self.enc_process_btn.setText(f"🔒 Encrypt {file_count} Files")
            else:
                self.enc_process_btn.setText("🔒 Encrypt Files")
        else:
            if file_count > 0:
                self.enc_process_btn.setText(f"🔓 Decrypt {file_count} Files")
            else:
                self.enc_process_btn.setText("🔓 Decrypt Files")
    
    def _toggle_password_visibility(self):
        """Toggle password field visibility."""
        if self.show_pass_btn.isChecked():
            self.enc_pass_input.setEchoMode(QLineEdit.Normal)
            self.show_pass_btn.setText("Hide")
        else:
            self.enc_pass_input.setEchoMode(QLineEdit.Password)
            self.show_pass_btn.setText("Show")
    
    def _generate_password(self):
        """Generate a secure random password and show it."""
        password = self.security_manager.generate_secure_password(20)
        self.enc_pass_input.setText(password)
        
        self.enc_pass_input.setEchoMode(QLineEdit.Normal)
        self.show_pass_btn.setChecked(True)
        self.show_pass_btn.setText("Hide")
        
        self._update_password_strength()
        self.show_toast("Secure password generated - copy it before proceeding!", "info")
    
    def _copy_password(self):
        """Copy password to clipboard."""
        from PyQt5.QtWidgets import QApplication
        
        password = self.enc_pass_input.text()
        if not password:
            self.show_toast("No password to copy", "warning")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(password)
        self.show_toast("Password copied to clipboard", "success")
    
    def _update_password_strength(self):
        """Update password strength indicator."""
        password = self.enc_pass_input.text()
        if not password:
            self.pass_strength_label.setText("Strength: --")
            self.pass_strength_label.setStyleSheet("color: #a3a3a3; font-size: 12px;")
            return
        
        result = self.security_manager.check_password_strength(password)
        strength = result['strength']
        score = result['score']
        
        colors = {
            0: "#ef4444", 1: "#ef4444", 2: "#f59e0b",
            3: "#eab308", 4: "#22c55e", 5: "#10b981", 6: "#059669"
        }
        color = colors.get(score, "#a3a3a3")
        
        self.pass_strength_label.setText(f"Strength: {strength}")
        self.pass_strength_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")
            
    def enc_process(self):
        password = self.enc_pass_input.text()
        if not password:
            self.show_toast("Password required", "error")
            return
            
        files = [self.enc_file_list.item(i).text() for i in range(self.enc_file_list.count())]
        if not files:
            self.show_toast("No files selected", "warning")
            return
            
        mode = 'encrypt' if self.enc_mode_btn.isChecked() else 'decrypt'
        
        self.enc_worker = EncryptionWorker(mode, files, password)
        self.enc_worker.progress.connect(lambda v, m: self.enc_progress.setValue(v))
        self.enc_worker.finished.connect(lambda: self.show_toast("Processing complete!", "success"))
        self.enc_worker.error.connect(lambda e: self.show_toast(str(e), "error"))
        
        self.enc_progress.setVisible(True)
        self.enc_progress.setValue(0)
        
        thread = QThread(self)
        self.enc_worker.moveToThread(thread)
        thread.started.connect(self.enc_worker.run)
        self.enc_worker.finished.connect(thread.quit)
        self.enc_worker.finished.connect(lambda: self.enc_progress.setVisible(False))
        thread.start()
        
    
    def init_backup_tab(self):
        """Inisialisasi Tab Pencadangan"""
        backup_tab = QWidget()
        layout = QVBoxLayout(backup_tab)
        layout.setContentsMargins(5, 5, 5, 5)
        
        new_card = GlassCard()
        new_layout = QVBoxLayout(new_card)
        new_label = QLabel("📦 Create New Backup")
        new_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        new_layout.addWidget(new_label)
        
        form_layout = QHBoxLayout()
        self.backup_path_input = QLineEdit()
        self.backup_path_input.setPlaceholderText("Select folder or files to backup...")
        form_layout.addWidget(self.backup_path_input, 1)
        
        browse_btn = ModernButton("Browse Folder", style="secondary")
        browse_btn.clicked.connect(self.backup_browse)
        form_layout.addWidget(browse_btn)
        
        create_btn = ModernButton("💾 Create Backup", style="primary")
        create_btn.clicked.connect(self.create_backup)
        form_layout.addWidget(create_btn)
        
        new_layout.addLayout(form_layout)
        layout.addWidget(new_card)
        
        hist_card = GlassCard()
        hist_layout = QVBoxLayout(hist_card)
        hist_label = QLabel("🕰️ Backup History")
        hist_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        hist_layout.addWidget(hist_label)
        
        self.backup_table = ModernTableWidget()
        self.backup_table.setColumnCount(4)
        self.backup_table.setHorizontalHeaderLabels(["Name", "Date", "Size", "Files"])
        self.backup_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.backup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        hist_layout.addWidget(self.backup_table)
        
        actions = QHBoxLayout()
        refresh_btn = ModernButton("🔄 Refresh List", style="secondary")
        refresh_btn.clicked.connect(self.refresh_backups)
        actions.addWidget(refresh_btn)
        
        restore_btn = ModernButton("📥 Restore Selected", style="warning")
        restore_btn.clicked.connect(self.restore_backup)
        actions.addWidget(restore_btn)
        
        hist_layout.addLayout(actions)
        layout.addWidget(hist_card, 1)
        
        self.tabs.addTab(backup_tab, "💾 Backups")
        
        self.refresh_backups()
    
    def backup_browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder to Backup")
        if path:
            self.backup_path_input.setText(path)
            
    def create_backup(self):
        path = self.backup_path_input.text()
        if not path or not os.path.exists(path):
            self.show_toast("Invalid path", "error")
            return
            
        files = []
        if os.path.isdir(path):
            for root, _, fs in os.walk(path):
                for f in fs:
                    files.append(os.path.join(root, f))
        else:
            files.append(path)
            
        result = self.backup_manager.create_backup(files, "Manual backup")
        if result:
            self.show_toast("Backup created successfully!", "success")
            self.refresh_backups()
        else:
            self.show_toast("Backup failed", "error")
            
    def refresh_backups(self):
        backups = self.backup_manager.list_backups()
        self.backup_table.setRowCount(0)
        for b in backups:
            row = self.backup_table.rowCount()
            self.backup_table.insertRow(row)
            self.backup_table.setItem(row, 0, QTableWidgetItem(b['name']))
            self.backup_table.setItem(row, 1, QTableWidgetItem(b['created'].strftime('%Y-%m-%d %H:%M')))
            self.backup_table.setItem(row, 2, QTableWidgetItem(format_size(b['size'])))
            self.backup_table.setItem(row, 3, QTableWidgetItem(str(b['file_count'])))
            self.backup_table.item(row, 0).setData(Qt.UserRole, b['path'])
            
    def restore_backup(self):
        row = self.backup_table.currentRow()
        if row < 0:
            self.show_toast("Select a backup to restore", "warning")
            return
            
        backup_path = self.backup_table.item(row, 0).data(Qt.UserRole)
        dest = QFileDialog.getExistingDirectory(self, "Restore Destination")
        if dest:
            res = self.backup_manager.restore_backup(backup_path, dest)
            if res['success']:
                self.show_toast(f"Restored {len(res['restored'])} files", "success")
            else:
                self.show_toast(f"Restore failed: {res.get('error')}", "error")

    
    def init_status_bar(self):
        """Inisialisasi bilah status"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🟢 Ready - Drag a folder or click Browse to start")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.tabs.setCurrentIndex(0)
                self.path_input.setText(path)
                self.start_scan()
                break

    def show_toast(self, message: str, toast_type: str = "info"):
        """Show toast notification with stacking support."""
        toast = ToastNotification(message, toast_type, 3000, self)
        
        if not hasattr(self, '_active_toasts'):
            self._active_toasts = []
        
        self._active_toasts = [t for t in self._active_toasts if t.isVisible()]
        
        base_y = 80
        for existing_toast in self._active_toasts:
            base_y = max(base_y, existing_toast.y() + existing_toast.height() + 10)
        
        toast.move(self.width() - toast.width() - 20, base_y)
        self._active_toasts.append(toast)
        toast.show()

    def browse_path(self):
        """Jelajahi folder (Tab Pemindai)"""
        path = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if path:
            self.path_input.setText(path)
            
    def setup_shortcuts(self):
        """Siapkan pintasan keyboard"""
        QShortcut(QKeySequence("Ctrl+S"), self, lambda: self.tabs.setCurrentIndex(0) or self.start_scan())
        QShortcut(QKeySequence("Ctrl+F"), self, self.fix_permissions)
        QShortcut(QKeySequence("Ctrl+E"), self, lambda: self.export_results('csv'))
        QShortcut(QKeySequence("F5"), self, lambda: self.start_scan() if self.tabs.currentIndex() == 0 else self.refresh_backups())
    
    
    def start_scan(self):
        """Mulai memindai folder"""
        folderpath = self.path_input.text().strip()
        if not folderpath:
            self.show_toast("Please enter folder path", "warning")
            return
        if not os.path.isdir(folderpath):
            self.show_toast("Folder not found", "error")
            return
        
        self.integrity_manager.log_audit_event('scan_started', file_path=folderpath, details=f"Scan initiated for folder: {folderpath}")
        
        self.all_files = []
        self.file_table.setRowCount(0)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage(f"🔍 Scanning {folderpath}...")
        
        self.scan_thread = ScanThread(folderpath, CUSTOM_RULES)
        self.scan_thread.progress.connect(self.update_scan_progress)
        self.scan_thread.file_found.connect(self.add_file_to_table)
        self.scan_thread.finished.connect(self.scan_finished)
        self.scan_thread.error.connect(self.scan_error)
        self.scan_thread.start()

    def update_scan_progress(self, progress: int, message: str):
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(f"🔍 {message}")

    def add_file_to_table(self, file_data: dict):
        self.all_files.append(file_data)
        row = self.file_table.rowCount()
        self.file_table.insertRow(row)
        self.file_table.setItem(row, 0, QTableWidgetItem(file_data['name']))
        self.file_table.setItem(row, 1, QTableWidgetItem(file_data['relative']))
        self.file_table.setItem(row, 2, QTableWidgetItem(file_data['info']['mode']))
        self.file_table.setItem(row, 3, QTableWidgetItem(file_data['info']['symbolic']))
        self.file_table.setItem(row, 4, RiskTableWidgetItem(file_data['risk'], file_data['risk']))
        self.file_table.setItem(row, 5, QTableWidgetItem(file_data['expected'] or '-'))
        size_item = QTableWidgetItem(format_size(file_data['info']['size']))
        size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.file_table.setItem(row, 6, size_item)
        self.file_table.setItem(row, 7, QTableWidgetItem(file_data['info']['modified'].strftime('%Y-%m-%d %H:%M')))

    def scan_finished(self, files: list, stats: dict):
        self.progress_bar.setVisible(False)
        self.update_stats(stats)
        log_scan(self.db_conn, {'folder_path': self.path_input.text(), 'total_files': stats['total_files'], 'total_size': stats['total_size'], 'high_risk': stats['high_risk'], 'medium_risk': stats['medium_risk'], 'low_risk': stats['low_risk']})
        self.integrity_manager.log_audit_event('scan_completed', file_path=self.path_input.text(), details=f"Scan completed: {len(self.all_files)} files")
        self.status_bar.showMessage(f"✅ Scan complete: {len(self.all_files):,} files")
        self.show_toast(f"Scan complete: {len(self.all_files):,} files", "success")

    def update_stats(self, stats: dict):
        def update_label(parent_frame, value_text):
            for child in parent_frame.children():
                if isinstance(child, QLabel) and child.objectName().startswith("value_"):
                    child.setText(value_text)
                    break
        update_label(self.stat_total, f"{stats.get('total_files', 0):,}")
        update_label(self.stat_safe, f"{stats.get('low_risk', 0):,}")
        update_label(self.stat_medium, f"{stats.get('medium_risk', 0):,}")
        update_label(self.stat_high, f"{stats.get('high_risk', 0):,}")
        update_label(self.stat_size, format_size(stats.get('total_size', 0)))

    def scan_error(self, error: str):
        self.progress_bar.setVisible(False)
        self.show_toast(f"Scan error: {error}", "error")

    def apply_filter(self):
        filter_text = self.filter_combo.currentText()
        search_text = self.search_input.text().lower()
        for row in range(self.file_table.rowCount()):
            show_row = True
            if "All" not in filter_text:
                risk_item = self.file_table.item(row, 4)
                if risk_item and filter_text.split(" ")[1] not in risk_item.text(): show_row = False
            if show_row and search_text:
                if search_text not in self.file_table.item(row, 0).text().lower() and search_text not in self.file_table.item(row, 1).text().lower(): show_row = False
            self.file_table.setRowHidden(row, not show_row)

    def update_selection_count(self):
        """Update selection count label and fix button with quantitative feedback."""
        count = len(set(item.row() for item in self.file_table.selectedItems()))
        self.selected_count_label.setText(f"Selected: {count}")
        
        if count > 0:
            self.fix_selected_btn.setText(f"Harden {count} Selected")
        else:
            self.fix_selected_btn.setText("Harden Selected")

    def get_selected_files(self) -> List[dict]:
        selected_rows = set(item.row() for item in self.file_table.selectedItems())
        return [self.all_files[row] for row in selected_rows if row < len(self.all_files)]

    def fix_permissions(self):
        """Perbaiki semua izin berisiko"""
        risky_files = [f for f in self.all_files if f['risk'] in ['High', 'Medium']]
        
        if not risky_files:
            self.show_toast("No risky permissions found! ✅", "success")
            return
        
        msg = QMessageBox(self)
        msg.setWindowTitle('Fix Risky Permissions')
        msg.setText(f"Found {len(risky_files)} files with risky permissions.")
        msg.setInformativeText(
            f"🔴 High Risk: {sum(1 for f in risky_files if f['risk'] == 'High')}\n"
            f"⚠️ Medium Risk: {sum(1 for f in risky_files if f['risk'] == 'Medium')}\n\n"
            "Choose repair method:"
        )
        msg.setIcon(QMessageBox.Warning)
        
        quick_btn = msg.addButton("⚡ Quick Fix (Auto)", QMessageBox.AcceptRole)
        adv_btn = msg.addButton("⚙️ Advanced...", QMessageBox.ActionRole)
        cancel_btn = msg.addButton(QMessageBox.Cancel)
        
        msg.exec_()
        
        if msg.clickedButton() == quick_btn:
            self._apply_fixes(risky_files)
        elif msg.clickedButton() == adv_btn:
            self._open_advanced_fix_dialog(risky_files)
    
    def fix_selected_permissions(self):
        """Perbaiki izin file yang dipilih"""
        selected_files = self.get_selected_files()
        
        if not selected_files:
            self.show_toast("Please select files to fix", "warning")
            return
            
        self._open_advanced_fix_dialog(selected_files)
    
    def _open_advanced_fix_dialog(self, files: List[dict]):
        """Buka dialog izin lanjutan"""
        dialog = AdvancedPermissionDialog(self, len(files))
        if dialog.exec_():
            settings = dialog.get_settings()
            self._apply_fixes(files, settings)
        
    def _apply_fixes(self, files: List[dict], settings: dict = None):
        """Terapkan perbaikan izin dengan dukungan opsi lanjutan"""
        filepaths = [f['path'] for f in files]
        custom_mode = int(settings['permission'], 8) if settings else None
        recursive = settings.get('recursive', False) if settings else False
        
        if settings and settings.get('backup'):
            self.status_bar.showMessage("📦 Creating backup before changes...")
            self.backup_manager.create_backup(filepaths, "Backup before permission fix")
        
        self.status_bar.showMessage("🔧 Fixing permissions...")
        results = self.permission_fixer.batch_fix_permissions(
            filepaths,
            custom_mode=custom_mode,
            recursive=recursive
        )
        
        audit_details = f"Fixed {results['success']} files"
        if custom_mode:
            audit_details += f" (Mode: {oct(custom_mode)})"
        if recursive:
            audit_details += " (Recursive)"
            
        self.integrity_manager.log_audit_event(
            action_type='permissions_fixed',
            details=audit_details
        )
        
        if settings and settings.get('encrypt'):
            self.status_bar.showMessage("🔒 Encrypting files...")
            self.show_toast("Please use Encryption Tab for secure encryption", "info")
            
        self.show_toast(f"Fixed {results['success']} files", "success")
        self.status_bar.showMessage(f"✅ Fixed {results['success']} files • {results['failed']} failed")
        
        QTimer.singleShot(500, self.start_scan)

    def export_results(self, format_type: str):
        if not self.all_files: return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "csv" if format_type == 'csv' else "json"
        filename, _ = QFileDialog.getSaveFileName(self, f"Export {ext.upper()}", f"report_{timestamp}.{ext}", f"{ext.upper()} Files (*.{ext})")
        if filename:
            if format_type == 'csv': self._export_csv(filename)
            else: self._export_json(filename)

    def _export_csv(self, filename: str):
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Path', 'Mode', 'Risk', 'Expected', 'Size', 'Modified'])
                for fd in self.all_files:
                    writer.writerow([fd['name'], fd['relative'], fd['info']['mode'], fd['risk'], fd['expected'], fd['info']['size'], fd['info']['modified']])
            os.chmod(filename, 0o600)
            self._create_checksum(filename)
            self.show_toast("Export successful", "success")
        except Exception as e: self.show_toast(f"Export failed: {e}", "error")

    def _export_json(self, filename: str):
        try:
            stats = {
                'high_risk': sum(1 for f in self.all_files if f['risk'] == 'High'),
                'medium_risk': sum(1 for f in self.all_files if f['risk'] == 'Medium'),
                'low_risk': sum(1 for f in self.all_files if f['risk'] == 'Low'),
                'total_files': len(self.all_files)
            }
            
            def json_serial(obj):
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} not serializable")
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'stats': stats,
                'files': self.all_files
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=json_serial)
                
            os.chmod(filename, 0o600)
            self._create_checksum(filename)
            self.show_toast("Export successful", "success")
        except Exception as e:
            self.show_toast(f"Export failed: {e}", "error") 

    def _create_checksum(self, filename: str):
        try:
            h = hashlib.sha256()
            with open(filename, 'rb') as f: 
                for c in iter(lambda: f.read(4096), b''): h.update(c)
            with open(filename + '.sha256', 'w') as f: f.write(f"{h.hexdigest()}  {os.path.basename(filename)}\n")
            os.chmod(filename + '.sha256', 0o600)
        except: pass

    def check_cia_status(self):
        """Periksa dan tampilkan status kepatuhan CIA Triad"""
        self.status_bar.showMessage("🛡️ Checking CIA status...")
        cia_status = self.integrity_manager.get_cia_status()
        
        conf = cia_status['confidentiality']
        self.cia_confidentiality.setText(f"🔒 Confidentiality: {'✅ Secure' if conf['database_secured'] else '⚠️ Check DB'}")
        self.cia_confidentiality.setStyleSheet(f"color: {'#10b981' if conf['database_secured'] else '#f59e0b'}; font-size: 11px;")
        
        integ = cia_status['integrity']
        valid = integ['database_valid'] and integ['audit_logs_valid']
        self.cia_integrity.setText(f"✅ Integrity: {'✅ Valid' if valid else '⚠️ Issues'}")
        self.cia_integrity.setStyleSheet(f"color: {'#10b981' if valid else '#ef4444'}; font-size: 11px;")
        
        avail = cia_status['availability']
        self.cia_availability.setText(f"🌐 Availability: {'✅ OK' if avail['database_accessible'] else '❌ Error'}")
        self.cia_availability.setStyleSheet(f"color: {'#10b981' if avail['database_accessible'] else '#ef4444'}; font-size: 11px;")
        
        self.show_toast("CIA Status Updated", "info")

    def closeEvent(self, event):
        if hasattr(self, 'db_conn'): self.db_conn.close()
        self.integrity_manager.log_audit_event('application_closed', details='Application closed normally')
        event.accept()

from PyQt5.QtCore import QThread
