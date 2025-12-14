"""
FilePermissionChecker v2.0
Advanced File Permission Security Tool
Focused on: Scanning, Analyzing, and Fixing File Permissions
"""

import sys
import os
import json
import csv
import time
import hashlib
from datetime import datetime
from typing import List, Dict
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QHeaderView, QProgressBar,
    QStatusBar, QComboBox, QCheckBox, QGroupBox,
    QAbstractItemView, QShortcut, QGridLayout, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QKeySequence, QDragEnterEvent, QDropEvent

from core.scanner import ScanThread
from core.permission_fixer import PermissionFixer
from core.integrity import IntegrityManager
from core.database import init_database, log_scan
from ui.modern_widgets import (
    GlassCard, ModernButton, AnimatedProgressBar,
    ModernTableWidget, RiskTableWidgetItem, ToastNotification
)
from utils.constants import CUSTOM_RULES
from utils.helpers import format_size


class FilePermissionChecker(QMainWindow):
    """Main application window - Permission Checker Only"""
    
    def __init__(self):
        super().__init__()
        self.all_files = []
        self.scan_cache = {}
        self.dark_mode = True
        
        # Core components (simplified)
        self.permission_fixer = PermissionFixer()
        self.integrity_manager = IntegrityManager()
        
        # Database
        self.db_conn = init_database()
        
        # Initialize UI
        self.init_ui()
        self.setup_shortcuts()
        self.load_stylesheet()
        self.setAcceptDrops(True)
    
    def load_stylesheet(self):
        """Load modern stylesheet"""
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
        """Initialize modern UI - Simplified for Permission Checking"""
        self.setWindowTitle("🔒 File Permission Checker")
        self.setGeometry(100, 100, 1400, 850)
        self.setMinimumSize(1100, 650)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header bar
        self.init_header()
        main_layout.addWidget(self.header_widget)
        
        # Content area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Sidebar with stats
        self.init_sidebar()
        content_layout.addWidget(self.sidebar, 0)
        
        # Main content
        self.init_main_content()
        content_layout.addWidget(self.main_panel, 1)
        
        main_layout.addWidget(content_widget, 1)
        
        # Status bar
        self.init_status_bar()
    
    def init_header(self):
        """Initialize header bar"""
        self.header_widget = QFrame()
        self.header_widget.setObjectName("headerBar")
        self.header_widget.setStyleSheet("""
            QFrame#headerBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 0.15), stop:1 rgba(118, 75, 162, 0.15));
                border-bottom: 1px solid rgba(102, 126, 234, 0.3);
            }
        """)
        self.header_widget.setFixedHeight(70)
        
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(25, 10, 25, 10)
        
        # Logo/Title
        title_layout = QVBoxLayout()
        title_label = QLabel("🔒 File Permission Checker")
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
        """)
        subtitle_label = QLabel("Scan • Analyze • Fix Permissions")
        subtitle_label.setStyleSheet("""
            font-size: 12px;
            color: #94a3b8;
        """)
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.setSpacing(2)
        header_layout.addLayout(title_layout)
        
        header_layout.addStretch()
        
        # Quick actions
        scan_btn = ModernButton("🔍 Scan", style="primary")
        scan_btn.clicked.connect(self.start_scan)
        header_layout.addWidget(scan_btn)
        
        fix_btn = ModernButton("🔧 Fix Risky", style="warning")
        fix_btn.clicked.connect(self.fix_permissions)
        header_layout.addWidget(fix_btn)
        
        # Export menu
        export_csv_btn = ModernButton("📊 CSV", style="secondary")
        export_csv_btn.clicked.connect(lambda: self.export_results('csv'))
        header_layout.addWidget(export_csv_btn)
        
        export_json_btn = ModernButton("📋 JSON", style="secondary")
        export_json_btn.clicked.connect(lambda: self.export_results('json'))
        header_layout.addWidget(export_json_btn)
    
    def init_sidebar(self):
        """Initialize sidebar with statistics"""
        self.sidebar = GlassCard()
        self.sidebar.setFixedWidth(260)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(15)
        
        # Stats title
        stats_title = QLabel("📊 Statistics")
        stats_title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 10px;
        """)
        sidebar_layout.addWidget(stats_title)
        
        # Stat cards
        self.stat_total = self._create_stat_item("📁", "Total Files", "0", "#667eea")
        sidebar_layout.addWidget(self.stat_total)
        
        self.stat_safe = self._create_stat_item("✅", "Safe (Low Risk)", "0", "#10b981")
        sidebar_layout.addWidget(self.stat_safe)
        
        self.stat_medium = self._create_stat_item("⚠️", "Medium Risk", "0", "#f59e0b")
        sidebar_layout.addWidget(self.stat_medium)
        
        self.stat_high = self._create_stat_item("🔴", "High Risk", "0", "#ef4444")
        sidebar_layout.addWidget(self.stat_high)
        
        sidebar_layout.addSpacing(15)
        
        # Size info
        self.stat_size = self._create_stat_item("💾", "Total Size", "0 B", "#8b5cf6")
        sidebar_layout.addWidget(self.stat_size)
        
        sidebar_layout.addSpacing(15)
        
        # CIA Status Section
        cia_title = QLabel("🛡️ CIA Triad Status")
        cia_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #ffffff;")
        sidebar_layout.addWidget(cia_title)
        
        # CIA Status items
        self.cia_confidentiality = QLabel("🔒 Confidentiality: ✅")
        self.cia_confidentiality.setStyleSheet("color: #10b981; font-size: 11px;")
        sidebar_layout.addWidget(self.cia_confidentiality)
        
        self.cia_integrity = QLabel("✅ Integrity: ✅")
        self.cia_integrity.setStyleSheet("color: #10b981; font-size: 11px;")
        sidebar_layout.addWidget(self.cia_integrity)
        
        self.cia_availability = QLabel("🌐 Availability: ✅")
        self.cia_availability.setStyleSheet("color: #10b981; font-size: 11px;")
        sidebar_layout.addWidget(self.cia_availability)
        
        # Check CIA button
        cia_check_btn = QPushButton("🔍 Check CIA Status")
        cia_check_btn.setStyleSheet("""
            QPushButton {
                background: rgba(102, 126, 234, 0.2);
                border: 1px solid rgba(102, 126, 234, 0.4);
                border-radius: 6px;
                padding: 8px;
                color: #667eea;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(102, 126, 234, 0.3);
            }
        """)
        cia_check_btn.clicked.connect(self.check_cia_status)
        sidebar_layout.addWidget(cia_check_btn)
        
        sidebar_layout.addStretch()
        
        # Legend
        legend_title = QLabel("🎨 Risk Legend")
        legend_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #ffffff;")
        sidebar_layout.addWidget(legend_title)
        
        legend_items = [
            ("🔴 High", "777, 666, world-writable"),
            ("⚠️ Medium", "Group/other writable"),
            ("✅ Low", "Standard safe permissions"),
        ]
        
        for icon_label, desc in legend_items:
            item = QLabel(f"{icon_label}: {desc}")
            item.setStyleSheet("color: #94a3b8; font-size: 11px;")
            item.setWordWrap(True)
            sidebar_layout.addWidget(item)
        
        sidebar_layout.addSpacing(10)
        
        # Version info
        version_label = QLabel("v2.0.0 • Permission Focused")
        version_label.setStyleSheet("""
            color: #64748b;
            font-size: 10px;
            text-align: center;
        """)
        version_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(version_label)
    
    def _create_stat_item(self, icon: str, title: str, value: str, color: str) -> QFrame:
        """Create mini stat widget"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(15, 15, 26, 0.5);
                border: 1px solid rgba(102, 126, 234, 0.2);
                border-radius: 10px;
            }}
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        value_label = QLabel(value)
        value_label.setObjectName(f"value_{title.lower().replace(' ', '_').replace('(', '').replace(')', '')}")
        value_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {color};
        """)
        text_layout.addWidget(value_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 10px;
            color: #94a3b8;
        """)
        text_layout.addWidget(title_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return frame
    
    def init_main_content(self):
        """Initialize main content panel"""
        self.main_panel = QFrame()
        main_layout = QVBoxLayout(self.main_panel)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)
        
        # Top panel - Path input
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
        
        browse_btn = ModernButton("Browse", style="secondary")
        browse_btn.clicked.connect(self.browse_path)
        top_layout.addWidget(browse_btn)
        
        scan_btn = ModernButton("🔍 Scan", style="primary")
        scan_btn.clicked.connect(self.start_scan)
        top_layout.addWidget(scan_btn)
        
        main_layout.addWidget(top_card)
        
        # Progress bar
        self.progress_bar = AnimatedProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(26)
        main_layout.addWidget(self.progress_bar)
        
        # File table
        self.file_table = ModernTableWidget()
        self.file_table.setColumnCount(8)
        self.file_table.setHorizontalHeaderLabels([
            "📄 Name", "📁 Path", "🔢 Mode", "🔣 Symbolic", 
            "⚠️ Risk", "🎯 Expected", "📊 Size", "📅 Modified"
        ])
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_table.setSelectionMode(QTableWidget.MultiSelection)
        self.file_table.setSortingEnabled(True)
        self.file_table.itemSelectionChanged.connect(self.update_selection_count)
        main_layout.addWidget(self.file_table, 1)
        
        # Bottom panel - Filters and actions
        bottom_card = GlassCard()
        bottom_layout = QHBoxLayout(bottom_card)
        bottom_layout.setContentsMargins(20, 12, 20, 12)
        
        # Filter dropdown
        filter_label = QLabel("🔍 Filter:")
        filter_label.setStyleSheet("font-weight: 600;")
        bottom_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Files", "🔴 High Risk", "⚠️ Medium Risk", "✅ Low Risk"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        self.filter_combo.setMinimumWidth(140)
        bottom_layout.addWidget(self.filter_combo)
        
        bottom_layout.addSpacing(20)
        
        # Search
        search_label = QLabel("🔎 Search:")
        search_label.setStyleSheet("font-weight: 600;")
        bottom_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files...")
        self.search_input.textChanged.connect(self.apply_filter)
        self.search_input.setMinimumWidth(200)
        bottom_layout.addWidget(self.search_input)
        
        bottom_layout.addStretch()
        
        # Selection count
        self.selected_count_label = QLabel("Selected: 0")
        self.selected_count_label.setStyleSheet("""
            color: #667eea;
            font-weight: 700;
            font-size: 13px;
        """)
        bottom_layout.addWidget(self.selected_count_label)
        
        bottom_layout.addSpacing(15)
        
        # Fix selected button
        fix_selected_btn = ModernButton("🔧 Fix Selected", style="warning")
        fix_selected_btn.clicked.connect(self.fix_selected_permissions)
        bottom_layout.addWidget(fix_selected_btn)
        
        main_layout.addWidget(bottom_card)
    
    def init_status_bar(self):
        """Initialize status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🟢 Ready - Drag a folder or click Browse to start")
    
    # ======================== DRAG & DROP ========================
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.path_input.setText(path)
                self.start_scan()
                break
    
    # ======================== CORE METHODS ========================
    
    def show_toast(self, message: str, toast_type: str = "info"):
        """Show toast notification"""
        toast = ToastNotification(message, toast_type, 3000, self)
        toast.move(self.width() - toast.width() - 20, 80)
        toast.show()
    
    def start_scan(self):
        """Start scanning folder"""
        folderpath = self.path_input.text().strip()
        
        if not folderpath:
            self.show_toast("Please enter folder path", "warning")
            return
        
        if not os.path.isdir(folderpath):
            self.show_toast("Folder not found", "error")
            return
        
        # Log audit event
        self.integrity_manager.log_audit_event(
            action_type='scan_started',
            file_path=folderpath,
            details=f"Scan initiated for folder: {folderpath}"
        )
        
        # Check cache
        try:
            cache_key = f"{folderpath}_{os.path.getmtime(folderpath)}"
            if cache_key in self.scan_cache:
                cached_data = self.scan_cache[cache_key]
                if time.time() - cached_data['timestamp'] < 300:
                    self.all_files = cached_data['files']
                    self.display_scan_results(cached_data['files'])
                    self.update_stats(cached_data['stats'])
                    self.show_toast("Using cached results", "info")
                    return
        except:
            pass
        
        # Clear previous results
        self.all_files = []
        self.file_table.setRowCount(0)
        
        # Update UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage(f"🔍 Scanning {folderpath}...")
        
        # Start scan thread
        self.scan_thread = ScanThread(folderpath, CUSTOM_RULES)
        self.scan_thread.progress.connect(self.update_scan_progress)
        self.scan_thread.file_found.connect(self.add_file_to_table)
        self.scan_thread.finished.connect(self.scan_finished)
        self.scan_thread.error.connect(self.scan_error)
        self.scan_thread.start()
    
    def update_scan_progress(self, progress: int, message: str):
        """Update scan progress"""
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(f"🔍 {message}")
    
    def add_file_to_table(self, file_data: dict):
        """Add file to table"""
        self.all_files.append(file_data)
        
        row = self.file_table.rowCount()
        self.file_table.insertRow(row)
        
        # Columns
        self.file_table.setItem(row, 0, QTableWidgetItem(file_data['name']))
        self.file_table.setItem(row, 1, QTableWidgetItem(file_data['relative']))
        self.file_table.setItem(row, 2, QTableWidgetItem(file_data['info']['mode']))
        self.file_table.setItem(row, 3, QTableWidgetItem(file_data['info']['symbolic']))
        
        # Risk level with custom widget
        risk_item = RiskTableWidgetItem(file_data['risk'], file_data['risk'])
        self.file_table.setItem(row, 4, risk_item)
        
        # Expected permission
        expected = file_data['expected'] or '-'
        self.file_table.setItem(row, 5, QTableWidgetItem(expected))
        
        # Size
        size_str = format_size(file_data['info']['size'])
        size_item = QTableWidgetItem(size_str)
        size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.file_table.setItem(row, 6, size_item)
        
        # Modified date
        modified = file_data['info']['modified'].strftime('%Y-%m-%d %H:%M')
        self.file_table.setItem(row, 7, QTableWidgetItem(modified))
    
    def scan_finished(self, files: list, stats: dict):
        """Handle scan completion"""
        # Cache results
        try:
            cache_key = f"{self.path_input.text()}_{os.path.getmtime(self.path_input.text())}"
            self.scan_cache[cache_key] = {
                'files': self.all_files,
                'stats': stats,
                'timestamp': time.time()
            }
        except:
            pass
        
        # Update UI
        self.progress_bar.setVisible(False)
        
        # Update stats
        self.update_stats(stats)
        
        # Log to database
        log_scan(self.db_conn, {
            'folder_path': self.path_input.text(),
            'total_files': stats['total_files'],
            'total_size': stats['total_size'],
            'high_risk': stats['high_risk'],
            'medium_risk': stats['medium_risk'],
            'low_risk': stats['low_risk'],
            'duration': stats.get('duration', 0)
        })
        
        # Log audit
        self.integrity_manager.log_audit_event(
            action_type='scan_completed',
            file_path=self.path_input.text(),
            details=f"Scan completed: {len(self.all_files)} files, {stats['high_risk']} high risk"
        )
        
        # Update status
        total_size = format_size(stats['total_size'])
        self.status_bar.showMessage(
            f"✅ Scan complete: {len(self.all_files):,} files ({total_size}) • "
            f"🔴 {stats['high_risk']} High • ⚠️ {stats['medium_risk']} Medium • ✅ {stats['low_risk']} Low"
        )
        self.show_toast(f"Scan complete: {len(self.all_files):,} files", "success")
    
    def update_stats(self, stats: dict):
        """Update sidebar statistics"""
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
    
    def scan_error(self, error: str, traceback_str: str):
        """Handle scan error"""
        self.progress_bar.setVisible(False)
        self.show_toast(f"Scan error: {error}", "error")
        self.status_bar.showMessage(f"❌ Error: {error}")
    
    def display_scan_results(self, files_data: list):
        """Display scan results from cache"""
        self.file_table.setRowCount(0)
        self.all_files = files_data
        for file_data in files_data:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)
            
            self.file_table.setItem(row, 0, QTableWidgetItem(file_data['name']))
            self.file_table.setItem(row, 1, QTableWidgetItem(file_data['relative']))
            self.file_table.setItem(row, 2, QTableWidgetItem(file_data['info']['mode']))
            self.file_table.setItem(row, 3, QTableWidgetItem(file_data['info']['symbolic']))
            
            risk_item = RiskTableWidgetItem(file_data['risk'], file_data['risk'])
            self.file_table.setItem(row, 4, risk_item)
            
            expected = file_data['expected'] or '-'
            self.file_table.setItem(row, 5, QTableWidgetItem(expected))
            
            size_str = format_size(file_data['info']['size'])
            size_item = QTableWidgetItem(size_str)
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.file_table.setItem(row, 6, size_item)
            
            modified = file_data['info']['modified'].strftime('%Y-%m-%d %H:%M')
            self.file_table.setItem(row, 7, QTableWidgetItem(modified))
    
    def apply_filter(self):
        """Apply filter to table"""
        filter_text = self.filter_combo.currentText()
        search_text = self.search_input.text().lower()
        
        for row in range(self.file_table.rowCount()):
            show_row = True
            
            # Risk filter
            if "All" not in filter_text:
                risk_item = self.file_table.item(row, 4)
                if risk_item:
                    if "High" in filter_text and risk_item.text() != "High":
                        show_row = False
                    elif "Medium" in filter_text and risk_item.text() != "Medium":
                        show_row = False
                    elif "Low" in filter_text and risk_item.text() != "Low":
                        show_row = False
            
            # Search filter
            if show_row and search_text:
                name_item = self.file_table.item(row, 0)
                path_item = self.file_table.item(row, 1)
                
                if name_item and path_item:
                    name = name_item.text().lower()
                    path = path_item.text().lower()
                    if search_text not in name and search_text not in path:
                        show_row = False
            
            self.file_table.setRowHidden(row, not show_row)
    
    def get_selected_files(self) -> List[dict]:
        """Get selected files from table"""
        selected_rows = set()
        for item in self.file_table.selectedItems():
            selected_rows.add(item.row())
        
        return [self.all_files[row] for row in selected_rows if row < len(self.all_files)]
    
    def update_selection_count(self):
        """Update selection count label"""
        count = len(set(item.row() for item in self.file_table.selectedItems()))
        self.selected_count_label.setText(f"Selected: {count}")
    
    def fix_permissions(self):
        """Fix all risky permissions"""
        risky_files = [f for f in self.all_files if f['risk'] in ['High', 'Medium']]
        
        if not risky_files:
            self.show_toast("No risky permissions found! ✅", "success")
            return
        
        reply = QMessageBox.question(
            self, 'Fix Risky Permissions',
            f"Found {len(risky_files)} files with risky permissions.\n\n"
            f"🔴 High Risk: {sum(1 for f in risky_files if f['risk'] == 'High')}\n"
            f"⚠️ Medium Risk: {sum(1 for f in risky_files if f['risk'] == 'Medium')}\n\n"
            "Apply automatic fixes?\n"
            "(Files: 644, Dirs: 755, Sensitive: 600)",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._apply_fixes(risky_files)
    
    def fix_selected_permissions(self):
        """Fix selected files permissions"""
        selected_files = self.get_selected_files()
        
        if not selected_files:
            self.show_toast("Please select files to fix", "warning")
            return
        
        risky = [f for f in selected_files if f['risk'] in ['High', 'Medium']]
        
        if not risky:
            self.show_toast("No risky files in selection", "info")
            return
        
        reply = QMessageBox.question(
            self, 'Fix Selected Permissions',
            f"Fix permissions for {len(risky)} risky files?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._apply_fixes(risky)
    
    def _apply_fixes(self, files: List[dict]):
        """Apply permission fixes"""
        results = self.permission_fixer.batch_fix_permissions(
            [f['path'] for f in files],
            lambda p: self.status_bar.showMessage(f"🔧 Fixing: {p}%")
        )
        
        # Log audit
        self.integrity_manager.log_audit_event(
            action_type='permissions_fixed',
            details=f"Fixed {results['success']} files, {results['failed']} failed"
        )
        
        self.show_toast(f"Fixed {results['success']} files", "success")
        self.status_bar.showMessage(f"✅ Fixed {results['success']} files • {results['failed']} failed")
        
        # Rescan
        QTimer.singleShot(500, self.start_scan)
    
    # ======================== EXPORT ========================
    
    def export_results(self, format_type: str):
        """Export results to CSV or JSON"""
        if not self.all_files:
            self.show_toast("No data to export", "warning")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == 'csv':
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export CSV",
                f"permission_report_{timestamp}.csv",
                "CSV Files (*.csv)"
            )
            if filename:
                self._export_csv(filename)
        else:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export JSON",
                f"permission_report_{timestamp}.json",
                "JSON Files (*.json)"
            )
            if filename:
                self._export_json(filename)
    
    def _export_csv(self, filename: str):
        """Export to CSV with checksum"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'Filename', 'Path', 'Mode', 'Symbolic', 'Risk Level',
                    'Expected', 'Size', 'Modified'
                ])
                
                for file_data in self.all_files:
                    info = file_data['info']
                    writer.writerow([
                        file_data['name'],
                        file_data['relative'],
                        info['mode'],
                        info['symbolic'],
                        file_data['risk'],
                        file_data['expected'] or '-',
                        info['size'],
                        info['modified'].isoformat()
                    ])
            
            # Set secure permissions
            os.chmod(filename, 0o600)
            
            # Create checksum file
            self._create_checksum(filename)
            
            self.show_toast(f"Exported to {os.path.basename(filename)}", "success")
            self.status_bar.showMessage(f"✅ Exported: {filename}")
            
        except Exception as e:
            self.show_toast(f"Export failed: {str(e)}", "error")
    
    def _export_json(self, filename: str):
        """Export to JSON with checksum"""
        try:
            stats = {
                'high_risk': sum(1 for f in self.all_files if f['risk'] == 'High'),
                'medium_risk': sum(1 for f in self.all_files if f['risk'] == 'Medium'),
                'low_risk': sum(1 for f in self.all_files if f['risk'] == 'Low'),
                'total_size': sum(f['info']['size'] for f in self.all_files)
            }
            
            export_data = {
                'export_date': datetime.now().isoformat(),
                'folder': self.path_input.text(),
                'total_files': len(self.all_files),
                'statistics': stats,
                'files': self.all_files
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            # Set secure permissions
            os.chmod(filename, 0o600)
            
            # Create checksum file
            self._create_checksum(filename)
            
            self.show_toast(f"Exported to {os.path.basename(filename)}", "success")
            self.status_bar.showMessage(f"✅ Exported: {filename}")
            
        except Exception as e:
            self.show_toast(f"Export failed: {str(e)}", "error")
    
    def _create_checksum(self, filename: str):
        """Create SHA256 checksum file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(filename, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(byte_block)
            
            checksum = sha256_hash.hexdigest()
            checksum_file = filename + '.sha256'
            
            with open(checksum_file, 'w') as f:
                f.write(f"{checksum}  {os.path.basename(filename)}\n")
            
            os.chmod(checksum_file, 0o600)
        except:
            pass
    
    # ======================== UTILITIES ========================
    
    def browse_path(self):
        """Browse for folder"""
        path = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if path:
            self.path_input.setText(path)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.start_scan)
        QShortcut(QKeySequence("Ctrl+F"), self, self.fix_permissions)
        QShortcut(QKeySequence("Ctrl+E"), self, lambda: self.export_results('csv'))
        QShortcut(QKeySequence("F5"), self, self.start_scan)
        QShortcut(QKeySequence("Esc"), self, self.cancel_scan)
    
    def cancel_scan(self):
        """Cancel current scan"""
        if hasattr(self, 'scan_thread') and self.scan_thread.isRunning():
            self.scan_thread.cancel()
            self.status_bar.showMessage("⚠️ Scan cancelled")
            self.progress_bar.setVisible(False)
    
    def check_cia_status(self):
        """Check and display CIA Triad compliance status"""
        self.status_bar.showMessage("🛡️ Checking CIA status...")
        
        # Get CIA status from integrity manager
        cia_status = self.integrity_manager.get_cia_status()
        
        # Update Confidentiality
        conf = cia_status['confidentiality']
        if conf['database_secured']:
            self.cia_confidentiality.setText("🔒 Confidentiality: ✅ Secure")
            self.cia_confidentiality.setStyleSheet("color: #10b981; font-size: 11px;")
        else:
            self.cia_confidentiality.setText("🔒 Confidentiality: ⚠️ Check DB")
            self.cia_confidentiality.setStyleSheet("color: #f59e0b; font-size: 11px;")
        
        # Update Integrity
        integ = cia_status['integrity']
        if integ['database_valid'] and integ['audit_logs_valid']:
            self.cia_integrity.setText("✅ Integrity: ✅ Valid")
            self.cia_integrity.setStyleSheet("color: #10b981; font-size: 11px;")
        else:
            self.cia_integrity.setText("✅ Integrity: ⚠️ Issues")
            self.cia_integrity.setStyleSheet("color: #ef4444; font-size: 11px;")
        
        # Update Availability
        avail = cia_status['availability']
        if avail['database_accessible']:
            self.cia_availability.setText("🌐 Availability: ✅ OK")
            self.cia_availability.setStyleSheet("color: #10b981; font-size: 11px;")
        else:
            self.cia_availability.setText("🌐 Availability: ❌ Error")
            self.cia_availability.setStyleSheet("color: #ef4444; font-size: 11px;")
        
        # Log audit event
        self.integrity_manager.log_audit_event(
            action_type='cia_check',
            details=f"CIA Check: C={conf['status']}, I={integ['status']}, A={avail['status']}"
        )
        
        # Show summary
        all_ok = (conf['database_secured'] and integ['database_valid'] and 
                  integ['audit_logs_valid'] and avail['database_accessible'])
        
        if all_ok:
            self.show_toast("CIA Triad: All checks passed! ✅", "success")
            self.status_bar.showMessage("🛡️ CIA Status: All checks passed ✅")
        else:
            self.show_toast("CIA Triad: Some issues detected", "warning")
            self.status_bar.showMessage("🛡️ CIA Status: Issues detected ⚠️")

    
    def closeEvent(self, event):
        """Handle application close"""
        # Close database
        if hasattr(self, 'db_conn'):
            self.db_conn.close()
        
        # Log audit
        self.integrity_manager.log_audit_event(
            action_type='application_closed',
            details='Application closed normally'
        )
        
        event.accept()