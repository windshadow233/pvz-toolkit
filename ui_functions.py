import os
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
        comboboxes = filter(lambda x: 'comboBox' in x[0], self.__dict__.items())
        for _, box in comboboxes:
            box.setStyleSheet("QAbstractItemView::item {height: 40px;}")
            box.setView(QListView())
        self.game = PvzModifier()

        def check_game_status():
            status = False
            while 1:
                if not self.game.is_open():
                    self.label_9.setStyleSheet("color:red")
                    self.label_9.setText("❌未检测到游戏进程")
                    self.game.wait_for_game()
                    status = True
                    self.set_status()
                else:
                    if status:
                        self.label_9.setStyleSheet("color:green")
                        self.label_9.setText("✅已检测到游戏进程")
                        status = False
                time.sleep(0.1)
        self._check_game_status_thread = threading.Thread(target=check_game_status)
        self._check_game_status_thread.setDaemon(True)
        self._check_game_status_thread.start()

    def set_status(self):
        self.money_not_dec()
        self.sun_not_dec()
        self.chocolate_not_dec()
        self.fertilizer_not_dec()
        self.bug_spray_not_dec()
        self.tree_food_not_dec()
        self.auto_collect()
        self.no_cool_down()
        self.vase_transparent()
        self.lock_shovel()
        self.unlock_limbo_page()
        self.background_running()
        self.plant_invincible()
        self.plant_weak()
        self.no_crater()
        self.no_ice_trail()
        self.overlapping_plant()
        self.mushroom_awake()
        self.zombie_invincible()
        self.zombie_weak()
        self.no_fog()
        self.chomper_no_cool_down()

    def open_download_url(self):
        QDesktopServices.openUrl(QUrl("https://pan.baidu.com/s/14OCAGDsNGcgynJXGK4NPfQ?pwd=fnpq"))

    def sun_shine(self):
        text = self.lineEdit.text()
        self.game.sun_shine(int(text))

    def money(self):
        text = self.lineEdit_2.text()
        self.game.money(int(text))

    def tree_height(self):
        text = self.lineEdit_3.text()
        self.game.tree_height(int(text))

    def fertilizer(self):
        text = self.lineEdit_4.text()
        self.game.fertilizer(int(text))

    def chocolate(self):
        text = self.lineEdit_5.text()
        self.game.chocolate(int(text))

    def bug_spray(self):
        text = self.lineEdit_6.text()
        self.game.bug_spray(int(text))

    def tree_food(self):
        text = self.lineEdit_7.text()
        self.game.tree_food(int(text))

    def auto_collect(self):
        self.game.auto_collect(self.checkBox.isChecked())

    def no_cool_down(self):
        self.game.no_cool_down(self.checkBox_2.isChecked())

    def vase_transparent(self):
        self.game.vase_transparent(self.checkBox_3.isChecked())

    def money_not_dec(self):
        self.game.money_not_dec(self.checkBox_4.isChecked())

    def sun_not_dec(self):
        self.game.sun_not_dec(self.checkBox_5.isChecked())

    def chocolate_not_dec(self):
        self.game.chocolate_not_dec(self.checkBox_6.isChecked())

    def fertilizer_not_dec(self):
        self.game.fertilizer_not_dec(self.checkBox_7.isChecked())

    def bug_spray_not_dec(self):
        self.game.bug_spray_not_dec(self.checkBox_8.isChecked())

    def tree_food_not_dec(self):
        self.game.tree_food_not_dec(self.checkBox_9.isChecked())

    def lock_shovel(self):
        self.game.lock_shovel(self.checkBox_10.isChecked())

    def adventure(self):
        a = int(self.spinBox.value()) - 1
        b = int(self.spinBox_2.value())
        self.game.adventure(a * 10 + b)

    def unlock_limbo_page(self):
        self.game.unlock_limbo_page(self.checkBox_11.isChecked())

    def background_running(self):
        self.game.background_running(self.checkBox_12.isChecked())

    def open_user_file_folder(self):
        os.startfile("C:\\ProgramData\\PopCap Games\\PlantsVsZombies\\userdata")

    def set_speed_rate(self):
        if not self.game.is_open():
            return
        rate = float(self.comboBox.currentText()[:-1])
        self.game.set_speed_rate(rate)

    def unlock_game(self):
        self.game.unlock_game()

    def unlock_achievements(self):
        self.game.unlock_achievements()

    def plant_invincible(self):
        if self.checkBox_16.isChecked():
            self.checkBox_16.setChecked(False)
            self.game.plant_weak(False)
        self.game.plant_invincible(self.checkBox_13.isChecked())

    def no_crater(self):
        self.game.no_crater(self.checkBox_14.isChecked())

    def no_ice_trail(self):
        self.game.no_ice_trail(self.checkBox_15.isChecked())

    def plant_weak(self):
        if self.checkBox_13.isChecked():
            self.checkBox_13.setChecked(False)
            self.game.plant_invincible(False)
        self.game.plant_weak(self.checkBox_16.isChecked())

    def overlapping_plant(self):
        self.game.overlapping_plant(self.checkBox_17.isChecked())

    def mushroom_awake(self):
        self.game.mushroom_awake(self.checkBox_18.isChecked())

    def zombie_invincible(self):
        if self.checkBox_20.isChecked():
            self.checkBox_20.setChecked(False)
            self.game.zombie_weak(False)
        self.game.zombie_invincible(self.checkBox_19.isChecked())

    def zombie_weak(self):
        if self.checkBox_19.isChecked():
            self.checkBox_19.setChecked(False)
            self.game.zombie_invincible(False)
        self.game.zombie_weak(self.checkBox_20.isChecked())

    def put_plant(self):
        row = self.comboBox_2.currentIndex() - 1
        col = self.comboBox_3.currentIndex() - 1
        plant_type = self.comboBox_4.currentIndex()
        imitator = self.checkBox_21.isChecked()
        self.game.put_plant(plant_type, row, col, imitator)

    def set_lawn_mower(self):
        index = self.comboBox_5.currentIndex()
        if index == 0:
            return
        self.game.set_lawn_mower(self.comboBox_5.currentIndex() - 1)
        self.comboBox_5.setCurrentIndex(0)

    def put_zombie(self):
        row = self.comboBox_2.currentIndex() - 1
        col = self.comboBox_3.currentIndex() - 1
        zombie_type = self.comboBox_6.currentIndex()
        self.game.put_zombie(zombie_type, row, col)

    def no_fog(self):
        self.game.no_fog(self.checkBox_22.isChecked())

    def delete_items(self):
        item_index = self.comboBox_7.currentIndex()
        if item_index == 0:
            self.game.delete_all_plants()
        elif item_index == 1:
            self.game.kill_all_zombies()
        elif item_index == 2:
            self.game.delete_grid_items({1})
        elif item_index == 3:
            self.game.delete_grid_items({3})
        elif item_index == 4:
            self.game.delete_grid_items({11})

    def put_lily(self):
        index = self.comboBox_8.currentIndex()
        if index == 0:
            return
        to_col = self.comboBox_8.currentIndex() - 1
        self.game.put_lily(0, to_col)
        self.comboBox_8.setCurrentIndex(0)

    def put_flowerpot(self):
        index = self.comboBox_9.currentIndex()
        if index == 0:
            return
        to_col = self.comboBox_9.currentIndex() - 1
        self.game.put_flowerpot(0, to_col)
        self.comboBox_9.setCurrentIndex(0)

    def play_music(self):
        music_id = self.comboBox_10.currentIndex() + 1
        self.game.set_music(music_id)

    def set_scene(self):
        scene_id = self.comboBox_11.currentIndex()
        self.game.set_scene(scene_id)

    def chomper_no_cool_down(self):
        self.game.chomper_no_cool_down(self.checkBox_23.isChecked())

