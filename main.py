import sys

from ui_functions import *


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PvzTool()
    window.show()
    sys.exit(app.exec())
