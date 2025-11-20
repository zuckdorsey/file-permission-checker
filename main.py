import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QLineEdit, QPushButton,
                              QTextEdit, QTableWidget, QTableWidgetItem,
                              QFileDialog, QMessageBox, QTabWidget, QHeaderView,
                              QProgressBar, QStatusBar, QComboBox, QCheckBox,
                              QGroupBox, QGridLayout, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QDragEnterEvent, QDropEvent
import os
import stat
import csv
import json
from datetime import datetime
from pathlib import Path
import sqlite3


# Custom Rules Engine
CUSTOM_RULES = {
    '.env': '600',
    '.git': '700',
    'storage': '755',
    'config': '644',
    'private': '600',
}


class ScanThread(QThread):
    """Thread untuk scanning folder agar UI tidak freeze"""
    progress = pyqtSignal(int)
    file_found = pyqtSignal(dict)
    finished = pyqtSignal(list)
    
    def __init__(self, folder_path, custom_rules):
        super().__init__()
        self.folder_path = folder_path
        self.custom_rules = custom_rules
        self.all_files = []
        
    def run(self):
        file_count = 0
        total_files = sum([len(files) for r, d, files in os.walk(self.folder_path)])
        
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                filepath = os.path.join(root, file)
                info = self.get_permission_info(filepath)
                if info:
                    file_count += 1
                    relative_path = os.path.relpath(filepath, self.folder_path)
                    
                    # Determine risk level
                    risk_level = self.determine_risk_level(info, filepath)
                    
                    # Check custom rules
                    expected_perm = self.check_custom_rules(filepath)
                    
                    file_data = {
                        'path': filepath,
                        'relative': relative_path,
                        'name': file,
                        'info': info,
                        'risk': risk_level,
                        'expected': expected_perm
                    }
                    
                    self.all_files.append(file_data)
                    self.file_found.emit(file_data)
                    
                    # Update progress
                    progress_percent = int((file_count / total_files) * 100)
                    self.progress.emit(progress_percent)
        
        self.finished.emit(self.all_files)
    
    def get_permission_info(self, filepath):
        """Mendapatkan informasi izin file"""
        try:
            file_stat = os.stat(filepath)
            
            is_readable = bool(file_stat.st_mode & stat.S_IRUSR)
            is_writable = bool(file_stat.st_mode & stat.S_IWUSR)
            is_executable = bool(file_stat.st_mode & stat.S_IXUSR)
            
            # Get octal permission
            mode_octal = oct(file_stat.st_mode)[-3:]
            
            # Get symbolic permission (like ls -l)
            mode_symbolic = stat.filemode(file_stat.st_mode)
            
            return {
                'readable': is_readable,
                'writable': is_writable,
                'executable': is_executable,
                'mode': mode_octal,
                'symbolic': mode_symbolic,
                'size': file_stat.st_size,
                'modified': datetime.fromtimestamp(file_stat.st_mtime)
            }
        except Exception as e:
            return None
    
    def determine_risk_level(self, info, filepath):
        """Menentukan tingkat risiko berdasarkan permission"""
        mode = info['mode']
        
        # High risk: world-writable (777, 666, etc)
        if mode in ['777', '666', '767', '676']:
            return 'High'
        
        # Medium risk: group writable or executable for sensitive files
        if mode[1] in ['6', '7'] or mode[2] in ['6', '7']:
            # Check if it's a sensitive file
            sensitive_extensions = ['.env', '.key', '.pem', '.conf', '.ini']
            if any(filepath.endswith(ext) for ext in sensitive_extensions):
                return 'High'
            return 'Medium'
        
        # Low risk: standard permissions
        return 'Low'
    
    def check_custom_rules(self, filepath):
        """Check if file matches custom rules"""
        filename = os.path.basename(filepath)
        for pattern, expected_perm in self.custom_rules.items():
            if pattern in filepath or filename == pattern:
                return expected_perm
        return None

