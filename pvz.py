import time

from typing import List
import win32gui
import win32process
import win32api
import ctypes
import threading

from data import Data, Hack
from run_asm import RunAsm, Reg, wt


class PvzModifier:

    def __init__(self):
        self.OpenProcess = ctypes.windll.kernel32.OpenProcess
        self.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
        self.OpenProcess.restype = wt.HANDLE

        self.ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
        self.WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory

        self.phand = None
        self.data = Data.pvz_goty_1_1_0_1056_zh_2012_06
        self.hwnd = 0
        self.lock = threading.Lock()
        self.asm = RunAsm()

    def wait_for_game(self):
        while 1:
            self.hwnd = hwnd = win32gui.FindWindow(0, "Plants vs. Zombies")
            if hwnd != 0:
                break
            time.sleep(0.01)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        self.phand = self.OpenProcess(0x000f0000 | 0x00100000 | 0xfff, False, pid)
        return 1

    def is_open(self):
        if self.hwnd == 0:
            return False
        if win32gui.IsWindow(self.hwnd):
            return True
        self.hwnd = 0
        return False

    def has_user(self):
        userdata = self.read_offset((self.data.lawn, self.data.user_data))
        return userdata != 0

    def game_ui(self):
        return self.read_offset((self.data.lawn, self.data.game_ui))

    def hack(self, hacks: List[Hack], status):
        for hack in hacks:
            address = hack.address
            if status:
                self.write_memory(address, hack.hack_value, hack.length)
            else:
                self.write_memory(address, hack.reset_value, hack.length)

    def read_memory(self, address, length):
        addr = ctypes.c_ulong()
        self.ReadProcessMemory(self.phand, address, ctypes.byref(addr), length, None)
        return addr.value

    def write_memory(self, address, data, length=4):
        self.lock.acquire()
        data = ctypes.c_ulong(data)
        self.WriteProcessMemory(self.phand, address, ctypes.byref(data), length, None)
        self.lock.release()

    def read_offset(self, offsets, length=4):
        if isinstance(offsets, int):
            offsets = (offsets,)
        addr = 0
        for offset in offsets[:-1]:
            addr = self.read_memory(addr + offset, 4)
        addr = self.read_memory(addr + offsets[-1], length)
        return addr

    def write_offset(self, offsets, data, length):
        if isinstance(offsets, int):
            offsets = (offsets,)
        addr = 0
        for offset in offsets[:-1]:
            addr = self.read_memory(addr + offset, 4)
        addr += offsets[-1]
        self.write_memory(addr, data, length)

    def loop_read_memory(self, start_addr, item_count, item_byte_len):
        return [self.read_memory(start_addr + i * item_byte_len, item_byte_len) for i in range(item_count)]

    def loop_write_memory(self, start_addr, items, item_byte_len):
        for i, data in enumerate(items):
            self.write_memory(start_addr + i * item_byte_len, data, item_byte_len)

    def sun_shine(self, number):
        if isinstance(number, int):
            sun_addr = self.read_offset((self.data.lawn, self.data.board)) + self.data.sun
            self.write_memory(sun_addr, number, 4)

    def money(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            money_addr = self.read_offset((self.data.lawn, self.data.user_data)) + self.data.money
            self.write_memory(money_addr, number // 10, 4)

    def adventure(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            level_addr = self.read_offset((self.data.lawn, self.data.user_data)) + self.data.level
            adventure_level = self.read_offset((self.data.lawn, self.data.board)) + self.data.adventure_level
            self.write_memory(level_addr, number, 4)
            self.write_memory(adventure_level, number, 4)

    def tree_height(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            tree_height_addr = self.read_offset((self.data.lawn, self.data.user_data)) + self.data.tree_height
            self.write_memory(tree_height_addr, number, 4)

    def fertilizer(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            fer_addr = self.read_offset((self.data.lawn, self.data.user_data)) + self.data.fertilizer
            self.write_memory(fer_addr, number + 1000, 4)

    def bug_spray(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            bug_spray_addr = self.read_offset((self.data.lawn, self.data.user_data)) + self.data.bug_spray
            self.write_memory(bug_spray_addr, number + 1000, 4)

    def chocolate(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            chocolate_addr = self.read_offset((self.data.lawn, self.data.user_data)) + self.data.chocolate
            self.write_memory(chocolate_addr, number + 1000, 4)

    def tree_food(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            tree_food_addr = self.read_offset((self.data.lawn, self.data.user_data)) + self.data.tree_food
            self.write_memory(tree_food_addr, number + 1000, 4)

    def vase_transparent(self, status=True):
        self.hack(self.data.vase_transparent, status)

    def no_cool_down(self, status=True):
        self.hack(self.data.no_cool_down, status)

    def auto_collect(self, status=True):
        self.hack(self.data.auto_collect, status)

    def money_not_dec(self, status=True):
        self.hack(self.data.money_not_dec, status)

    def sun_not_dec(self, status=True):
        self.hack(self.data.sun_not_dec, status)

    def chocolate_not_dec(self, status=True):
        self.hack(self.data.chocolate_not_dec, status)

    def fertilizer_not_dec(self, status=True):
        self.hack(self.data.fertilizer_not_dec, status)

    def bug_spray_not_dec(self, status=True):
        self.hack(self.data.bug_spray_not_dec, status)

    def tree_food_not_dec(self, status=True):
        self.hack(self.data.tree_food_not_dec, status)

    def lock_shovel(self, status=True):
        cursor_grab_addr = self.read_offset((self.data.lawn, self.data.board, self.data.cursor)) + self.data.cursor_grab
        if status:
            self.write_memory(cursor_grab_addr, 6, 4)
        else:
            self.write_memory(cursor_grab_addr, 0, 4)
        self.hack(self.data.lock_shovel, status)

    def unlock_limbo_page(self, status=True):
        self.hack(self.data.unlock_limbo_page, status)

    def background_running(self, status=True):
        self.hack(self.data.background_running, status)

    def set_speed_rate(self, rate):
        frame_duration = int(10 // rate)
        self.write_offset((self.data.lawn, self.data.frame_duration), frame_duration, 4)

    def unlock_game(self):
        if not self.has_user():
            return
        user_data = self.read_offset((self.data.lawn, self.data.user_data))
        playthrough_addr = user_data + self.data.playthrough
        playthrough = self.read_memory(playthrough_addr, 4)
        if playthrough < 2:
            self.write_memory(playthrough_addr, 2, 4)
        survival_addr = user_data + self.data.survival
        self.loop_write_memory(survival_addr, [5, 5, 5, 5, 5, 10, 10, 10, 10, 10], 4)
        mini_game_addr = user_data + self.data.mini_game
        puzzle_addr = user_data + self.data.puzzle
        mini_game_flags = self.loop_read_memory(mini_game_addr, 20, 4)
        puzzle_flags = self.loop_read_memory(puzzle_addr, 20, 4)
        self.loop_write_memory(mini_game_addr, map(lambda x: x or 1, mini_game_flags), 4)
        self.loop_write_memory(puzzle_addr, map(lambda x: x or 1, puzzle_flags), 4)
        """8种紫卡与模仿者"""
        twiddydinky_addr = user_data + self.data.twiddydinky
        self.loop_write_memory(twiddydinky_addr, [1] * 9, 4)
        twiddydinky_addr += 9 * 4
        """园艺手套、蘑菇园等"""
        self.loop_write_memory(twiddydinky_addr, [1] * 12, 4)
        twiddydinky_addr += 12 * 4
        """解锁10卡槽"""
        self.write_memory(twiddydinky_addr, 4, 4)
        twiddydinky_addr += 4
        """水池清洁车与屋顶车"""
        self.loop_write_memory(twiddydinky_addr, [1] * 2, 4)
        twiddydinky_addr += 2 * 4
        twiddydinky_addr += 4
        """水族馆"""
        self.write_memory(twiddydinky_addr, 1, 4)
        twiddydinky_addr += 8
        """智慧树、树肥、坚果包扎"""
        self.loop_write_memory(twiddydinky_addr, [1] * 3, 4)

        self.money(999990)
        self.fertilizer(999)
        self.bug_spray(999)
        self.tree_food(999)
        self.chocolate(999)

        if playthrough == 0 and self.game_ui() == 1:
            self.asm.asm_init()
            self.asm.asm_push_byte(1)
            self.asm.asm_mov_exx_dword_ptr(Reg.ECX, self.data.lawn)
            self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.ECX, self.data.game_selector)
            self.asm.asm_call(self.data.call_main_menu)
            self.asm.asm_ret()
            self.asm.asm_code_inject(self.phand)

    def unlock_achievements(self):
        if not self.has_user():
            return
        user_data = self.read_offset((self.data.lawn, self.data.user_data))
        achievement_address = user_data + self.data.achievement
        self.loop_write_memory(achievement_address, [1] * 20, 1)

    def plant_invincible(self, status=True):
        self.hack(self.data.plant_immune_eat, status)
        self.hack(self.data.plant_immune_radius, status)
        self.hack(self.data.plant_immune_projectile, status)
        self.hack(self.data.plant_immune_squish, status)
        self.hack(self.data.plant_immune_jalapeno, status)
        self.hack(self.data.plant_immune_spike_rock, status)
        self.hack(self.data.plant_immune_lob_motion, status)
        self.hack(self.data.plant_immune_square, status)
        self.hack(self.data.plant_immune_row_area, status)

    def plant_weak(self, status=True):
        self.hack(self.data.plant_eat_weak, status)
        self.hack(self.data.plant_projectile_weak, status)
        self.hack(self.data.plant_lob_motion_weak, status)

    def no_crater(self, status=True):
        self.hack(self.data.doom_shroom_no_crater, status)

    def no_ice_trail(self, status=True):
        self.hack(self.data.no_ice_trail, status)

    def overlapping_plant(self, status=True):
        self.hack(self.data.overlapping_plant, status)
        self.hack(self.data.overlapping_plant_preview, status)
        self.hack(self.data.overlapping_plant_iz, status)

    def mushroom_awake(self, status=True):
        self.hack(self.data.mushrooms_awake, status)

    def zombie_invincible(self, status=True):
        self.hack(self.data.zombie_immune_body_damage, status)
        self.hack(self.data.zombie_immune_helm_damage, status)
        self.hack(self.data.zombie_immune_shield_damage, status)
        self.hack(self.data.zombie_immune_burn_crumble, status)
        self.hack(self.data.zombie_immune_radius, status)
        self.hack(self.data.zombie_immune_burn_row, status)
        self.hack(self.data.zombie_immune_chomper, status)
        self.hack(self.data.zombie_immune_mind_control, status)
        self.hack(self.data.zombie_immune_blow_away, status)
        self.hack(self.data.zombie_immune_splash, status)
        self.hack(self.data.zombie_immune_lawn_mower, status)

    def zombie_weak(self, status=True):
        self.hack(self.data.zombie_body_weak, status)
        self.hack(self.data.zombie_helm_weak, status)
        self.hack(self.data.zombie_shield_weak, status)
        self.hack(self.data.zombie_can_burn_crumble, status)


if __name__ == '__main__':
    game = PvzModifier()
    game.wait_for_game()
