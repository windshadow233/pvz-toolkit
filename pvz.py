import time

from typing import List
import win32gui
import win32process
import win32api
import ctypes
import threading

from address import Data, Hack
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
        lawn, user_data = self.data.recursively_get_attrs(['lawn', 'user_data'])
        userdata = self.read_offset((lawn, user_data))
        return userdata != 0

    def game_ui(self):
        lawn, game_ui = self.data.recursively_get_attrs(['lawn', 'game_ui'])
        return self.read_offset((lawn, game_ui))

    def scene(self):
        ui = self.game_ui()
        if ui == 2 or ui == 3:
            lawn, board, scene = self.data.recursively_get_attrs(['lawn', 'board', 'scene'])
            scene = self.read_offset((lawn, board, scene), 4)
        else:
            scene = -1
        return scene

    def get_row_count(self):
        scene = self.scene()
        if scene == 2 or scene == 3:
            return 6
        elif scene == 0 or scene == 1 or scene == 4 or scene == 5:
            return 5
        return -1

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
            lawn, board, sun = self.data.recursively_get_attrs(['lawn', 'board', 'sun'])
            self.write_offset((lawn, board, sun), number, 4)

    def money(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn, user_data, money = self.data.recursively_get_attrs(['lawn', 'user_data', 'money'])
            self.write_offset((lawn, user_data, money), number // 10, 4)

    def adventure(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn = self.data.lawn
            user_data, level = lawn.recursively_get_attrs(['user_data', 'level'])
            board, adventure_level = lawn.recursively_get_attrs(['board', 'adventure_level'])
            self.write_offset((lawn, user_data, level), number, 4)
            self.write_offset((lawn, board, adventure_level), number, 4)

    def tree_height(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn, user_data, tree_height = self.data.recursively_get_attrs(['lawn', 'user_data', 'tree_height'])
            self.write_offset((lawn, user_data, tree_height), number, 4)

    def fertilizer(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn, user_data, fertilizer = self.data.recursively_get_attrs(['lawn', 'user_data', 'fertilizer'])
            self.write_offset((lawn, user_data, fertilizer), number + 1000, 4)

    def bug_spray(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn, user_data, bug_spray = self.data.recursively_get_attrs(['lawn', 'user_data', 'bug_spray'])
            self.write_offset((lawn, user_data, bug_spray), number + 1000, 4)

    def chocolate(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn, user_data, chocolate = self.data.recursively_get_attrs(['lawn', 'user_data', 'chocolate'])
            self.write_offset((lawn, user_data. chocolate), number + 1000, 4)

    def tree_food(self, number):
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn, user_data, tree_food = self.data.recursively_get_attrs(['lawn', 'user_data', 'tree_food'])
            self.write_offset((lawn, user_data, tree_food), number + 1000, 4)

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
        lawn, board, cursor, cursor_grab = self.data.recursively_get_attrs(['lawn', 'board', 'cursor', 'cursor_grab'])
        if status:
            self.write_offset((lawn, board, cursor, cursor_grab), 6, 4)
        else:
            self.write_offset((lawn, board, cursor, cursor_grab), 0, 4)
        self.hack(self.data.lock_shovel, status)

    def unlock_limbo_page(self, status=True):
        self.hack(self.data.unlock_limbo_page, status)

    def background_running(self, status=True):
        self.hack(self.data.background_running, status)

    def set_speed_rate(self, rate):
        new_duration = int(10 // rate)
        lawn, frame_duration = self.data.recursively_get_attrs(['lawn', 'frame_duration'])
        self.write_offset((lawn, frame_duration), new_duration, 4)

    def unlock_game(self):
        if not self.has_user():
            return
        lawn, user_data, playthrough = self.data.recursively_get_attrs(['lawn', 'user_data', 'playthrough'])
        user_data_addr = self.read_offset((lawn, user_data))
        playthrough_addr = user_data_addr + playthrough
        playthrough = self.read_memory(playthrough_addr, 4)
        if playthrough < 2:
            self.write_memory(playthrough_addr, 2, 4)
        survival_addr = user_data_addr + user_data.survival
        self.loop_write_memory(survival_addr, [5, 5, 5, 5, 5, 10, 10, 10, 10, 10], 4)
        mini_game_addr = user_data_addr + user_data.mini_game
        puzzle_addr = user_data_addr + user_data.puzzle
        mini_game_flags = self.loop_read_memory(mini_game_addr, 20, 4)
        puzzle_flags = self.loop_read_memory(puzzle_addr, 20, 4)
        self.loop_write_memory(mini_game_addr, map(lambda x: x or 1, mini_game_flags), 4)
        self.loop_write_memory(puzzle_addr, map(lambda x: x or 1, puzzle_flags), 4)
        """8种紫卡与模仿者"""
        twiddydinky_addr = user_data_addr + user_data.twiddydinky
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
            lawn, game_selector = self.data.recursively_get_attrs(['lawn', 'game_selector'])
            call_main_menu = lawn.call_main_menu
            self.asm.asm_init()
            self.asm.asm_push_byte(1)
            self.asm.asm_mov_exx_dword_ptr(Reg.ECX, lawn)
            self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.ECX, game_selector)
            self.asm.asm_mov_exx_exx(Reg.ESI, Reg.ECX)
            self.asm.asm_call(call_main_menu)
            self.asm.asm_ret()
            self.lock.acquire()
            self.asm.asm_code_inject(self.phand)
            self.lock.release()

    def unlock_achievements(self):
        if not self.has_user():
            return
        lawn, user_data, achievement = self.data.recursively_get_attrs(['lawn', 'user_data', 'achievement'])
        achievement_address = self.read_offset((lawn, user_data)) + achievement
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
        if status:
            self.set_mushroom_awake()

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

    def asm_put_plant(self, plant_type, row, col, imitator):
        lawn, board = self.data.recursively_get_attrs(['lawn', 'board'])
        if imitator:
            self.asm.asm_push_dword(plant_type)
            self.asm.asm_push_dword(0x30)
        else:
            self.asm.asm_push_dword(0xffffffff)
            self.asm.asm_push_dword(plant_type)
        self.asm.asm_mov_exx(Reg.EAX, row)
        self.asm.asm_push_dword(col)
        self.asm.asm_mov_exx_dword_ptr(Reg.EDI, lawn)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EDI, board)
        self.asm.asm_push_exx(Reg.EDI)
        self.asm.asm_call(0x418d70)

    def put_plant(self, plant_type, row, col, imitator):
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        row_count = self.get_row_count()
        col_count = 8 if plant_type == 47 else 9
        width = 2 if plant_type == 47 else 1
        if row >= row_count or col >= col_count:
            return
        self.asm.asm_init()
        if row == -1 and col == -1:
            for r in range(row_count):
                for c in range(0, col_count, width):
                    self.asm_put_plant(plant_type, r, c, imitator)
        elif row == -1 and col != -1:
            for r in range(row_count):
                self.asm_put_plant(plant_type, r, col, imitator)
        elif row != -1 and col == -1:
            for c in range(0, col_count, width):
                self.asm_put_plant(plant_type, row, c, imitator)
        else:
            self.asm_put_plant(plant_type, row, col, imitator)
        self.asm.asm_ret()
        self.lock.acquire()
        self.asm.asm_code_inject(self.phand)
        self.lock.release()

    def set_mushroom_awake(self):
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        lawn, board, plant_count_max = self.data.recursively_get_attrs(['lawn', 'board', 'plant_count_max'])
        plants = board.plants
        plants_addr = self.read_offset((lawn, board, plants))
        plant_size = 0x14c
        plant_dead = plants.dead
        plant_squished = plants.squished
        plant_asleep = plants.asleep
        plant_count_max = self.read_offset((lawn, board, plant_count_max), 4)
        self.asm.asm_init()
        for i in range(plant_count_max):
            addr = plants_addr + plant_size * i
            is_dead = self.read_memory(addr + plant_dead, 1)
            is_squished = self.read_memory(addr + plant_squished, 1)
            is_asleep = self.read_memory(addr + plant_asleep, 1)
            if is_dead or is_squished or not is_asleep:
                continue
            self.asm.asm_mov_exx(Reg.EDI, addr)
            self.asm.asm_push_byte(0)
            self.asm.asm_call(self.data.call_set_plant_sleeping)
        self.asm.asm_ret()
        self.lock.acquire()
        self.asm.asm_code_inject(self.phand)
        self.lock.release()

    def set_lawn_mower(self, status):
        ui = self.game_ui()
        if ui != 3:
            return
        lawn, board, lawn_mower_count_max = self.data.recursively_get_attrs(['lawn', 'board', 'lawn_mower_count_max'])
        lawn_mower = board.lawn_mowers
        lawn_mower_dead = lawn_mower.dead
        lawn_mower_count_max = self.read_offset((lawn, board, lawn_mower_count_max))
        lawn_mowers_addr = self.read_offset((lawn, board, lawn_mower))
        lawn_mower_size = 0x48
        if status == 2:
            self.hack(self.data.init_lawn_mowers, True)
        self.asm.asm_init()
        for i in range(lawn_mower_count_max):
            addr = lawn_mowers_addr + i * lawn_mower_size
            is_dead = self.read_memory(addr + lawn_mower_dead, 1)
            if is_dead:
                continue
            if status == 0:
                self.asm.asm_mov_exx(Reg.ESI, addr)
                self.asm.asm_call(self.data.call_start_lawn_mower)
            else:
                self.asm.asm_mov_exx(Reg.EAX, addr)
                self.asm.asm_call(self.data.call_delete_lawn_mower)
        if status == 2:
            self.asm.asm_mov_exx_dword_ptr(Reg.EAX, lawn)
            self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EAX, board)
            self.asm.asm_push_exx(Reg.EAX)
            self.asm.asm_call(self.data.call_restore_lawn_mower)
        self.asm.asm_ret()
        self.lock.acquire()
        self.asm.asm_code_inject(self.phand)
        self.lock.release()
        if status == 2:
            self.hack(self.data.init_lawn_mowers, False)


if __name__ == '__main__':
    game = PvzModifier()
    game.wait_for_game()
