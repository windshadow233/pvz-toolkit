from collections import namedtuple


Hack = namedtuple("Hack", field_names=["address", "reset_value", "hack_value", "length"])


Data = namedtuple("Data", field_names=[
    "lawn",
    "board",
    "sun",
    "adventure_level",
    "cursor",
    "cursor_grab",

    "user_data",
    "money",
    "level",
    "fertilizer",
    "bug_spray",
    "chocolate",
    "tree_height",
    "tree_food",

    "vase_transparent",
    "no_cool_down",
    "auto_collect",
    "money_not_dec",
    "sun_not_dec",
    "chocolate_not_dec",
    "fertilizer_not_dec",
    "bug_spray_not_dec",
    "tree_food_not_dec",
    "lock_shovel",
    "unlock_limbo_page",
    "background_running"
])


class Address:
    pvz_goty_1_1_0_1056_zh_2012_06 = Data(
        lawn=0x755e0c,
        board=0x868,
        sun=0x5578,
        adventure_level=0x5568,
        cursor=0x150,
        cursor_grab=0x30,

        user_data=0x950,
        money=0x50,
        level=0x4c,
        fertilizer=0x220,
        bug_spray=0x224,
        chocolate=0x250,
        tree_height=0x11c,
        tree_food=0x258,

        vase_transparent=[Hack(0x459c1a, 0x047ec085, 0x0033b866, 4)],
        no_cool_down=[Hack(0x49ce02, 0x167e, 0x9090, 2)],
        auto_collect=[Hack(0x43cc72, 0x0975, 0x09eb, 2)],
        money_not_dec=[Hack(0x4a2451, 0x504129, 0x909090, 3)],
        sun_not_dec=[Hack(0x427694, 0xf32b, 0x9090, 2)],
        chocolate_not_dec=[Hack(0x534a17, 0x0000025088ff, 0x909090909090, 6), Hack(0x534995, 0x0000025088ff, 0x909090909090, 6)],
        fertilizer_not_dec=[Hack(0x534d7b, 0x0000022088ff, 0x909090909090, 6)],
        bug_spray_not_dec=[Hack(0x534e73, 0x0000022488ff, 0x909090909090, 6)],
        tree_food_not_dec=[Hack(0x43885d, 0x0000025888ff, 0x909090909090, 6)],
        lock_shovel=[Hack(0x41e36e, 0x89, 0x39, 1)],
        unlock_limbo_page=[Hack(0x43935a, 0x88, 0x38, 1)],
        background_running=[Hack(0x624919, 0x4074, 0x00eb, 2)]
    )
