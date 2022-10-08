import time

from typing import List
import win32gui
import win32process
import win32api
import ctypes
import threading

from data import Address, Hack


class PvzModifier:

    def __init__(self):
        self.kernel32 = ctypes.windll.LoadLibrary('kernel32.dll')
        self.phand = None
        self.data = Address.pvz_goty_1_1_0_1056_zh_2012_06
        self.game_base = 0x00400000
        self.hwnd = 0
        self.lock = threading.Lock()

    def wait_for_game(self):
        while 1:
            self.hwnd = hwnd = win32gui.FindWindow(0, "Plants vs. Zombies")
            if hwnd != 0:
                break
            time.sleep(0.01)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        self.phand = win32api.OpenProcess(0x000f0000 | 0x00100000 | 0xfff, False, pid)
        return 1

    def is_open(self):
        if self.hwnd == 0:
            return False
        if win32gui.IsWindow(self.hwnd):
            return True
        self.hwnd = 0
        return False

    def hack(self, hacks: List[Hack], status):
        for hack in hacks:
            address = hack.address
            if status:
                self.write_memory(address, hack.hack_value, hack.length)
            else:
                self.write_memory(address, hack.reset_value, hack.length)

    def read_memory(self, address, length):
        addr = ctypes.c_ulong()
        self.kernel32.ReadProcessMemory(int(self.phand), address, ctypes.byref(addr), length, None)
        return addr.value

    def write_memory(self, address, data, length):
        self.lock.acquire()
        data = ctypes.c_ulong(data)
        self.kernel32.WriteProcessMemory(int(self.phand), address, ctypes.byref(data), length, None)
        self.lock.release()

    def read_offset(self, offsets, length):
        if isinstance(offsets, int):
            offsets = (offsets,)
        addr = 0
        for offset in offsets:
            addr = self.read_memory(addr + offset, length)
        return addr

    def write_offset(self, offsets, data, length):
        if isinstance(offsets, int):
            offsets = (offsets,)
        addr = 0
        for offset in offsets[:-1]:
            addr = self.read_memory(addr + offset, length)
        addr += offsets[-1]
        self.write_memory(addr, data, length)

    def sun_shine(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.data.lawn, self.data.board, self.data.sun), number, 4)
        else:
            return self.read_offset((self.data.lawn, self.data.board, self.data.sun), 4)

    def money(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.data.lawn, self.data.user_data, self.data.money), number // 10, 4)
        else:
            return self.read_offset((self.data.lawn, self.data.user_data, self.data.money), 4) * 10

    def adventure(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.data.lawn, self.data.user_data, self.data.level), number, 4)
            self.write_offset((self.data.lawn, self.data.board, self.data.adventure_level), number, 4)
        else:
            return self.read_offset((self.data.lawn, self.data.user_data, self.data.level), 4)

    def tree_height(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.data.lawn, self.data.user_data, self.data.tree_height), number, 4)
        else:
            return self.read_offset((self.data.lawn, self.data.user_data, self.data.tree_height), 4)

    def fertilizer(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.data.lawn, self.data.user_data, self.data.fertilizer), number + 1000, 4)
        else:
            number = self.read_offset((self.data.lawn, self.data.user_data, self.data.fertilizer), 4)
            if number == 0:
                return 0
            return number - 1000

    def bug_spray(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.data.lawn, self.data.user_data, self.data.bug_spray), number + 1000, 4)
        else:
            number = self.read_offset((self.data.lawn, self.data.user_data, self.data.bug_spray), 4)
            if number == 0:
                return 0
            return number - 1000

    def chocolate(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.data.lawn, self.data.user_data, self.data.chocolate), number + 1000, 4)
        else:
            number = self.read_offset((self.data.lawn, self.data.user_data, self.data.chocolate), 4)
            if number == 0:
                return 0
            return number - 1000

    def tree_food(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.data.lawn, self.data.user_data, self.data.tree_food), number + 1000, 4)
        else:
            number = self.read_offset((self.data.lawn, self.data.user_data, self.data.tree_food), 4)
            if number == 0:
                return 0
            return number - 1000

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
        if status:
            self.write_offset((self.data.lawn, self.data.board, self.data.cursor, self.data.cursor_grab), 6, 4)
        else:
            self.write_offset((self.data.lawn, self.data.board, self.data.cursor, self.data.cursor_grab), 0, 4)
        self.hack(self.data.lock_shovel, status)

    def unlock_limbo_page(self, status=True):
        self.hack(self.data.unlock_limbo_page, status)

    def background_running(self, status=True):
        self.hack(self.data.background_running, status)


if __name__ == '__main__':
    game = PvzModifier()
