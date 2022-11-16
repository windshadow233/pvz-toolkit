from collections import namedtuple


class Offset(int):

    def __new__(cls, num, **kwargs):
        data = int.__new__(cls, num)
        for k, v in kwargs.items():
            data.__setattr__(k, v)
        return data

    def recursively_get_attrs(self, attrs):
        value = self
        for attr in attrs:
            value = value.__getattribute__(attr)
            yield value


Hack = namedtuple("Hack", field_names=["address", "reset_value", "hack_value", "length"])


class Data:
    pvz_goty_1_1_0_1056_zh_2012_06 = Offset(
        0,
        lawn=Offset(
            0x755e0c,
            frame_duration=0x4b4,
            game_selector=0x870,
            game_mode=0x91c,
            game_ui=0x920,
            board=Offset(
                0x868,
                challenge=0x178,
                block_type=0x180,
                row_type=0x5f0,
                scene=0x5564,
                sun=0x5578,
                adventure_level=0x5568,
                cursor=Offset(0x150, cursor_grab=0x30),
                slots=Offset(
                    0x15c,
                    count=0x24,
                    cd_past=0x4c,
                    cd_total=0x50,
                    plant_type=0x5c,
                    plant_type_imitator=0x60
                ),
                zombies=Offset(
                    0xa8,
                    row=0x1c,
                    type=0x24,
                    status=0x28,
                    speed=0x34,
                    dead=0xec
                ),
                zombie_count_max=0xac,
                zombie_count=0xb8,
                plants=Offset(
                    0xc4,
                    row=0x1c,
                    type=0x24,
                    col=0x28,
                    imitator=0x138,
                    dead=0x141,
                    squished=0x142,
                    asleep=0x143
                ),
                plant_count_max=0xc8,
                plant_count=0xd4,
                plant_next_pos=0xd0,
                lawn_mowers=Offset(
                    0x118,
                    row=0x14,
                    status=0x2c,
                    dead=0x30
                ),
                lawn_mower_count_max=0x11c,
                lawn_mower_count=0x128,
                grid_items=Offset(
                    0x134,
                    type=0x08,
                    vase_type=0xc,  # 3: 随机罐  4: 植物罐  5: 僵尸罐
                    col=0x10,
                    row=0x14,
                    layer=0x1c,
                    dead=0x20,
                    zombie_in_vase=0x3c,
                    plant_in_vase=0x40,
                    vase_content_type=0x44,  # 0: 空罐  1: 植物  2: 僵尸  3: 阳光
                    sun_shine_in_vase=0x50
                ),
                grid_item_count_max=0x138,
                grid_item_count=0x144,
                particle_systems=0x5638
            ),
            free_planting=0x938,
            animations=Offset(
                0x944,
                unnamed=Offset(
                    0x00,
                    particle_system=Offset(
                        0x00,
                        type=0x00,
                        dead=0x1c
                    ),
                    particle_system_count_max=0x04
                )
            ),
            user_data=Offset(
                0x950,
                achievement=0x24,
                level=0x4c,
                money=0x50,
                playthrough=0x54,
                survival=0x58,
                mini_game=0x94,
                tree_height=0x11c,
                puzzle=0x120,
                twiddydinky=0x1e8,
                fertilizer=0x220,
                bug_spray=0x224,
                remaining_rakes_count=248,
                chocolate=0x250,
                tree_food=0x258,
                garden_plants=Offset(
                    0x388,
                    type=0,
                    garden=0x4
                ),
                garden_plant_count=0x37c
            ),
            music=0x960
        ),
        block_main_loop=[Hack(0x62941e, 0xc8, 0xfe, 1)],
        vase_transparent=[Hack(0x459c1a, 0x047ec085, 0x0033b866, 4)],
        no_cool_down=[Hack(0x49ce02, 0x167e, 0x9090, 2)],
        auto_collect=[Hack(0x43cc72, 0x75, 0xeb, 1)],
        money_not_dec=[Hack(0x4a2451, 0x504129, 0x909090, 3)],
        sun_not_dec=[Hack(0x427694, 0xf32b, 0x9090, 2)],
        chocolate_not_dec=[Hack(0x534a17, 0x0000025088ff, 0x909090909090, 6),
                           Hack(0x534995, 0x0000025088ff, 0x909090909090, 6)],
        fertilizer_not_dec=[Hack(0x534d7b, 0x0000022088ff, 0x909090909090, 6)],
        bug_spray_not_dec=[Hack(0x534e73, 0x0000022488ff, 0x909090909090, 6)],
        tree_food_not_dec=[Hack(0x43885d, 0x0000025888ff, 0x909090909090, 6)],
        lock_cursor=[Hack(0x41e36e, 0x89, 0x39, 1)],
        unlock_limbo_page=[Hack(0x43935a, 0x88, 0x38, 1)],
        background_running=[Hack(0x624919, 0x4074, 0x00eb, 2)],

        plant_immune_eat=[Hack(0x54ba6b, 0xfc4046, 0x004046, 3)],
        plant_immune_radius=[Hack(0x42883f, 0x74, 0xeb, 1)],
        plant_immune_projectile=[Hack(0x47c3db, 0x405029, 0x909090, 3)],
        plant_immune_squish=[Hack(0x470f80, 0x8b5553, 0x0004c2, 3)],
        plant_immune_jalapeno=[Hack(0x54316a, 0x75, 0xeb, 1)],
        plant_immune_spike_rock=[Hack(0x46cf96, 0xce, 0x00, 1)],
        plant_immune_lob_motion=[Hack(0x47cb99, 0x404e29, 0x909090, 3)],
        plant_immune_square=[Hack(0x54a6ab, 0x74, 0xeb, 1)],
        plant_immune_row_area=[Hack(0x46d13a, 0x75, 0x70, 1)],

        plant_eat_weak=[Hack(0x54ba6b, 0xfc4046, 0x004066, 3)],
        plant_projectile_weak=[Hack(0x47c3db, 0x405029, 0x404029, 3)],
        plant_lob_motion_weak=[Hack(0x47cb99, 0x404e29, 0x407629, 3)],

        zombie_immune_body_damage=[Hack(0x54d0ba, 0x20246c2b, 0x90909090, 4)],
        zombie_immune_helm_damage=[Hack(0x54cdd4, 0xc82b, 0x9090, 2)],
        zombie_immune_shield_damage=[Hack(0x54ca2b, 0xc28b027c, 0xd233c033, 4)],
        zombie_immune_burn_crumble=[Hack(0x54e951, 0x8d, 0x81, 1)],
        zombie_immune_radius=[Hack(0x429523, 0x7f, 0xeb, 1)],
        zombie_immune_burn_row=[Hack(0x474962, 0x75, 0xeb, 1)],
        zombie_immune_chomper=[Hack(0x46f808, 0x74, 0xeb, 1)],
        zombie_immune_mind_control=[Hack(0x54b7ff, 0x01, 0x00, 1)],
        zombie_immune_blow_away=[Hack(0x474a71, 0x0574, 0x9090, 2)],
        zombie_immune_splash=[Hack(0x47c843, 0x74, 0xeb, 1)],
        zombie_immune_lawn_mower=[Hack(0x466785, 0x74, 0xeb, 1)],

        zombie_body_weak=[Hack(0x54d0ba, 0x20246c2b, 0x9090ed2b, 4)],
        zombie_helm_weak=[Hack(0x54cdd4, 0xc82b, 0xc92b, 2)],
        zombie_shield_weak=[Hack(0x54ca2b, 0xc28b027c, 0xc28bd08b, 4)],
        zombie_can_burn_crumble=[Hack(0x54e951, 0x8d, 0x80, 1)],

        doom_shroom_no_crater=[Hack(0x4293cd, 0x0575, 0x9090, 2)],
        no_ice_trail=[Hack(0x420220, 0x007d89, 0x90ff31, 3)],

        plant_anywhere=[Hack(0x41bd2e, 0x84, 0x81, 1)],
        plant_anywhere_preview=[Hack(0x444790, 0x74, 0xeb, 1)],
        plant_anywhere_iz=[Hack(0x435579, 0x84, 0x8d, 1)],

        mushrooms_awake=[Hack(0x46c1c2, 0x74, 0xeb, 1)],
        init_lawn_mowers=[Hack(0x417a57, 0x00, 0x01, 1),
                          Hack(0x465f62, 0x7a78, 0x7894, 2)],
        no_fog=[Hack(0x42616d, 0xf23b, 0xd231, 2)],
        chomper_no_cool_down=[Hack(0x46f925, 0x75, 0x70, 1)],
        rake_unlimited=[Hack(0x417732, 0x84, 0x80, 1)],
        stop_spawning=[Hack(0x41ff1c, 0x000055b48dff, 0x909090909090, 6)],
        plants_growup=[Hack(0x46df73, 0x75, 0x70, 1),
                       Hack(0x46e224, 0x85, 0x80, 1),
                       Hack(0x46f40b, 0x85, 0x80, 1)],
        zombie_not_explode=[Hack(0x54257c, 0x8f, 0x81, 1),
                            Hack(0x54305d, 0x85, 0x81, 1)],
        zombie_stop=[Hack(0x546823, 0x64, 0x54, 1),
                     Hack(0x54682c, 0x44, 0x54, 1)],
        lock_butter=[Hack(0x46d542, 0x75, 0x70, 1)],

        call_sync_profile=0x455420,
        call_set_plant_sleeping=0x46cb90,
        call_wisdom_tree=0x4385d0,
        call_put_plant=0x418d70,
        call_put_imitator_plant=0x475050,
        call_start_lawn_mower=0x466cf0,
        call_restore_lawn_mower=0x4179b0,
        call_delete_lawn_mower=0x466c60,
        call_put_zombie_in_row=0x419a60,
        call_put_zombie=0x435390,
        call_put_grave=0x431900,
        call_pick_background=0x415e90,
        call_put_ladder=0x414d10,
        call_put_rake=0x417710,
        call_delete_plant=0x475e90,
        call_delete_grid_item=0x458620,
        call_delete_particle_system=0x52b620,
        call_play_music=0x469a10,
        call_add_garden_plant=0x533520,
        call_set_slot_plant=0x49f5b0,
        call_new_grid_item=0x429d20,

        bullet_types={
            0: '豌豆',
            1: '冰豌豆',
            2: '卷心菜',
            3: '西瓜',
            4: '孢子',
            5: '冰瓜',
            6: '火豌豆',
            7: '杨桃',
            8: '尖刺',
            9: '篮球',
            10: '玉米粒',
            11: '玉米炮弹',
            12: '黄油'
        }
    )
