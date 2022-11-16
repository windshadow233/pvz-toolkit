import os
import random
import json

import win32con
from PyQt5.Qt import *
from PyQt5.QtGui import QDesktopServices

from pvz import *
from pvztoolkit import *


class PvzToolkit(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(PvzToolkit, self).__init__()
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
        self.tableView.setModel(QStandardItemModel(4, 3))
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.game = PvzModifier()
        self.lineup_codes = {}
        with open('lineup/lineup.json', 'r', encoding='utf-8') as f:
            self.lineup_codes.update(json.loads(f.read()))
        with open('lineup/lineup-diy.json', 'r', encoding='utf-8') as f:
            self.lineup_codes.update(json.loads(f.read()))
        names = filter(lambda x: 'PE' in x, self.lineup_codes)
        self.comboBox_17.clear()
        self.comboBox_17.addItems(names)

        def check_game_status():
            status = False
            while 1:
                if not self.game.is_open():
                    self.label_9.setStyleSheet("color:red")
                    self.label_9.setText("❌未检测到游戏进程")
                    self.game.wait_for_game()
                    self.tableView.setModel(QStandardItemModel(4, 3))
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

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.game.is_open():
            reply = QMessageBox.question(
                self,
                "温馨提示", "此窗口关闭时，为正常管理内存空间，所有子弹变换效果将被重置，而其他开启的辅助功能将正常保留，是否退出？",
                buttons=QMessageBox.Yes | QMessageBox.No,
                defaultButton=QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.game.reset_bullets()
                event.accept()
            else:
                event.ignore()

    def set_status(self):
        for _, checkbox in filter(lambda x: 'checkBox' in x[0], self.__dict__.items()):
            if checkbox.isChecked():
                checkbox.toggled.emit(True)
        self.set_speed_rate()

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
        try:
            os.startfile("C:\\ProgramData\\PopCap Games\\PlantsVsZombies\\userdata")
        except FileNotFoundError:
            QMessageBox.warning(self, '温馨提示', '找不到存档目录，请检查一下~')

    def set_speed_rate(self):
        if not self.game.is_open():
            return
        rate = float(self.comboBox.currentText()[:-1])
        self.game.set_speed_rate(rate)

    def unlock_game(self):
        self.game.unlock_game()

    def unlock_achievements(self):
        self.game.unlock_achievements()

    def no_crater(self):
        self.game.no_crater(self.checkBox_14.isChecked())

    def no_ice_trail(self):
        self.game.no_ice_trail(self.checkBox_15.isChecked())

    def plant_invincible(self):
        is_checked = self.checkBox_13.isChecked()
        if is_checked and self.checkBox_16.isChecked():
            self.checkBox_16.setChecked(False)
        self.game.plant_invincible(is_checked)

    def plant_weak(self):
        is_checked = self.checkBox_16.isChecked()
        if is_checked and self.checkBox_13.isChecked():
            self.checkBox_13.setChecked(False)
        self.game.plant_weak(is_checked)

    def plant_anywhere(self):
        self.game.plant_anywhere(self.checkBox_17.isChecked())

    def mushroom_awake(self):
        self.game.mushroom_awake(self.checkBox_18.isChecked())

    def zombie_invincible(self):
        is_checked = self.checkBox_19.isChecked()
        if is_checked and self.checkBox_20.isChecked():
            self.checkBox_20.setChecked(False)
        self.game.zombie_invincible(is_checked)

    def zombie_weak(self):
        is_checked = self.checkBox_20.isChecked()
        if is_checked and self.checkBox_19.isChecked():
            self.checkBox_19.setChecked(False)
        self.game.zombie_weak(is_checked)

    def put_plant(self):
        row = self.comboBox_2.currentIndex() - 1
        col = self.comboBox_3.currentIndex() - 1
        plant_type = self.comboBox_4.currentIndex()
        if plant_type == 48:
            imitator = 1
        else:
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
        if zombie_type == 25:
            scene = self.game.get_scene()
            if scene == 2 or scene == 3:
                QMessageBox.information(self, "温馨提示", "泳池与雾夜模式不支持召唤僵王", QMessageBox.Ok)
                return
        self.game.put_zombie(zombie_type, row, col)

    def no_fog(self):
        self.game.no_fog(self.checkBox_22.isChecked())

    def delete_items(self):
        index = self.comboBox_7.currentIndex()
        if index == 0:
            return
        if index == 1:
            self.game.delete_all_plants()
        elif index == 2:
            self.game.kill_all_zombies()
        elif index == 3:
            self.game.delete_grid_items({1})
        elif index == 4:
            self.game.delete_grid_items({3})
        elif index == 5:
            self.game.delete_grid_items({11})
        self.comboBox_7.setCurrentIndex(0)

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
        index = self.comboBox_11.currentIndex()
        self.game.set_scene(index)

    def chomper_no_cool_down(self):
        self.game.chomper_no_cool_down(self.checkBox_23.isChecked())

    def put_grave(self):
        row = self.comboBox_2.currentIndex() - 1
        col = self.comboBox_3.currentIndex() - 1
        self.game.put_grave(row, col)

    def put_ladder(self):
        row = self.comboBox_2.currentIndex() - 1
        col = self.comboBox_3.currentIndex() - 1
        self.game.put_ladder(row, col)

    def put_rake(self):
        row = self.comboBox_2.currentIndex() - 1
        col = self.comboBox_3.currentIndex() - 1
        self.game.put_rake(row, col)

    def screen_shot(self):
        self.game.screen_shot()

    def stop_spawning(self):
        self.game.stop_spawning(self.checkBox_24.isChecked())

    def plants_growup(self):
        self.game.plants_instant_growup(self.checkBox_25.isChecked())

    def zombie_not_explode(self):
        self.game.zombie_not_explode(self.checkBox_26.isChecked())

    def zombie_stop(self):
        self.game.zombie_stop(self.checkBox_27.isChecked())

    def lock_butter(self):
        self.game.lock_butter(self.checkBox_28.isChecked())

    def change_bullet(self):
        from_bullet = [0, 1, 2, 3, 4, 5, 7, 8, 10, 11, 12][self.comboBox_13.currentIndex()]
        to_bullet = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12][self.comboBox_12.currentIndex()]
        if to_bullet == 9 and from_bullet in {2, 3, 5, 10, 12}:
            reply = QMessageBox.question(
                self,
                "温馨提示", "投掷类植物无法使用篮球对僵尸造成伤害，是否继续？",
                buttons=QMessageBox.Yes | QMessageBox.No,
                defaultButton=QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        if from_bullet == 11 and to_bullet != 11:
            reply = QMessageBox.question(
                self,
                "温馨提示", "建议不要变换玉米炮弹~是否继续？",
                buttons=QMessageBox.Yes | QMessageBox.No,
                defaultButton=QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        self.game.change_bullet(from_bullet, to_bullet)
        types = self.game.data.bullet_types
        items = [f"{types[f]} ⇒ {types[t]}" for f, t in self.game.changed_bullets.get('items', {}).items()]
        model = QStandardItemModel(4, 3)
        for index, item in enumerate(items):
            row = index // 3
            col = index % 3
            model.setItem(row, col, QStandardItem(item))
        self.tableView.setModel(model)

    def reset_bullets(self):
        self.game.reset_bullets()
        self.tableView.setModel(QStandardItemModel(4, 3))

    def add_garden_plant(self):
        plant_type = self.comboBox_14.currentIndex()
        direction = self.comboBox_15.currentIndex() - 1
        color = self.comboBox_16.currentIndex() + 1
        if direction == -1:
            direction = random.randint(0, 1)
        ret = self.game.add_garden_plant(plant_type, direction, color)
        if ret == 0:
            QMessageBox.information(self, '温馨提示', '您的花园过于拥挤，请先留出一些空位再继续吧~')

    def generate_lineup_code(self):
        lineup = self.game.get_lineup()
        if lineup is None:
            return
        s = str(lineup)
        self.textBrowser.setText(s)

    def copy_lineup_code(self):
        s = self.textBrowser.toPlainText()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, s)
        win32clipboard.CloseClipboard()

    def paste_lineup_code(self):
        try:
            win32clipboard.OpenClipboard()
            s = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            self.textBrowser.setText(s)
        except:
            QMessageBox.warning(self, '温馨提示', '请复制一个字符串再进行导入')

    def set_lineup(self):
        s = self.textBrowser.toPlainText()
        try:
            lineup = Lineup.from_str(s)
            self.game.set_lineup(lineup)
        except:
            QMessageBox.warning(self, '温馨提示', '阵型代码有误！')

    def update_lineup_list(self):
        scene = self.comboBox_11.currentIndex()
        scene_str = ['DE', 'NE', 'PE', 'FE', 'RE', 'ME'][scene]
        names = filter(lambda x: scene_str in x, self.lineup_codes)
        self.comboBox_17.clear()
        self.comboBox_17.addItems(names)

    def set_lineup_code(self):
        name = self.comboBox_17.currentText()
        if name:
            code = self.lineup_codes[name]
            self.textBrowser.setText(code)

    def free_planting(self):
        self.game.free_planting(self.checkBox_29.isChecked())

    def change_garden_cursor(self):
        index = self.comboBox_18.currentIndex()
        cursor_type = [0, 9, 10, 11, 12, 13, 15, 17][index]
        self.game.change_garden_cursor(cursor_type)

    def set_slot_plant(self):
        slot_id = self.comboBox_19.currentIndex() - 1
        plant_type = self.comboBox_20.currentIndex()
        is_imitator = self.checkBox_30.isChecked()
        self.game.set_slot_plant(plant_type, slot_id, is_imitator)

    def put_vase(self):
        plant_type = self.comboBox_22.currentIndex()
        zombie_type = self.comboBox_24.currentIndex()
        vase_content_type = self.comboBox_26.currentIndex()
        if vase_content_type == 1 and plant_type == 0x30:
            reply = QMessageBox.warning(
                self,
                '温馨提示',
                '不建议在罐子中放置模仿者（种植会闪退），是否继续？',
                buttons=QMessageBox.Yes | QMessageBox.No,
                defaultButton=QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        row = self.comboBox_21.currentIndex() - 1
        col = self.comboBox_23.currentIndex() - 1
        vase_type = self.comboBox_25.currentIndex() + 3
        sun_shine_count = self.spinBox_3.value()
        self.game.put_vase(row, col, vase_type, vase_content_type, plant_type, zombie_type, sun_shine_count)

    def delete_vases(self):
        self.game.delete_grid_items({7})
