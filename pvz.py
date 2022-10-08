import time

import win32gui
import win32process
import win32api
import ctypes
import threading


class PvzModifier:

    def __init__(self):
        self.kernel32 = ctypes.windll.LoadLibrary('kernel32.dll')
        self.phand = None
        self.lawn = 0x755e0c
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
            self.write_offset((self.lawn, 0x868, 0x5578), number, 4)
        else:
            return self.read_offset((self.lawn, 0x868, 0x5578), 4)

    def money(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.lawn, 0x950, 0x50), number // 10, 4)
        else:
            return self.read_offset((self.lawn, 0x950, 0x50), 4) * 10

    def adventure(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.lawn, 0x950, 0x4c), number, 4)
        return self.read_offset((self.lawn, 0x950, 0x4c), 4)

    def tree_height(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.lawn, 0x950, 0x11c), number, 4)
        else:
            return self.read_offset((self.lawn, 0x950, 0x11c), 4)

    def fertilizer(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.lawn, 0x950, 0x220), number + 1000, 4)
        else:
            number = self.read_offset((self.lawn, 0x950, 0x220), 4)
            if number == 0:
                return 0
            return number - 1000

    def bug_spray(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.lawn, 0x950, 0x224), number + 1000, 4)
        else:
            number = self.read_offset((self.lawn, 0x950, 0x224), 4)
            if number == 0:
                return 0
            return number - 1000

    def chocolate(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.lawn, 0x950, 0x250), number + 1000, 4)
        else:
            number = self.read_offset((self.lawn, 0x950, 0x250), 4)
            if number == 0:
                return 0
            return number - 1000

    def tree_food(self, number=None):
        if isinstance(number, int):
            self.write_offset((self.lawn, 0x950, 0x258), number + 1000, 4)
        else:
            number = self.read_offset((self.lawn, 0x950, 0x258), 4)
            if number == 0:
                return 0
            return number - 1000

    def vase_transparent(self, status=True):
        if status:
            self.write_memory(self.game_base + 0x59c1a, 0x0033b866, 4)
        else:
            self.write_memory(self.game_base + 0x59c1a, 0x047ec085, 4)

    def plant_instant_cool_down(self, status=True):
        """
        植物无需冷却
        :param status: True 开启; False关闭
        """
        if status:
            self.write_memory(self.game_base + 0x9ce02, 0x9090, 2)
        else:
            self.write_memory(self.game_base + 0x9ce02, 0x167e, 2)

    def auto_collect(self, status=True):
        """
        自动收集
        :param status: True 开启; False关闭
        """

        if status:
            self.write_memory(self.game_base + 0x3cc72, 0x09eb, 2)
        else:
            self.write_memory(self.game_base + 0x3cc72, 0x0975, 2)

    def money_not_dec(self, status=True):
        if status:
            self.write_memory(self.game_base + 0xa2451, 0x909090, 3)
        else:
            self.write_memory(self.game_base + 0xa2451, 0x504129, 3)

    def sun_shine_not_dec(self, status=True):
        if status:
            self.write_memory(self.game_base + 0x27694, 0x9090, 2)
        else:
            self.write_memory(self.game_base + 0x27694, 0xf32b, 2)

    def chocolate_not_dec(self, status=True):
        if status:
            self.write_memory(self.game_base + 0x134a17, 0x909090909090, 6)
            self.write_memory(self.game_base + 0x134995, 0x909090909090, 6)
        else:
            self.write_memory(self.game_base + 0x134a17, 0x0000025088ff, 6)
            self.write_memory(self.game_base + 0x134995, 0x0000025088ff, 6)

    def fertilizer_not_dec(self, status=True):
        if status:
            self.write_memory(self.game_base + 0x134d7b, 0x909090909090, 6)
        else:
            self.write_memory(self.game_base + 0x134d7b, 0x0000022088ff, 6)

    def bug_spray_not_dec(self, status=True):
        if status:
            self.write_memory(self.game_base + 0x134e73, 0x909090909090, 6)
        else:
            self.write_memory(self.game_base + 0x134e73, 0x0000022488ff, 6)

    def tree_food_not_dec(self, status=True):
        if status:
            self.write_memory(self.game_base + 0x3885d, 0x909090909090, 6)
        else:
            self.write_memory(self.game_base + 0x3885d, 0x0000025888ff, 6)

    def lock_shovel(self, status=True):
        if status:
            self.write_offset((self.lawn, 0x868, 0x150, 0x30), 6, 4)
            self.write_memory(self.game_base + 0x1e36e, 0x39, 1)
        else:
            self.write_offset((self.lawn, 0x868, 0x150, 0x30), 0, 4)
            self.write_memory(self.game_base + 0x1e36e, 0x89, 1)

    def unlock_limbo_page(self, status=True):
        if status:
            self.write_memory(self.game_base + 0x3935a, 0x38, 1)
        else:
            self.write_memory(self.game_base + 0x3935a, 0x88, 1)

    def background_running(self, status=True):
        if status:
            self.write_memory(self.game_base + 0x224919, 0x00eb, 2)
        else:
            self.write_memory(self.game_base + 0x224919, 0x4074, 2)


if __name__ == '__main__':
    game = PvzModifier()
