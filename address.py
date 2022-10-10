from collections import namedtuple


class Offset(int):

    def __new__(cls, num, **kwargs):
        data = int.__new__(cls, num)
        for k, v in kwargs.items():
            v: Offset
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
            frame_duration=Offset(0x4b4),
            game_selector=Offset(0x870),
            game_ui=Offset(0x920),
            board=Offset(
                0x868,
                scene=Offset(0x5564),
                sun=Offset(0x5578),
                adventure_level=Offset(0x5568),
                cursor=Offset(0x150, cursor_grab=0x30),
                plant_count_max=Offset(0xc8),
                plant_count=Offset(0xd4),
                plants=Offset(
                    0xc4,
                    row=0x1c,
                    type=0x24,
                    col=0x28,
                    imitator=0x138,
                    dead=0x141,
                    squished=0x142,
                    asleep=0x143,
                    count_max=0xc8
                ),
                zombie_count=Offset(0xb8),
                zombies=Offset(0xa8)
            ),
            user_data=Offset(
                0x950,
                achievement=Offset(0x24),
                level=Offset(0x4c),
                money=Offset(0x50),
                playthrough=Offset(0x54),
                survival=Offset(0x58),
                mini_game=Offset(0x94),
                tree_height=Offset(0x11c),
                puzzle=Offset(0x120),
                twiddydinky=Offset(0x1e8),
                fertilizer=Offset(0x220),
                bug_spray=Offset(0x224),
                chocolate=Offset(0x250),
                tree_food=Offset(0x258)
            )
        ),
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
        lock_shovel=[Hack(0x41e36e, 0x89, 0x39, 1)],
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

        overlapping_plant=[Hack(0x41bd2e, 0x84, 0x81, 1)],
        overlapping_plant_preview=[Hack(0x444790, 0x74, 0xeb, 1)],
        overlapping_plant_iz=[Hack(0x435579, 0x84, 0x8d, 1)],

        mushrooms_awake=[Hack(0x0046c1c2, 0x74, 0xeb, 1)],

        call_main_menu=0x00455420,
        call_set_plant_sleeping=0x46cb90
    )