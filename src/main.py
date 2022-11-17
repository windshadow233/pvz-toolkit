import sys
import win32event
import win32api

from ui_functions import *


if __name__ == '__main__':
    mutex = win32event.CreateMutex(None, True, "PvZ Toolkit Python")
    if win32api.GetLastError() == 0:
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        app = QApplication(sys.argv)
        window = PvzToolkit()
        window.show()
        sys.exit(app.exec())
