from main import FilePermissionChecker
from PyQt5.QtWidgets import QApplication
import sys
import os

# Create dummy app to instantiate class
app = QApplication(sys.argv)
checker = FilePermissionChecker()
# init_database is called in __init__
print("FilePermissionChecker initialized.")
checker.close()
