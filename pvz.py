import time

from typing import List
import win32gui
import win32process
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
        self.asm = RunAsm(self.lock)

    def wait_for_game(self):
        while 1:
            self.hwnd = hwnd = win32gui.FindWindow(0, "Plants vs. Zombies")
            if hwnd != 0:
                break
            time.sleep(0.01)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        self.phand = self.OpenProcess(0x000f0000 | 0x00100000 | 0xfff, False, pid)
        return 1

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

    def asm_code_inject(self):
        self.hack(self.data.block_main_loop, True)
        time.sleep(self.get_frame_duration() * 2 / 1000)
        self.asm.asm_code_inject(self.phand)
        self.hack(self.data.block_main_loop, False)

    def is_open(self):
        if self.hwnd == 0:
            return False
        if win32gui.IsWindow(self.hwnd):
            return True
        self.hwnd = 0
        return False

    def has_user(self):
        if not self.is_open():
            return
        lawn_offset, user_data_offset = self.data.recursively_get_attrs(['lawn', 'user_data'])
        userdata = self.read_offset((lawn_offset, user_data_offset))
        return userdata != 0

    def get_frame_duration(self):
        if not self.is_open():
            return 10
        lawn_offset, frame_duration_offset = self.data.recursively_get_attrs(['lawn', 'frame_duration'])
        return self.read_offset((lawn_offset, frame_duration_offset), 4)

    def game_mode(self):
        if not self.is_open():
            return
        lawn_offset, game_mode_offset = self.data.recursively_get_attrs(['lawn', 'game_mode'])
        return self.read_offset((lawn_offset, game_mode_offset))

    def game_ui(self):
        if not self.is_open():
            return
        lawn_offset, game_ui_offset = self.data.recursively_get_attrs(['lawn', 'game_ui'])
        return self.read_offset((lawn_offset, game_ui_offset))

    def get_scene(self):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui == 2 or ui == 3:
            lawn_offset, board_offset, scene_offset = self.data.recursively_get_attrs(['lawn', 'board', 'scene'])
            scene = self.read_offset((lawn_offset, board_offset, scene_offset), 4)
        else:
            scene = -1
        return scene

    def get_row_count(self):
        if not self.is_open():
            return
        scene = self.get_scene()
        if scene == 2 or scene == 3:
            return 6
        elif scene == 0 or scene == 1 or scene == 4 or scene == 5:
            return 5
        return -1

    def _refresh_main_page(self):
        lawn_offset, game_selector_offset = self.data.recursively_get_attrs(['lawn', 'game_selector'])
        self.asm.asm_init()
        self.asm.asm_push_byte(1)
        self.asm.asm_mov_exx_dword_ptr(Reg.ECX, lawn_offset)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.ECX, game_selector_offset)
        self.asm.asm_mov_exx_exx(Reg.ESI, Reg.ECX)
        self.asm.asm_call(self.data.call_sync_profile)
        self.asm.asm_ret()
        self.asm_code_inject()

    def hack(self, hacks: List[Hack], status):
        for hack in hacks:
            address = hack.address
            if status:
                self.write_memory(address, hack.hack_value, hack.length)
            else:
                self.write_memory(address, hack.reset_value, hack.length)

    def sun_shine(self, number):
        if not self.is_open():
            return
        if isinstance(number, int):
            lawn_offset, board_offset, sun_offset = self.data.recursively_get_attrs(['lawn', 'board', 'sun'])
            self.write_offset((lawn_offset, board_offset, sun_offset), number, 4)

    def money(self, number):
        if not self.is_open():
            return
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn_offset, user_data_offset, money_offset = self.data.recursively_get_attrs(['lawn', 'user_data', 'money'])
            self.write_offset((lawn_offset, user_data_offset, money_offset), number // 10, 4)

    def adventure(self, number):
        if not self.is_open():
            return
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn_offset = self.data.lawn
            user_data_offset, level_offset = lawn_offset.recursively_get_attrs(['user_data', 'level'])
            board_offset, adventure_level_offset = lawn_offset.recursively_get_attrs(['board', 'adventure_level'])
            self.write_offset((lawn_offset, user_data_offset, level_offset), number, 4)
            self.write_offset((lawn_offset, board_offset, adventure_level_offset), number, 4)
            self._refresh_main_page()

    def tree_height(self, number):
        if not self.is_open():
            return
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn_offset, user_data_offset, tree_height_offset = self.data.recursively_get_attrs(['lawn', 'user_data', 'tree_height'])
            self.write_offset((lawn_offset, user_data_offset, tree_height_offset), number, 4)

    def fertilizer(self, number):
        if not self.is_open():
            return
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn_offset, user_data_offset, fertilizer_offset = self.data.recursively_get_attrs(['lawn', 'user_data', 'fertilizer'])
            self.write_offset((lawn_offset, user_data_offset, fertilizer_offset), number + 1000, 4)

    def bug_spray(self, number):
        if not self.is_open():
            return
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn_offset, user_data_offset, bug_spray_offset = self.data.recursively_get_attrs(['lawn', 'user_data', 'bug_spray'])
            self.write_offset((lawn_offset, user_data_offset, bug_spray_offset), number + 1000, 4)

    def chocolate(self, number):
        if not self.is_open():
            return
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn_offset, user_data_offset, chocolate_offset = self.data.recursively_get_attrs(['lawn', 'user_data', 'chocolate'])
            self.write_offset((lawn_offset, user_data_offset, chocolate_offset), number + 1000, 4)

    def tree_food(self, number):
        if not self.is_open():
            return
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn_offset, user_data_offset, tree_food_offset = self.data.recursively_get_attrs(['lawn', 'user_data', 'tree_food'])
            self.write_offset((lawn_offset, user_data_offset, tree_food_offset), number + 1000, 4)

    def vase_transparent(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.vase_transparent, status)

    def no_cool_down(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.no_cool_down, status)

    def auto_collect(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.auto_collect, status)

    def money_not_dec(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.money_not_dec, status)

    def sun_not_dec(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.sun_not_dec, status)

    def chocolate_not_dec(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.chocolate_not_dec, status)

    def fertilizer_not_dec(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.fertilizer_not_dec, status)

    def bug_spray_not_dec(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.bug_spray_not_dec, status)

    def tree_food_not_dec(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.tree_food_not_dec, status)

    def lock_shovel(self, status=True):
        if not self.is_open():
            return
        lawn_offset, board_offset, cursor_offset, cursor_grab_offset = self.data.recursively_get_attrs(['lawn', 'board', 'cursor', 'cursor_grab'])
        if status:
            self.write_offset((lawn_offset, board_offset, cursor_offset, cursor_grab_offset), 6, 4)
        else:
            self.write_offset((lawn_offset, board_offset, cursor_offset, cursor_grab_offset), 0, 4)
        self.hack(self.data.lock_shovel, status)

    def unlock_limbo_page(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.unlock_limbo_page, status)

    def background_running(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.background_running, status)

    def set_speed_rate(self, rate):
        if not self.is_open():
            return
        new_duration = int(10 // rate)
        lawn_offset, frame_duration_offset = self.data.recursively_get_attrs(['lawn', 'frame_duration'])
        self.write_offset((lawn_offset, frame_duration_offset), new_duration, 4)

    def unlock_game(self):
        if not self.is_open():
            return
        if not self.has_user():
            return
        lawn_offset, user_data_offset, playthrough_offset = self.data.recursively_get_attrs(['lawn', 'user_data', 'playthrough'])
        user_data = self.read_offset((lawn_offset, user_data_offset))
        playthrough_addr = user_data + playthrough_offset
        playthrough = self.read_memory(playthrough_addr, 4)
        if playthrough < 2:
            self.write_memory(playthrough_addr, 2, 4)
        survival_addr = user_data + user_data_offset.survival
        self.loop_write_memory(survival_addr, [5, 5, 5, 5, 5, 10, 10, 10, 10, 10], 4)
        mini_game_addr = user_data + user_data_offset.mini_game
        puzzle_addr = user_data + user_data_offset.puzzle
        mini_game_flags = self.loop_read_memory(mini_game_addr, 20, 4)
        puzzle_flags = self.loop_read_memory(puzzle_addr, 20, 4)
        self.loop_write_memory(mini_game_addr, map(lambda x: x or 1, mini_game_flags), 4)
        self.loop_write_memory(puzzle_addr, map(lambda x: x or 1, puzzle_flags), 4)
        """8种紫卡与模仿者"""
        twiddydinky_addr = user_data + user_data_offset.twiddydinky
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
            self._refresh_main_page()

    def unlock_achievements(self):
        if not self.is_open():
            return
        if not self.has_user():
            return
        lawn_offset, user_data_offset, achievement_offset = self.data.recursively_get_attrs(['lawn', 'user_data', 'achievement'])
        achievement_addr = self.read_offset((lawn_offset, user_data_offset)) + achievement_offset
        self.loop_write_memory(achievement_addr, [1] * 20, 1)

    def plant_invincible(self, status=True):
        if not self.is_open():
            return
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
        if not self.is_open():
            return
        self.hack(self.data.plant_eat_weak, status)
        self.hack(self.data.plant_projectile_weak, status)
        self.hack(self.data.plant_lob_motion_weak, status)

    def no_crater(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.doom_shroom_no_crater, status)

    def no_ice_trail(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.no_ice_trail, status)

    def overlapping_plant(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.overlapping_plant, status)
        self.hack(self.data.overlapping_plant_preview, status)
        self.hack(self.data.overlapping_plant_iz, status)

    def mushroom_awake(self, status=True):
        if not self.is_open():
            return
        self.hack(self.data.mushrooms_awake, status)
        if status:
            self.set_mushroom_awake()

    def zombie_invincible(self, status=True):
        if not self.is_open():
            return
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
        if not self.is_open():
            return
        self.hack(self.data.zombie_body_weak, status)
        self.hack(self.data.zombie_helm_weak, status)
        self.hack(self.data.zombie_shield_weak, status)
        self.hack(self.data.zombie_can_burn_crumble, status)

    def _asm_put_plant(self, plant_type, row, col, imitator):
        lawn_offset, board_offset = self.data.recursively_get_attrs(['lawn', 'board'])
        if imitator:
            self.asm.asm_push_dword(plant_type)
            self.asm.asm_push_dword(0x30)
        else:
            self.asm.asm_push_dword(0xffffffff)
            self.asm.asm_push_dword(plant_type)
        self.asm.asm_mov_exx(Reg.EAX, row)
        self.asm.asm_push_dword(col)
        self.asm.asm_mov_exx_dword_ptr(Reg.EDI, lawn_offset)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EDI, board_offset)
        self.asm.asm_push_exx(Reg.EDI)
        self.asm.asm_call(self.data.call_put_plant)

    def put_plant(self, plant_type, row, col, imitator):
        if not self.is_open():
            return
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
                    self._asm_put_plant(plant_type, r, c, imitator)
        elif row == -1 and col != -1:
            for r in range(row_count):
                self._asm_put_plant(plant_type, r, col, imitator)
        elif row != -1 and col == -1:
            for c in range(0, col_count, width):
                self._asm_put_plant(plant_type, row, c, imitator)
        else:
            self._asm_put_plant(plant_type, row, col, imitator)
        self.asm.asm_ret()
        self.asm_code_inject()

    def set_mushroom_awake(self):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        lawn_offset, board_offset, plant_count_max_offset = self.data.recursively_get_attrs(['lawn', 'board', 'plant_count_max'])
        plants_offset = board_offset.plants
        plants_addr = self.read_offset((lawn_offset, board_offset, plants_offset))
        plant_struct_size = 0x14c
        plant_dead = plants_offset.dead
        plant_squished = plants_offset.squished
        plant_asleep = plants_offset.asleep
        plant_count_max = self.read_offset((lawn_offset, board_offset, plant_count_max_offset), 4)
        self.asm.asm_init()
        for i in range(plant_count_max):
            addr = plants_addr + plant_struct_size * i
            is_dead = self.read_memory(addr + plant_dead, 1)
            is_squished = self.read_memory(addr + plant_squished, 1)
            is_asleep = self.read_memory(addr + plant_asleep, 1)
            if is_dead or is_squished or not is_asleep:
                continue
            self.asm.asm_mov_exx(Reg.EDI, addr)
            self.asm.asm_push_byte(0)
            self.asm.asm_call(self.data.call_set_plant_sleeping)
        self.asm.asm_ret()
        self.asm_code_inject()

    def set_lawn_mower(self, status):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 3:
            return
        lawn_offset, board_offset, lawn_mower_count_max_offset = self.data.recursively_get_attrs(['lawn', 'board', 'lawn_mower_count_max'])
        lawn_mower_offset = board_offset.lawn_mowers
        lawn_mower_dead_offset = lawn_mower_offset.dead
        lawn_mower_count_max = self.read_offset((lawn_offset, board_offset, lawn_mower_count_max_offset))
        lawn_mowers_addr = self.read_offset((lawn_offset, board_offset, lawn_mower_offset))
        lawn_mower_struct_size = 0x48
        if status == 2:
            self.hack(self.data.init_lawn_mowers, True)
        self.asm.asm_init()
        for i in range(lawn_mower_count_max):
            addr = lawn_mowers_addr + i * lawn_mower_struct_size
            is_dead = self.read_memory(addr + lawn_mower_dead_offset, 1)
            if is_dead:
                continue
            if status == 0:
                self.asm.asm_mov_exx(Reg.ESI, addr)
                self.asm.asm_call(self.data.call_start_lawn_mower)
            else:
                self.asm.asm_mov_exx(Reg.EAX, addr)
                self.asm.asm_call(self.data.call_delete_lawn_mower)
        if status == 2:
            self.asm.asm_mov_exx_dword_ptr(Reg.EAX, lawn_offset)
            self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EAX, board_offset)
            self.asm.asm_push_exx(Reg.EAX)
            self.asm.asm_call(self.data.call_restore_lawn_mower)
        self.asm.asm_ret()
        self.asm_code_inject()
        if status == 2:
            self.hack(self.data.init_lawn_mowers, False)

    def _asm_put_zombie(self, zombie_type, row, col):
        lawn_offset, board_offset, challenge_offset = self.data.recursively_get_attrs(['lawn', 'board', 'challenge'])
        self.asm.asm_push_dword(col)
        self.asm.asm_push_dword(zombie_type)
        self.asm.asm_mov_exx(Reg.EAX, row)
        self.asm.asm_mov_exx_dword_ptr(Reg.ECX, lawn_offset)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.ECX, board_offset)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.ECX, challenge_offset)
        self.asm.asm_call(self.data.call_put_zombie)

    def put_zombie(self, zombie_type, row, col):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        if zombie_type == 25:
            lawn_offset, board_offset = self.data.recursively_get_attrs(['lawn', 'board'])
            zombie_count_max = board_offset.zombie_count_max
            board = self.read_offset((lawn_offset, board_offset), 4)
            zombie_count_max = self.read_memory(board + zombie_count_max, 4)
            zombies_offset, type_offset = board_offset.recursively_get_attrs(['zombies', 'type'])
            zombie_struct_size = 0x168
            zombies_addr = self.read_memory(board + zombies_offset, 4)
            for i in range(zombie_count_max):
                type_ = self.read_memory(zombies_addr + i * zombie_struct_size + type_offset, 4)
                if type_ == 25:  # 多个僵王会出bug
                    return
            self.asm.asm_init()
            self.asm.asm_mov_exx_dword_ptr(Reg.EAX, lawn_offset)
            self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EAX, board_offset)
            self.asm.asm_push_dword(0)
            self.asm.asm_push_dword(25)
            self.asm.asm_call(self.data.call_put_zombie_in_row)
            self.asm.asm_ret()
            self.asm_code_inject()
            return
        row_count = self.get_row_count()
        if row >= row_count:
            return
        col_count = 9
        self.asm.asm_init()
        if row == -1 and col == -1:
            for r in range(row_count):
                for c in range(col_count):
                    self._asm_put_zombie(zombie_type, r, c)
        elif row == -1 and col != -1:
            for r in range(row_count):
                self._asm_put_zombie(zombie_type, r, col)
        elif row != -1 and col == -1:
            for c in range(col_count):
                self._asm_put_zombie(zombie_type, row, c)
        else:
            self._asm_put_zombie(zombie_type, row, col)
        self.asm.asm_ret()
        self.asm_code_inject()


if __name__ == '__main__':
    game = PvzModifier()
    game.wait_for_game()
