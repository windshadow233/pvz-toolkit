import os
import sys

from PyQt5.Qt import *
from PyQt5.QtGui import QDesktopServices

from pvz import *
from pvztool import *


class PvzTool(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(PvzTool, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.lineEdit.setValidator(QIntValidator(0, 9990))
        self.lineEdit_2.setValidator(QIntValidator(0, 999990))
        self.lineEdit_3.setValidator(QIntValidator(0, 10000))
        self.lineEdit_4.setValidator(QIntValidator(0, 9999))
        self.lineEdit_5.setValidator(QIntValidator(0, 9999))
        self.lineEdit_6.setValidator(QIntValidator(0, 9999))
        self.lineEdit_7.setValidator(QIntValidator(0, 9999))
        self.setFixedSize(self.width(), self.height())
        self.game = PvzModifier()

        def check_game_status():
            status = False
            while 1:
                if not self.game.is_open():
                    self.label_9.setStyleSheet("color:red")
                    self.label_9.setText("未检测到游戏进程")
                    self.game.wait_for_game()
                    status = True
                    self.set_status()
                else:
                    if status:
                        self.label_9.setStyleSheet("color:green")
                        self.label_9.setText("已检测到游戏进程")
                        status = False
                time.sleep(0.001)
        self._check_game_status_thread = threading.Thread(target=check_game_status)
        self._check_game_status_thread.setDaemon(True)
        self._check_game_status_thread.start()

    def set_status(self):
        self.money_not_dec()
        self.sun_shine_not_dec()
        self.chocolate_not_dec()
        self.fertilizer_not_dec()
        self.bug_spray_not_dec()
        self.tree_food_not_dec()
        self.auto_collect()
        self.plant_instant_cool_down()
        self.vase_transparent()
        self.lock_shovel()
        self.unlock_limbo_page()
        self.background_running()

    def open_download_url(self):
        QDesktopServices.openUrl(QUrl("https://pan.baidu.com/s/14OCAGDsNGcgynJXGK4NPfQ?pwd=fnpq"))

    def sun_shine(self):
        if not self.game.is_open():
            return
        text = self.lineEdit.text()
        self.game.sun_shine(int(text))

    def money(self):
        if not self.game.is_open():
            return
        text = self.lineEdit_2.text()
        self.game.money(int(text))

    def tree_height(self):
        if not self.game.is_open():
            return
        text = self.lineEdit_3.text()
        self.game.tree_height(int(text))

    def fertilizer(self):
        if not self.game.is_open():
            return
        text = self.lineEdit_4.text()
        self.game.fertilizer(int(text))

    def chocolate(self):
        if not self.game.is_open():
            return
        text = self.lineEdit_5.text()
        self.game.chocolate(int(text))

    def bug_spray(self):
        if not self.game.is_open():
            return
        text = self.lineEdit_6.text()
        self.game.bug_spray(int(text))

    def tree_food(self):
        if not self.game.is_open():
            return
        text = self.lineEdit_7.text()
        self.game.tree_food(int(text))

    def auto_collect(self):
        if not self.game.is_open():
            return
        self.game.auto_collect(self.checkBox.isChecked())

    def plant_instant_cool_down(self):
        if not self.game.is_open():
            return
        self.game.plant_instant_cool_down(self.checkBox_2.isChecked())

    def vase_transparent(self):
        if not self.game.is_open():
            return
        self.game.vase_transparent(self.checkBox_3.isChecked())

    def money_not_dec(self):
        if not self.game.is_open():
            return
        self.game.money_not_dec(self.checkBox_4.isChecked())

    def sun_shine_not_dec(self):
        if not self.game.is_open():
            return
        self.game.sun_shine_not_dec(self.checkBox_5.isChecked())

    def chocolate_not_dec(self):
        if not self.game.is_open():
            return
        self.game.chocolate_not_dec(self.checkBox_6.isChecked())

    def fertilizer_not_dec(self):
        if not self.game.is_open():
            return
        self.game.fertilizer_not_dec(self.checkBox_7.isChecked())

    def bug_spray_not_dec(self):
        if not self.game.is_open():
            return
        self.game.bug_spray_not_dec(self.checkBox_8.isChecked())

    def tree_food_not_dec(self):
        if not self.game.is_open():
            return
        self.game.tree_food_not_dec(self.checkBox_9.isChecked())

    def lock_shovel(self):
        if not self.game.is_open():
            return
        self.game.lock_shovel(self.checkBox_10.isChecked())

    def adventure(self):
        if not self.game.is_open():
            return
        a = int(self.spinBox.value()) - 1
        b = int(self.spinBox_2.value())
        self.game.adventure(a * 10 + b)

    def unlock_limbo_page(self):
        if not self.game.is_open():
            return
        self.game.unlock_limbo_page(self.checkBox_11.isChecked())

    def background_running(self):
        if not self.game.is_open():
            return
        self.game.background_running(self.checkBox_12.isChecked())

    def open_user_file_folder(self):
        os.startfile("C:\\ProgramData\\PopCap Games\\PlantsVsZombies\\userdata")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PvzTool()
    window.show()
    sys.exit(app.exec())

