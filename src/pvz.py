import time

from typing import List
import win32gui
import win32process
import win32clipboard
import ctypes
import threading
import copy

from data import Data, Hack
from asm_inject import AsmInjector, Reg
from lineup import Lineup


may_asleep = [0, 0, 0, 0, 0, 0, 0, 0,
              1, 1, 1, 0, 1, 1, 1, 1,
              0, 0, 0, 0, 0, 0, 0, 0,
              1, 0, 0, 0, 0, 0, 0, 1,
              0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 1, 0, 0, 0, 0, 0, 1]


class PvzModifier:

    def __init__(self):
        self.OpenProcess = ctypes.windll.kernel32.OpenProcess

        self.ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
        self.WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory

        self.phand = None
        self.data = Data.pvz_goty_1_1_0_1056_zh_2012_06
        self.hwnd = 0
        self.lock = threading.Lock()
        self.asm = AsmInjector(self.lock)
        self.changed_bullets = {}

    def wait_for_game(self):
        while 1:
            self.hwnd = hwnd = win32gui.FindWindow(0, "Plants vs. Zombies")
            if hwnd != 0:
                break
            time.sleep(0.1)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        self.phand = self.OpenProcess(0x000f0000 | 0x00100000 | 0xfff, False, pid)
        return 1

    def read_memory(self, address, length=4):
        addr = ctypes.c_ulonglong()
        self.ReadProcessMemory(self.phand, address, ctypes.byref(addr), length, None)
        return addr.value

    def write_memory(self, address, data, length=4):
        self.lock.acquire()
        data = ctypes.c_ulonglong(data)
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

    def asm_code_execute(self, addr=None):
        self.hack(self.data.block_main_loop, True)
        time.sleep(self.get_frame_duration() * 2 / 1000)
        addr = addr or self.asm.asm_alloc(self.phand, self.asm.length)
        if addr:
            if self.asm.asm_code_inject(self.phand, addr):
                self.asm.asm_execute(self.phand, addr)
            self.asm.asm_free(self.phand, addr)
        self.hack(self.data.block_main_loop, False)

    def is_open(self):
        if self.hwnd == 0:
            return False
        if win32gui.IsWindow(self.hwnd):
            return True
        self.hwnd = 0
        self.changed_bullets.clear()
        return False

    def hack(self, hacks: List[Hack], status):
        for hack in hacks:
            address = hack.address
            if status:
                self.write_memory(address, hack.hack_value, hack.length)
            else:
                self.write_memory(address, hack.reset_value, hack.length)

    def has_user(self):
        if not self.is_open():
            return
        userdata = self.read_offset((self.data.lawn, self.data.lawn.user_data))
        return userdata != 0

    def get_frame_duration(self):
        if not self.is_open():
            return 10
        return self.read_offset((self.data.lawn, self.data.lawn.frame_duration), 4)

    def game_mode(self):
        if not self.is_open():
            return
        return self.read_offset((self.data.lawn, self.data.lawn.game_mode))

    def game_ui(self):
        if not self.is_open():
            return
        return self.read_offset((self.data.lawn, self.data.lawn.game_ui))

    def get_scene(self):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui == 2 or ui == 3:
            lawn_offset, board_offset, scene_offset = self.data.recursively_get_attrs(['lawn', 'board', 'scene'])
            scene = self.read_offset((lawn_offset, board_offset, scene_offset), 4)
        else:
            scene = 0xff
        return scene

    def set_scene(self, scene):
        if not self.is_open():
            return
        pre_scene = self.get_scene()
        if pre_scene > 5 or pre_scene < 0:
            return
        if scene > 5 or scene < 0:
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        self.delete_all_plants()
        self.delete_grid_items({1, 2, 3, 11})
        lawn_offset, board_offset, block_type_offset = self.data.recursively_get_attrs(['lawn', 'board', 'block_type'])
        row_type_offset = board_offset.row_type
        board_addr = self.read_offset((lawn_offset, board_offset), 4)
        block_type_addr = board_addr + block_type_offset
        row_type_addr = board_addr + row_type_offset
        scene_offset = board_offset.scene
        lawn_mower_count = self.read_memory(board_addr + board_offset.lawn_mower_count, 4)
        if lawn_mower_count > 0:
            self.set_lawn_mower(1)
        self.asm.asm_init()
        self.asm.asm_mov_exx_dword_ptr(Reg.ESI, lawn_offset)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.ESI, board_offset)
        self.asm.asm_add_list([0xc7, 0x86])
        self.asm.asm_add_dword(scene_offset)
        self.asm.asm_add_dword(scene)
        self.asm.asm_call(self.data.call_pick_background)
        self.asm.asm_ret()
        self.asm_code_execute()
        if scene in {0, 1, 4, 5}:
            block_types, row_types = [1, 1, 1, 1, 1, 2] * 9, [1, 1, 1, 1, 1, 0]
        else:
            block_types, row_types = [1, 1, 3, 3, 1, 1] * 9, [1, 1, 2, 2, 1, 1]
        self.loop_write_memory(block_type_addr, block_types, 4)
        self.loop_write_memory(row_type_addr, row_types, 4)

        if lawn_mower_count > 0:
            self.set_lawn_mower(2)
        if ui == 3:
            if pre_scene != scene:
                music_id = scene + 1
                if music_id == 6:
                    music_id = 2
                self.set_music(music_id)

        if pre_scene != 2 and pre_scene != 3:
            return
        if scene == 2 or scene == 3:
            return
        particle_system_struct_size = 0x2c
        lawn_offset, animations_offset, unnamed_offset, particle_system_offset = self.data.recursively_get_attrs(['lawn', 'animations', 'unnamed', 'particle_system'])
        particle_system_addr = self.read_offset((lawn_offset, animations_offset, unnamed_offset, particle_system_offset))
        particle_system_count_max_offset = unnamed_offset.particle_system_count_max
        particle_system_count_max = self.read_offset((lawn_offset, animations_offset, unnamed_offset, particle_system_count_max_offset))
        particle_type = particle_system_offset.type
        particle_dead = particle_system_offset.dead
        self.asm.asm_init()
        for i in range(particle_system_count_max):
            addr = particle_system_addr + i * particle_system_struct_size
            type_ = self.read_memory(addr + particle_type, 4)
            is_dead = self.read_memory(addr + particle_dead, 1)
            if not is_dead and type_ == 34:
                self.asm.asm_push_dword(addr)
                self.asm.asm_call(self.data.call_delete_particle_system)
        self.asm.asm_mov_exx_dword_ptr(Reg.EAX, lawn_offset)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EAX, board_offset)
        self.asm.asm_add_list([0xc7, 0x80])
        self.asm.asm_add_dword(board_offset.particle_systems)
        self.asm.asm_add_dword(0)
        self.asm.asm_ret()
        self.asm_code_execute()

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
        self.asm_code_execute()

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
            current_level = self.read_offset((lawn_offset, user_data_offset, level_offset), 4)
            if current_level != number:
                self.write_offset((lawn_offset, user_data_offset, level_offset), number, 4)
                self.write_offset((lawn_offset, board_offset, adventure_level_offset), number, 4)
                ui = self.game_ui()
                if ui == 1:
                    self._refresh_main_page()

    def tree_height(self, number):
        if not self.is_open():
            return
        if not self.has_user():
            return
        if isinstance(number, int):
            lawn_offset, user_data_offset, tree_height_offset = self.data.recursively_get_attrs(['lawn', 'user_data', 'tree_height'])
            if self.game_mode() == 50:
                self.write_offset((lawn_offset, user_data_offset, tree_height_offset), number - 1, 4)
                board_offset, challenge_offset = lawn_offset.recursively_get_attrs(['board', 'challenge'])
                self.asm.asm_init()
                self.asm.asm_mov_exx_dword_ptr(Reg.EDI, lawn_offset)
                self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EDI, board_offset)
                self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EDI, challenge_offset)
                self.asm.asm_call(self.data.call_wisdom_tree)
                self.asm.asm_ret()
                self.asm_code_execute()
            else:
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

    def set_cursor(self, cursor_type):
        lawn_offset, board_offset, cursor_offset, cursor_grab_offset = self.data.recursively_get_attrs(
            ['lawn', 'board', 'cursor', 'cursor_grab'])
        self.write_offset((lawn_offset, board_offset, cursor_offset, cursor_grab_offset), cursor_type, 4)

    def lock_shovel(self, status=True):
        if not self.is_open():
            return
        scene = self.get_scene()
        if scene < 0 or scene > 5:
            return
        cursor_type = 6 if status else 0
        self.set_cursor(cursor_type)
        self.hack(self.data.lock_cursor, status)

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
        self.fertilizer(9999)
        self.bug_spray(9999)
        self.tree_food(9999)
        self.chocolate(9999)

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

    def _get_plant_addresses(self):
        lawn_offset, board_offset, plant_count_max_offset = self.data.recursively_get_attrs(['lawn', 'board', 'plant_count_max'])
        plants_offset = board_offset.plants
        plant_dead = plants_offset.dead
        board = self.read_offset([lawn_offset, board_offset])
        plants_addr = self.read_memory(board + plants_offset, 4)
        plant_struct_size = 0x14c
        plant_squished = plants_offset.squished
        plant_count_max = self.read_memory(board + plant_count_max_offset, 4)
        for i in range(plant_count_max):
            addr = plants_addr + plant_struct_size * i
            is_dead = self.read_memory(addr + plant_dead, 1)
            is_squished = self.read_memory(addr + plant_squished, 1)
            if is_dead or is_squished:
                continue
            yield addr

    def _get_zombie_addresses(self):
        lawn_offset, board_offset, zombie_count_max_offset = self.data.recursively_get_attrs(['lawn', 'board', 'zombie_count_max'])
        zombies_offset = board_offset.zombies
        zombie_dead = zombies_offset.dead
        board = self.read_offset([lawn_offset, board_offset])
        zombies_addr = self.read_memory(board + zombies_offset, 4)
        zombie_struct_size = 0x168
        zombie_count_max = self.read_memory(board + zombie_count_max_offset, 4)
        for i in range(zombie_count_max):
            addr = zombies_addr + i * zombie_struct_size
            is_dead = self.read_memory(addr + zombie_dead, 1)
            if not is_dead:
                yield addr

    def _get_grid_items(self, types):
        lawn_offset, board_offset, grid_item_max_offset = self.data.recursively_get_attrs(['lawn', 'board', 'grid_item_count_max'])
        grid_items_offset = board_offset.grid_items
        grid_items_addr = self.read_offset((lawn_offset, board_offset, grid_items_offset))
        grid_item_struct_size = 0xec
        grid_item_type = grid_items_offset.type
        grid_item_dead = grid_items_offset.dead
        grid_item_count_max = self.read_offset((lawn_offset, board_offset, grid_item_max_offset), 4)
        for i in range(grid_item_count_max):
            addr = grid_items_addr + grid_item_struct_size * i
            item_type = self.read_memory(addr + grid_item_type, 4)
            is_dead = self.read_memory(addr + grid_item_dead, 1)
            if item_type in types and not is_dead:
                yield addr

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
        if imitator:
            self.asm.asm_mov_exx_dword_ptr(Reg.ECX, lawn_offset)
            self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.ECX, board_offset)
            self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.ECX, board_offset.plants)
            self.asm.asm_mov_exx_dword_ptr(Reg.EBX, lawn_offset)
            self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EBX, board_offset)
            self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EBX, board_offset.plant_next_pos)
            self.asm.asm_add_list([0x69, 0xdb, 0x4c, 0x01, 0x00, 0x00])
            self.asm.asm_add_list([0x01, 0xd9])
            self.asm.asm_push_exx(Reg.ECX)
            self.asm.asm_mov_exx_exx(Reg.ESI, Reg.EAX)
            self.asm.asm_call(self.data.call_put_imitator_plant)
            self.asm.asm_pop_exx(Reg.ECX)
            self.asm.asm_mov_exx_exx(Reg.EAX, Reg.ECX)

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
        self.asm_code_execute()

    def set_mushroom_awake(self):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        plant_asleep = self.data.lawn.board.plants.asleep
        addrs = self._get_plant_addresses()
        self.asm.asm_init()
        for addr in addrs:
            is_asleep = self.read_memory(addr + plant_asleep, 1)
            if is_asleep:
                self.asm.asm_mov_exx(Reg.EDI, addr)
                self.asm.asm_push_byte(0)
                self.asm.asm_call(self.data.call_set_plant_sleeping)
        self.asm.asm_ret()
        self.asm_code_execute()

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
        self.asm_code_execute()
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
            scene = self.get_scene()
            if scene == 2 or scene == 3:  # 泳池模式放僵王会闪退
                return
            self.asm.asm_init()
            self.asm.asm_mov_exx_dword_ptr(Reg.EAX, self.data.lawn)
            self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EAX, self.data.lawn.board)
            self.asm.asm_push_dword(0)
            self.asm.asm_push_dword(25)
            self.asm.asm_call(self.data.call_put_zombie_in_row)
            self.asm.asm_ret()
            self.asm_code_execute()
            self.set_music(12)
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
        self.asm_code_execute()

    def no_fog(self, status):
        if not self.is_open():
            return
        self.hack(self.data.no_fog, status)

    def delete_all_plants(self):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        if self.game_mode() == 43:
            return
        addrs = self._get_plant_addresses()
        self.asm.asm_init()
        for addr in addrs:
            self.asm.asm_push_dword(addr)
            self.asm.asm_call(self.data.call_delete_plant)
        self.asm.asm_ret()
        self.asm_code_execute()

    def kill_all_zombies(self):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        addrs = self._get_zombie_addresses()
        zombie_status = self.data.lawn.board.zombies.status
        for addr in addrs:
            self.write_memory(addr + zombie_status, 3, 1)

    def delete_grid_items(self, types):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        addrs = self._get_grid_items(types)
        self.asm.asm_init()
        for addr in addrs:
            self.asm.asm_mov_exx(Reg.ESI, addr)
            self.asm.asm_call(self.data.call_delete_grid_item)
        self.asm.asm_ret()
        self.asm_code_execute()

    def put_lily(self, from_col, to_col):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        scene = self.get_scene()
        if scene != 2 and scene != 3:
            return
        addrs = self._get_plant_addresses()
        plant_row = self.data.lawn.board.plants.row
        plant_col = self.data.lawn.board.plants.col
        occupied = set()
        for addr in addrs:
            row = self.read_memory(addr + plant_row, 4)
            col = self.read_memory(addr + plant_col, 4)
            occupied.add((row, col))
        self.asm.asm_init()
        if from_col < 0:
            from_col = 0
        if to_col > 8:
            to_col = 8
        if to_col < from_col:
            to_col = from_col
        for col in range(from_col, to_col + 1):
            if (2, col) not in occupied:
                self._asm_put_plant(16, 2, col, False)
            if (3, col) not in occupied:
                self._asm_put_plant(16, 3, col, False)
        self.asm.asm_ret()
        self.asm_code_execute()

    def put_flowerpot(self, from_col, to_col):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        scene = self.get_scene()
        if scene != 4 and scene != 5:
            return
        addrs = self._get_plant_addresses()
        plant_row = self.data.lawn.board.plants.row
        plant_col = self.data.lawn.board.plants.col
        occupied = set()
        for addr in addrs:
            row = self.read_memory(addr + plant_row, 4)
            col = self.read_memory(addr + plant_col, 4)
            occupied.add((row, col))
        self.asm.asm_init()
        if from_col < 0:
            from_col = 0
        if to_col > 8:
            to_col = 8
        if to_col < from_col:
            to_col = from_col
        for col in range(from_col, to_col + 1):
            for i in range(5):
                if (i, col) not in occupied:
                    self._asm_put_plant(33, i, col, False)
        self.asm.asm_ret()
        self.asm_code_execute()

    def set_music(self, music_id):
        if not self.is_open():
            return
        lawn_offset, music_offset = self.data.recursively_get_attrs(['lawn', 'music'])
        self.asm.asm_init()
        self.asm.asm_mov_exx(Reg.EDI, music_id)
        self.asm.asm_mov_exx_dword_ptr(Reg.EAX, lawn_offset)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EAX, music_offset)
        self.asm.asm_call(self.data.call_play_music)
        self.asm.asm_ret()
        self.asm_code_execute()

    def chomper_no_cool_down(self, status):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        self.hack(self.data.chomper_no_cool_down, status)

    def _asm_put_grave(self, row, col):
        lawn_offset, board_offset, challenge_offset = self.data.recursively_get_attrs(['lawn', 'board', 'challenge'])
        self.asm.asm_mov_exx(Reg.EDI, row)
        self.asm.asm_mov_exx(Reg.EBX, col)
        self.asm.asm_mov_exx_dword_ptr(Reg.ECX, lawn_offset)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.ECX, board_offset)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.ECX, challenge_offset)
        self.asm.asm_push_exx(Reg.ECX)
        self.asm.asm_call(self.data.call_put_grave)

    def put_grave(self, row, col):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        row_count = self.get_row_count()
        col_count = 9
        if row >= row_count or col >= col_count:
            return
        self.asm.asm_init()
        if row == -1 and col == -1:
            for r in range(row_count):
                for c in range(col_count):
                    self._asm_put_grave(r, c)
        elif row != -1 and col == -1:
            for c in range(col_count):
                self._asm_put_grave(row, c)
        elif row == -1 and col != -1:
            for r in range(row_count):
                self._asm_put_grave(r, col)
        else:
            self._asm_put_grave(row, col)
        self.asm.asm_ret()
        self.asm_code_execute()

    def _asm_put_ladder(self, row, col):
        lawn_offset, board_offset = self.data.recursively_get_attrs(['lawn', 'board'])
        self.asm.asm_push_dword(col)
        self.asm.asm_mov_exx(Reg.EDI, row)
        self.asm.asm_mov_exx_dword_ptr(Reg.EAX, lawn_offset)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EAX, board_offset)
        self.asm.asm_call(self.data.call_put_ladder)

    def put_ladder(self, row, col):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        row_count = self.get_row_count()
        col_count = 9
        if row >= row_count or col >= col_count:
            return
        self.asm.asm_init()
        if row == -1 and col == -1:
            for r in range(row_count):
                for c in range(col_count):
                    self._asm_put_ladder(r, c)
        elif row != -1 and col == -1:
            for c in range(col_count):
                self._asm_put_ladder(row, c)
        elif row == -1 and col != -1:
            for r in range(row_count):
                self._asm_put_ladder(r, col)
        else:
            self._asm_put_ladder(row, col)
        self.asm.asm_ret()
        self.asm_code_execute()

    def _asm_put_rake(self, row, col):
        lawn_offset, board_offset = self.data.recursively_get_attrs(['lawn', 'board'])
        self.write_memory(0x41786b, row, 4)
        self.write_memory(0x4177d7, col, 4)
        self.asm.asm_init()
        self.asm.asm_mov_exx_dword_ptr(Reg.EAX, lawn_offset)
        self.asm.asm_mov_exx_dword_ptr_exx_add(Reg.EAX, board_offset)
        self.asm.asm_call(self.data.call_put_rake)
        self.asm.asm_ret()
        self.asm_code_execute()

    def put_rake(self, row, col):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        row_count = self.get_row_count()
        col_count = 9
        if row >= row_count or col >= col_count:
            return
        reset_dec_rake_code = self.read_memory(0x41786a, 6)
        reset_rake_col_code = self.read_memory(0x4177d7, 4)
        self.write_memory(0x41786a, 0x9000000000bf, 6)
        self.hack(self.data.rake_unlimited, True)
        if row == -1 and col == -1:
            for r in range(row_count):
                for c in range(col_count):
                    self._asm_put_rake(r, c)
        elif row != -1 and col == -1:
            for c in range(col_count):
                self._asm_put_rake(row, c)
        elif row == -1 and col != -1:
            for r in range(row_count):
                self._asm_put_rake(r, col)
        else:
            self._asm_put_rake(row, col)
        self.write_memory(0x41786a, reset_dec_rake_code, 6)
        self.write_memory(0x4177d7, reset_rake_col_code, 4)
        self.hack(self.data.rake_unlimited, False)

    def screen_shot(self):
        if not self.is_open():
            return
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        width = right - left
        height = bottom - top
        hdc_window = win32gui.GetDC(self.hwnd)
        if not hdc_window:
            win32gui.ReleaseDC(self.hwnd, hdc_window)
        hdc_mem = win32gui.CreateCompatibleDC(hdc_window)
        if not hdc_mem:
            win32gui.DeleteObject(hdc_mem)
            win32gui.ReleaseDC(self.hwnd, hdc_window)
        screen = win32gui.CreateCompatibleBitmap(hdc_window, width, height)
        if not screen:
            win32gui.DeleteObject(screen)
            win32gui.DeleteObject(hdc_mem)
            win32gui.ReleaseDC(self.hwnd, hdc_window)
        win32gui.SelectObject(hdc_mem, screen)
        if win32gui.BitBlt(hdc_mem, 0, 0, width, height, hdc_window, 0, 0, 0xCC0020):
            win32gui.DeleteObject(screen)
            win32gui.DeleteObject(hdc_mem)
            win32gui.ReleaseDC(self.hwnd, hdc_window)
        if win32clipboard.OpenClipboard() != 0:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(2, screen)
            win32clipboard.CloseClipboard()
        win32gui.DeleteObject(screen)
        win32gui.DeleteObject(hdc_mem)
        win32gui.ReleaseDC(self.hwnd, hdc_window)

    def stop_spawning(self, status):
        self.hack(self.data.stop_spawning, status)

    def plants_instant_growup(self, status):
        if not self.is_open():
            return
        self.hack(self.data.plants_growup, status)

    def get_lineup(self):
        if not self.is_open():
            return
        ui = self.game_ui()
        lineup = Lineup()
        lineup.scene = self.get_scene()
        if ui != 2 and ui != 3:
            return lineup

        plant_addrs = self._get_plant_addresses()
        plants_offset = self.data.lawn.board.plants
        plant_row_offset = plants_offset.row
        plant_col_offset = plants_offset.col
        plant_type_offset = plants_offset.type
        plant_asleep_offset = plants_offset.asleep
        plant_imitator_offset = plants_offset.imitator
        for addr in plant_addrs:
            row = self.read_memory(addr + plant_row_offset, 4)
            col = self.read_memory(addr + plant_col_offset, 4)
            index = row * 9 + col
            plant_type = self.read_memory(addr + plant_type_offset, 4)
            imitator = self.read_memory(addr + plant_imitator_offset, 1) == 48
            if plant_type == 16:
                lineup.base[index] = 1
                lineup.base_is_imitator[index] = imitator
            elif plant_type == 33:
                lineup.base[index] = 2
                lineup.base_is_imitator[index] = imitator
            elif plant_type == 30:
                lineup.pumpkins[index] = 1
                lineup.pumpkins_is_imitator[index] = imitator
            elif plant_type == 35:
                lineup.coffee_beans[index] = 1
                lineup.coffee_beans_is_imitator[index] = imitator
            else:
                is_asleep = self.read_memory(addr + plant_asleep_offset, 1)
                lineup.plants[index] = plant_type + 1
                lineup.plants_is_imitator[index] = imitator
                lineup.plants_is_asleep[index] = is_asleep

        grid_item_addrs = self._get_grid_items([1, 3, 11])
        grid_items_offset = self.data.lawn.board.grid_items
        grid_items_row_offset = grid_items_offset.row
        grid_items_col_offset = grid_items_offset.col
        grid_items_type_offset = grid_items_offset.type
        for addr in grid_item_addrs:
            row = self.read_memory(addr + grid_items_row_offset, 4)
            col = self.read_memory(addr + grid_items_col_offset, 4)
            index = row * 9 + col
            grid_item_type = self.read_memory(addr + grid_items_type_offset, 4)
            if grid_item_type == 1:
                lineup.base[index] = 3
            elif grid_item_type == 3:
                lineup.ladders[index] = 1
            else:
                lineup.rakes[index] = 1
        lineup.compress()
        return lineup

    def set_lineup(self, lineup: Lineup):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 2 and ui != 3:
            return
        scene = self.get_scene()
        if scene < 0 or scene > 5 or lineup.scene < 0 or lineup.scene > 5:
            return
        if scene != lineup.scene:
            self.set_scene(lineup.scene)
        else:
            self.delete_all_plants()
            self.delete_grid_items({1, 2, 3, 11})
        rakes = []
        self.asm.asm_init()
        for r in range(6):
            for c in range(9):
                index = r * 9 + c
                if lineup.base[index] == 1:
                    self._asm_put_plant(16, r, c, lineup.base_is_imitator[index])
                elif lineup.base[index] == 2:
                    self._asm_put_plant(33, r, c, lineup.base_is_imitator[index])
                if lineup.pumpkins[index]:
                    self._asm_put_plant(30, r, c, lineup.pumpkins_is_imitator[index])
                if lineup.coffee_beans[index]:
                    self._asm_put_plant(35, r, c, lineup.coffee_beans_is_imitator[index])
                if lineup.plants[index]:
                    plant_type = lineup.plants[index] - 1
                    if plant_type < 0 or plant_type > 47\
                            or plant_type == 16 or plant_type == 33\
                            or plant_type == 30 or plant_type == 35:
                        continue
                    is_imitator = lineup.plants_is_imitator[index]
                    self._asm_put_plant(plant_type, r, c, is_imitator)
                    if lineup.scene == 0 or lineup.scene == 2 or lineup.scene == 4:
                        if not lineup.plants_is_asleep[index] and may_asleep[plant_type]:
                            self.asm.asm_push_exx(Reg.EAX)
                            self.asm.asm_mov_exx_exx(Reg.EDI, Reg.EAX)
                            self.asm.asm_push_byte(0)
                            self.asm.asm_call(self.data.call_set_plant_sleeping)
                            self.asm.asm_pop_exx(Reg.EAX)
                    if plant_type == 4 or plant_type == 9 or plant_type == 47:
                        self.asm.asm_add_list([0xc7, 0x40, 0x54])
                        self.asm.asm_add_dword(1)

                if lineup.base[index] == 3:
                    self._asm_put_grave(r, c)
                if lineup.ladders[index]:
                    self._asm_put_ladder(r, c)
                if lineup.rakes[index]:
                    rakes.append((r, c))
        self.asm.asm_ret()
        self.asm_code_execute()

        reset_dec_rake_code = self.read_memory(0x41786a, 6)
        reset_rake_col_code = self.read_memory(0x4177d7, 4)
        self.write_memory(0x41786a, 0x9000000000bf, 6)
        self.hack(self.data.rake_unlimited, True)
        for row, col in rakes:
            self._asm_put_rake(row, col)
        self.write_memory(0x41786a, reset_dec_rake_code, 6)
        self.write_memory(0x4177d7, reset_rake_col_code, 4)
        self.hack(self.data.rake_unlimited, False)

    def zombie_not_explode(self, status):
        if not self.is_open():
            return
        self.hack(self.data.zombie_not_explode, status)

    def zombie_stop(self, status):
        if not self.is_open():
            return
        self.hack(self.data.zombie_stop, status)

    def lock_butter(self, status):
        if not self.is_open():
            return
        self.hack(self.data.lock_butter, status)

    def _asm_change_bullet(self, from_bullet, to_bullet):
        self.asm.asm_add_dword(0x24247c83)
        self.asm.asm_add_byte(from_bullet)  # cmp [esp+24],f
        self.asm.asm_add_word(0x0c75)
        self.asm.asm_add_list([0xc7, 0x45, 0x5c])
        self.asm.asm_add_dword(to_bullet)  # mov [ebp+5c],t

    def change_bullet(self, from_bullet, to_bullet):
        if not self.is_open():
            return
        items = copy.copy(self.changed_bullets.get('items', {}))
        if from_bullet == to_bullet:
            if from_bullet in items:
                items.pop(from_bullet)
                if not items:
                    self.reset_bullets()
                    return
        else:
            if to_bullet == items.get(from_bullet):
                return
            items[from_bullet] = to_bullet
        inject_addr = self.changed_bullets.get('address') or self.asm.asm_alloc(self.phand, 512)
        return_addr = 0x47bb6c
        self.asm.asm_init()
        for f, t in items.items():
            self._asm_change_bullet(f, t)
            self.asm.asm_near_jmp(return_addr)
        self.asm.asm_add_dword(0x2424448b)  # mov eax,[esp+24]
        self.asm.asm_add_list([0x89, 0x45, 0x5c])  # mov [ebp+5c],eax
        self.asm.asm_near_jmp(return_addr)  # jmp return_addr
        ret = self.asm.asm_code_inject(self.phand, inject_addr)
        if not ret:
            return
        self.changed_bullets['items'] = items
        if 'address' not in self.changed_bullets:
            self.changed_bullets['address'] = inject_addr
            target = inject_addr - 0x47bb6a
            if target < 0:
                target += 0x100000000
            self.write_memory(0x47bb65, 0x906600000000e9 + target * 16 * 16, 7)

    def reset_bullets(self):
        if not self.is_open():
            return
        addr = self.changed_bullets.get('address')
        if addr:
            self.write_memory(0x47bb65, 0x5c45892424448b, 7)
            self.asm.asm_free(self.phand, addr)
            self.changed_bullets.clear()

    def add_garden_plant(self, plant_type: int, direction: int, color: int):
        if not self.is_open():
            return
        lawn_offset, user_data_offset, garden_plants_offset = self.data.recursively_get_attrs(['lawn', 'user_data', 'garden_plants'])
        plants_addr = self.read_offset((lawn_offset, user_data_offset)) + garden_plants_offset
        garden_offset = garden_plants_offset.garden
        count = self.read_offset((lawn_offset, user_data_offset, user_data_offset.garden_plant_count))
        plant_struct_size = 0x58
        zen_count = 0
        for i in range(count):
            garden = self.read_memory(plants_addr + garden_offset + i * plant_struct_size)
            if garden == 0:
                zen_count += 1
        if zen_count >= 32:
            return 0
        data = bytearray(b'\x00' * plant_struct_size)
        data[0: 4] = int.to_bytes(plant_type, 4, 'little')
        data[0x2c: 0x30] = int.to_bytes(3, 4, 'little')
        data[0x10: 0x14] = int.to_bytes(direction, 4, 'little')
        data[0x20: 0x24] = int.to_bytes(color, 4, 'little')
        addr = self.asm.asm_alloc(self.phand, 512)
        self.asm.asm_init()
        self.asm.asm_mov_exx_dword_ptr(Reg.ECX, lawn_offset)
        self.asm.asm_add_word(0x818b)
        self.asm.asm_add_dword(0x940)
        self.asm.asm_push_exx(Reg.EAX)
        self.asm.asm_mov_exx(Reg.EDX, addr + 0x18)
        self.asm.asm_call(self.data.call_add_garden_plant)
        self.asm.asm_ret()
        self.asm.asm_add_list(data)
        self.asm_code_execute(addr)
        return 1

    def free_planting(self, status):
        if not self.is_open():
            return
        lawn_offset, free_planting_offset = self.data.recursively_get_attrs(['lawn', 'free_planting'])
        free_planting_addr = self.read_memory(lawn_offset) + free_planting_offset
        hack = Hack(free_planting_addr, 0, 1, 1)
        self.hack([hack], status)

    def change_garden_cursor(self, cursor_type):
        if not self.is_open():
            return
        scene = self.get_scene()
        if scene < 6 or scene > 9:
            return
        status = cursor_type != 0
        self.set_cursor(cursor_type)
        self.hack(self.data.lock_cursor, status)

    def _asm_set_slot_plant(self, plant_type, slot_addr, plant_type_imitator):
        self.asm.asm_mov_exx(Reg.ESI, slot_addr)
        self.asm.asm_mov_exx(Reg.EDI, plant_type)
        self.asm.asm_mov_exx(Reg.EDX, plant_type_imitator)
        self.asm.asm_call(self.data.call_set_slot_plant)

    def set_slot_plant(self, plant_type, slot_id, imitator):
        if not self.is_open():
            return
        ui = self.game_ui()
        if ui != 3:
            return
        slot_struct_size = 0x50
        lawn_offset, board_offset, slots_offset = self.data.recursively_get_attrs(['lawn', 'board', 'slots'])
        slots_addr = self.read_offset((lawn_offset, board_offset, slots_offset))
        if imitator or plant_type == 0x30:
            plant_type_imitator = plant_type
            plant_type = 0x30
        else:
            plant_type_imitator = 0xffffffff
        self.asm.asm_init()
        if slot_id == -1:
            for slot_id in range(10):
                slot_addr = slots_addr + slot_id * slot_struct_size + 0x28
                self._asm_set_slot_plant(plant_type, slot_addr, plant_type_imitator)
        else:
            slot_addr = slots_addr + slot_id * slot_struct_size + 0x28
            self._asm_set_slot_plant(plant_type, slot_addr, plant_type_imitator)
        self.asm.asm_ret()
        self.asm_code_execute()


if __name__ == '__main__':
    game = PvzModifier()
    game.wait_for_game()