class FilePermissionChecker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.all_files = []
        self.dark_mode = False
        self.init_database()
        self.init_ui()
        self.setAcceptDrops(True)  # Enable drag & drop
    
    def init_database(self):
        """Initialize SQLite database for logging"""
        self.db_conn = sqlite3.connect('scan_logs.db')
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_date DATETIME,
                folder_path TEXT,
                total_files INTEGER,
                high_risk INTEGER,
                medium_risk INTEGER,
                low_risk INTEGER
            )
        ''')
        self.db_conn.commit()
    
    def init_ui(self):
        self.setWindowTitle("📋 Advanced File Permission Checker")
        self.setGeometry(100, 100, 1200, 800)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Widget utama
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Header
        header_label = QLabel("📋 Advanced File Permission Checker")
        header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header_label.setFont(header_font)
        main_layout.addWidget(header_label)
        
        subtitle_label = QLabel("Periksa, Analisis, dan Perbaiki izin file dengan mudah")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: gray;")
        main_layout.addWidget(subtitle_label)
        
        # Dark mode toggle
        dark_mode_layout = QHBoxLayout()
        dark_mode_layout.addStretch()
        self.dark_mode_checkbox = QCheckBox("🌙 Dark Mode")
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        dark_mode_layout.addWidget(self.dark_mode_checkbox)
        main_layout.addLayout(dark_mode_layout)
        
        # Input section
        input_group = QGroupBox("📂 Pilih Folder untuk Scan")
        input_layout = QHBoxLayout()
        
        input_label = QLabel("Path:")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Drag folder ke sini atau klik Browse...")
        
        browse_btn = QPushButton("📂 Browse...")
        browse_btn.clicked.connect(self.browse_path)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.path_input, 3)
        input_layout.addWidget(browse_btn)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("🔍 Scan Folder")
        self.scan_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px 20px; font-weight: bold; font-size: 14px;")
        self.scan_btn.clicked.connect(self.start_scan)
        
        self.fix_btn = QPushButton("� Fix Risky Permissions")
        self.fix_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px 20px; font-weight: bold; font-size: 14px;")
        self.fix_btn.clicked.connect(self.fix_permissions)
        self.fix_btn.setEnabled(False)
        
        self.export_csv_btn = QPushButton("📄 Export CSV")
        self.export_csv_btn.clicked.connect(lambda: self.export_results('csv'))
        self.export_csv_btn.setEnabled(False)
        
        self.export_json_btn = QPushButton("📋 Export JSON")
        self.export_json_btn.clicked.connect(lambda: self.export_results('json'))
        self.export_json_btn.setEnabled(False)
        
        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(self.fix_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.export_csv_btn)
        button_layout.addWidget(self.export_json_btn)
        main_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Statistics section
        self.stats_group = QGroupBox("📊 Statistik Scan")
        stats_layout = QGridLayout()
        
        self.total_files_label = QLabel("Total File: 0")
        self.total_files_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.safe_files_label = QLabel("✅ Aman: 0")
        self.safe_files_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        
        self.medium_risk_label = QLabel("⚠️ Medium Risk: 0")
        self.medium_risk_label.setStyleSheet("color: orange; font-weight: bold; font-size: 14px;")
        
        self.high_risk_label = QLabel("🔴 High Risk: 0")
        self.high_risk_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        
        stats_layout.addWidget(self.total_files_label, 0, 0)
        stats_layout.addWidget(self.safe_files_label, 0, 1)
        stats_layout.addWidget(self.medium_risk_label, 0, 2)
        stats_layout.addWidget(self.high_risk_label, 0, 3)
        
        self.stats_group.setLayout(stats_layout)
        self.stats_group.setVisible(False)
        main_layout.addWidget(self.stats_group)
        
        # Filter section
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "High Risk", "Medium Risk", "Low Risk"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)
        
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by filename...")
        self.search_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        # Results Table
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(8)
        self.result_table.setHorizontalHeaderLabels([
            "Nama File", "Path Relatif", "Mode", "Symbolic", "Risk Level", 
            "Expected", "Size", "Modified"
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSortingEnabled(True)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.result_table)
    
    def browse_path(self):
        """Browse untuk folder"""
        path = QFileDialog.getExistingDirectory(self, "Pilih Folder untuk Scan")
        if path:
            self.path_input.setText(path)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            folder_path = files[0]
            if os.path.isdir(folder_path):
                self.path_input.setText(folder_path)
                self.statusBar.showMessage(f"Folder dropped: {folder_path}")
            else:
                QMessageBox.warning(self, "Invalid Drop", "Please drop a folder, not a file.")
    
    def start_scan(self):
        """Start scanning folder"""
        folderpath = self.path_input.text().strip()
        
        if not folderpath:
            QMessageBox.warning(self, "Peringatan", "Silakan masukkan path folder terlebih dahulu.")
            return
        
        if not os.path.isdir(folderpath):
            QMessageBox.critical(self, "Error", "Folder tidak ditemukan.")
            return
        
        # Clear previous results
        self.result_table.setRowCount(0)
        self.all_files = []
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Disable buttons
        self.scan_btn.setEnabled(False)
        self.fix_btn.setEnabled(False)
        
        self.statusBar.showMessage("Scanning folder...")
        
        # Start scan thread
        self.scan_thread = ScanThread(folderpath, CUSTOM_RULES)
        self.scan_thread.progress.connect(self.update_progress)
        self.scan_thread.file_found.connect(self.add_file_to_table)
        self.scan_thread.finished.connect(self.scan_finished)
        self.scan_thread.start()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def add_file_to_table(self, file_data):
        """Add file to table as it's found"""
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        
        info = file_data['info']
        
        # Filename
        self.result_table.setItem(row, 0, QTableWidgetItem(file_data['name']))
        
        # Relative path
        self.result_table.setItem(row, 1, QTableWidgetItem(file_data['relative']))
        
        # Mode (octal)
        self.result_table.setItem(row, 2, QTableWidgetItem(info['mode']))
        
        # Symbolic mode
        self.result_table.setItem(row, 3, QTableWidgetItem(info['symbolic']))
        
        # Risk level with color
        risk_item = QTableWidgetItem(file_data['risk'])
        risk_item.setTextAlignment(Qt.AlignCenter)
        if file_data['risk'] == 'High':
            risk_item.setBackground(QColor(255, 200, 200))
            risk_item.setForeground(QColor(200, 0, 0))
        elif file_data['risk'] == 'Medium':
            risk_item.setBackground(QColor(255, 230, 200))
            risk_item.setForeground(QColor(200, 100, 0))
        else:
            risk_item.setBackground(QColor(200, 255, 200))
            risk_item.setForeground(QColor(0, 150, 0))
        self.result_table.setItem(row, 4, risk_item)
        
        # Expected permission
        expected = file_data['expected'] if file_data['expected'] else '-'
        self.result_table.setItem(row, 5, QTableWidgetItem(expected))
        
        # File size
        size_str = self.format_size(info['size'])
        self.result_table.setItem(row, 6, QTableWidgetItem(size_str))
        
        # Modified date
        modified_str = info['modified'].strftime('%Y-%m-%d %H:%M')
        self.result_table.setItem(row, 7, QTableWidgetItem(modified_str))
    
    def format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def scan_finished(self, all_files):
        """Called when scan is finished"""
        self.all_files = all_files
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Enable buttons
        self.scan_btn.setEnabled(True)
        self.fix_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)
        self.export_json_btn.setEnabled(True)
        
        # Update statistics
        self.update_statistics()
        
        # Show stats group
        self.stats_group.setVisible(True)
        
        # Log to database
        self.log_scan_to_database()
        
        self.statusBar.showMessage(f"Scan completed: {len(all_files)} files found")
        QMessageBox.information(self, "Scan Complete", f"Found {len(all_files)} files!")
    
    def update_statistics(self):
        """Update statistics labels"""
        total = len(self.all_files)
        high_risk = sum(1 for f in self.all_files if f['risk'] == 'High')
        medium_risk = sum(1 for f in self.all_files if f['risk'] == 'Medium')
        low_risk = sum(1 for f in self.all_files if f['risk'] == 'Low')
        
        self.total_files_label.setText(f"Total File: {total}")
        self.safe_files_label.setText(f"✅ Aman: {low_risk}")
        self.medium_risk_label.setText(f"⚠️ Medium Risk: {medium_risk}")
        self.high_risk_label.setText(f"🔴 High Risk: {high_risk}")
    
    def apply_filter(self):
        """Apply filter to table"""
        filter_text = self.filter_combo.currentText()
        search_text = self.search_input.text().lower()
        
        for row in range(self.result_table.rowCount()):
            show_row = True
            
            # Filter by risk level
            if filter_text != "All":
                risk_item = self.result_table.item(row, 4)
                if risk_item and risk_item.text() != filter_text.replace(" Risk", ""):
                    show_row = False
            
            # Filter by search text
            if search_text and show_row:
                filename = self.result_table.item(row, 0).text().lower()
                if search_text not in filename:
                    show_row = False
            
            self.result_table.setRowHidden(row, not show_row)
    
    def fix_permissions(self):
        """Fix risky permissions"""
        risky_files = [f for f in self.all_files if f['risk'] in ['High', 'Medium']]
        
        if not risky_files:
            QMessageBox.information(self, "No Issues", "No risky permissions found!")
            return
        
        reply = QMessageBox.question(
            self, 
            'Fix Permissions', 
            f"Found {len(risky_files)} files with risky permissions.\n\n"
            "Do you want to fix them automatically?\n"
            "(Files will be set to 644, directories to 755)",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            fixed_count = 0
            errors = []
            
            for file_data in risky_files:
                try:
                    filepath = file_data['path']
                    
                    # Use expected permission if available, otherwise use safe default
                    if file_data['expected']:
                        new_mode = int(file_data['expected'], 8)
                    else:
                        # Safe default: 644 for files
                        new_mode = 0o644
                    
                    os.chmod(filepath, new_mode)
                    fixed_count += 1
                except Exception as e:
                    errors.append(f"{file_data['name']}: {str(e)}")
            
            message = f"Fixed {fixed_count} files!"
            if errors:
                message += f"\n\nErrors ({len(errors)}):\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    message += f"\n... and {len(errors) - 5} more"
            
            QMessageBox.information(self, "Fix Complete", message)
            
            # Re-scan to update table
            self.start_scan()
    
    def export_results(self, format_type):
        """Export results to CSV or JSON"""
        if not self.all_files:
            QMessageBox.warning(self, "No Data", "No scan results to export!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"permission_scan_{timestamp}.{format_type}"
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            f"Save {format_type.upper()} File",
            default_filename,
            f"{format_type.upper()} Files (*.{format_type})"
        )
        
        if not filename:
            return
        
        try:
            if format_type == 'csv':
                self.export_to_csv(filename)
            elif format_type == 'json':
                self.export_to_json(filename)
            
            QMessageBox.information(self, "Export Success", f"Results exported to:\n{filename}")
            self.statusBar.showMessage(f"Exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")
    
    def export_to_csv(self, filename):
        """Export to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Filename', 'Path', 'Mode', 'Symbolic', 'Risk Level', 'Expected', 'Size', 'Modified'])
            
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
                    info['modified'].strftime('%Y-%m-%d %H:%M:%S')
                ])
    
    def export_to_json(self, filename):
        """Export to JSON"""
        export_data = {
            'scan_date': datetime.now().isoformat(),
            'folder': self.path_input.text(),
            'total_files': len(self.all_files),
            'statistics': {
                'high_risk': sum(1 for f in self.all_files if f['risk'] == 'High'),
                'medium_risk': sum(1 for f in self.all_files if f['risk'] == 'Medium'),
                'low_risk': sum(1 for f in self.all_files if f['risk'] == 'Low')
            },
            'files': [
                {
                    'name': f['name'],
                    'path': f['relative'],
                    'mode': f['info']['mode'],
                    'symbolic': f['info']['symbolic'],
                    'risk': f['risk'],
                    'expected': f['expected'],
                    'size': f['info']['size'],
                    'modified': f['info']['modified'].isoformat()
                }
                for f in self.all_files
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
    
    def log_scan_to_database(self):
        """Log scan results to database"""
        try:
            cursor = self.db_conn.cursor()
            
            high_risk = sum(1 for f in self.all_files if f['risk'] == 'High')
            medium_risk = sum(1 for f in self.all_files if f['risk'] == 'Medium')
            low_risk = sum(1 for f in self.all_files if f['risk'] == 'Low')
            
            cursor.execute('''
                INSERT INTO scan_logs (scan_date, folder_path, total_files, high_risk, medium_risk, low_risk)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                self.path_input.text(),
                len(self.all_files),
                high_risk,
                medium_risk,
                low_risk
            ))
            
            self.db_conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
    
    def toggle_dark_mode(self, state):
        """Toggle dark mode"""
        self.dark_mode = state == Qt.Checked
        
        if self.dark_mode:
            # Dark mode palette
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
            dark_palette.setColor(QPalette.ToolTipText, Qt.white)
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, Qt.black)
            
            QApplication.instance().setPalette(dark_palette)
        else:
            # Light mode (default)
            QApplication.instance().setPalette(QApplication.style().standardPalette())
        
        self.statusBar.showMessage(f"{'Dark' if self.dark_mode else 'Light'} mode enabled")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Close database connection
        if hasattr(self, 'db_conn'):
            self.db_conn.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better appearance
    
    window = FilePermissionChecker()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()