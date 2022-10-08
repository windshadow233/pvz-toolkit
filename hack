{
            0x7525b0, // path
            0x755e0c, // lawn

            0x454 + 0x60, // frame_duration

            0x768 + 0x100, // board

            0x90 + 0x18, // zombie
            0x28,        //   zombie_status
            0xec,        //   zombie_dead
            0x94 + 0x18, // zombie_count_max

            0xac + 0x18, // plant
            0x1c,        //   plant_row
            0x24,        //   plant_type
            0x28,        //   plant_col
            0x138,       //   plant_imitater
            0x141,       //   plant_dead
            0x142,       //   plant_squished
            0x143,       //   plant_asleep
            0xb0 + 0x18, // plant_count_max
            0xb8 + 0x18, // plant_next_pos

            0x100 + 0x18, // lawn_mower
            0x30,         //   lawn_mower_dead
            0x104 + 0x18, // lawn_mower_count_max
            0x110 + 0x18, // lawn_mower_count

            0x11c + 0x18, // grid_item
            0x08,         //   grid_item_type
            0x10,         //   grid_item_col
            0x14,         //   grid_item_row
            0x20,         //   grid_item_dead
            0x120 + 0x18, // grid_item_count_max

            0x138 + 0x18, // cursor
            0x30,         //   cursor_grab

            0x144 + 0x18, // slot
            0x24,         //   slot_count
            0x4c,         //   slot_seed_cd_past
            0x50,         //   slot_seed_cd_total
            0x5c,         //   slot_seed_type
            0x60,         //   slot_seed_type_im

            0x15c + 0x18, // cut_scene

            0x160 + 0x18, // challenge
            0x6c,         //   endless_rounds

            0x164 + 0x18,  // game_paused
            0x168 + 0x18,  // block_type
            0x5d8 + 0x18,  // row_type
            0x624 + 0x18,  // ice_trail_cd
            0x6b4 + 0x18,  // spawn_list
            0x54d4 + 0x18, // spawn_type
            0x554c + 0x18, // scene
            0x5550 + 0x18, // adventure_level
            0x5560 + 0x18, // sun
            0x5568 + 0x18, // game_clock
            0x55f8 + 0x18, // debug_mode
            0x5620 + 0x18, // particle_systems_addr

            0x770 + 0x100, // game_selector

            0x7f5 + 0x120 + 4, // tod_mode

            0x7f8 + 0x120 + 4, // game_mode
            0x7fc + 0x120 + 4, // game_ui

            0x814 + 0x120 + 4, // free_planting

            0x820 + 0x120 + 4, // anim
            0x00,              //   unnamed
            0x00,              //     particle_system
            0x00,              //       particle_system_type
            0x1c,              //       particle_system_dead
            0x04,              //     particle_system_count_max

            0x82c + 0x120 + 4, // user_data
            0x24 + 0x28,       //   level
            0x28 + 0x28,       //   money
            0x2c + 0x28,       //   playthrough
            0x30 + 0x28,       //   mini_games
            0xf4 + 0x28,       //   tree_height
            0x1c0 + 0x28,      //   twiddydinky

            0x83c + 0x120 + 4, // music

            {0x0062941e, {0xfe}, {0xc8}}, // block_main_loop

            {0x0043c0c1, {0xeb}, {0x7e}}, // unlock_sun_limit
            {0x0043cc72, {0xeb}, {0x75}}, // auto_collected
            {0x0054bfe6, {0x66}, {0x5b}}, // not_drop_loot

            {0x00534d7b, {0x39}, {0xff}},                                 // fertilizer_unlimited
            {0x00534e73, {0x39}, {0xff}},                                 // bug_spray_unlimited
            {{0x00534995, {0x39}, {0xff}}, {0x00534a17, {0x39}, {0xff}}}, // chocolate_unlimited
            {0x0043885d, {0x39}, {0xff}},                                 // tree_food_unlimited

            {0x0041bd2e, {0x81}, {0x84}},                                 // placed_anywhere
            {0x00444790, {0xeb}, {0x74}},                                 // placed_anywhere_preview
            {0x00435579, {0x8d}, {0x84}},                                 // placed_anywhere_iz
            {{0x0042e58f, {0x80}, {0x8f}}, {0x0049f6fe, {0x33}, {0x85}}}, // fast_belt
            {0x0041e36e, {0x39}, {0x89}},                                 // lock_shovel

            {0x00417731, {0x800f}, {0x840f}},             // rake_unlimited
            {0x00417a54 + 3, {0x01}, {0x00}},             // init_lawn_mowers
            {0x00465f60 + 2, {0x00727894}, {0x00727a78}}, // lawn_mower_initialize

            {0x0054ba6b, {0x46, 0x40, 0x00}, {0x46, 0x40, 0xfc}}, // plant_immune_eat
            {0x0042883f, {0xeb}, {0x74}},                         // plant_immune_radius
            {0x0054316a, {0xeb}, {0x75}},                         // plant_immune_jalapeno
            {0x0047c3db, {0x90, 0x90, 0x90}, {0x29, 0x50, 0x40}}, // plant_immune_projectile
            {0x0047cb99, {0x90, 0x90, 0x90}, {0x29, 0x4e, 0x40}}, // plant_immune_lob_motion
            {0x0054a6ab, {0xeb}, {0x74}},                         // plant_immune_square
            {0x0046d13a, {0x70}, {0x75}},                         // plant_immune_row_area
            {0x0046cf96, {0x00}, {0xce}},                         // plant_immune_spike_rock
            {0x00470f80, {0xc2, 0x04, 0x00}, {0x53, 0x55, 0x8b}}, // plant_immune_squish

            {0x0054ba6b, {0x66, 0x40, 0x00}, {0x46, 0x40, 0xfc}}, // _plant_immune_eat
            {0x0047c3db, {0x29, 0x40, 0x40}, {0x29, 0x50, 0x40}}, // _plant_immune_projectile
            {0x0047cb99, {0x29, 0x76, 0x40}, {0x29, 0x4e, 0x40}}, // _plant_immune_lob_motion
            {0x0046d13a, {0xeb}, {0x75}},                         // _plant_immune_row_area

            {0x0054d0ba, {0x90909090}, {0x20246c2b}}, // zombie_immune_body_damage
            {0x0054cdd4, {0x2b, 0xc0}, {0x2b, 0xc8}}, // zombie_immune_helm_damage
            {0x0054ca2b, {0xd233c033}, {0xc28b027c}}, // zombie_immune_shield_damage
            {0x0054e951, {0x81}, {0x8d}},             // zombie_immune_burn_crumble
            {0x00429523, {0xeb}, {0x7f}},             // zombie_immune_radius
            {0x00474962, {0xeb}, {0x75}},             // zombie_immune_burn_row
            {0x0046f808, {0xeb}, {0x74}},             // zombie_immune_chomper
            {0x0054b7ff, {0x00}, {0x01}},             // zombie_immune_mind_controll
            {0x00474a71, {0x90, 0x90}, {0x74, 0x05}}, // zombie_immune_blow_away
            {0x0047c843, {0xeb}, {0x74}},             // zombie_immune_splash
            {0x00466785, {0xeb}, {0x74}},             // zombie_immune_lawn_mower

            {0x0054d0ba, {0x9090ed2b}, {0x20246c2b}}, // _zombie_immune_body_damage
            {0x0054cdd4, {0x2b, 0xc9}, {0x2b, 0xc8}}, // _zombie_immune_helm_damage
            {0x0054ca2b, {0xc28bd08b}, {0xc28b027c}}, // _zombie_immune_shield_damage
            {0x0054e951, {0x80}, {0x8d}},             // _zombie_immune_burn_crumble

            {0x0046f40b, {0x80}, {0x85}},                                 // reload_instantly
            {{0x0046e224, {0x80}, {0x85}}, {0x0046df73, {0x70}, {0x75}}}, // grow_up_quickly
            {{0x0046f925, {0x70}, {0x75}}, {0x00470217, {0x80}, {0x85}}}, // no_cooldown
            {0x0046c1c2, {0xeb}, {0x74}},                                 // mushrooms_awake
            {0x004318bc, {0xeb}, {0x74}},                                 // stop_spawning
            {{0x00546823, {0x54}, {0x64}}, {0x0054682c, {0x54}, {0x44}}}, // stop_zombies
            {0x0046d542, {0x70}, {0x75}},                                 // lock_butter
            {0x004293cd, {0x70}, {0x75}},                                 // no_crater
            {{0x005464a0, {0xc3}, {0x51}}, {0x0042b0b9, {0xeb}, {0x75}}}, // no_ice_trail
            {{0x0054257c, {0x81}, {0x8f}}, {0x0054305d, {0x81}, {0x85}}}, // zombie_not_explode

            {0x00445d33, {0x80}, {0x85}}, // hack_street_zombies

            {0x0042616d, {0xd231}, {0xf23b}},                     // no_fog
            {0x00459c1a, {0x0033b866}, {0x047ec085}},             // see_vase
            {0x00624919, {0x00eb}, {0x4074}},                     // background_running
            {0x00620143, {0x70}, {0x74}},                         // disable_delete_userdata
            {0x00497ed3, {0x001879c9 + 0x28}, {0x001879c9}},      // disable_save_userdata
            {0x0043935a, {0x38, 0x58, 0x64}, {0x88, 0x58, 0x64}}, // unlock_limbo_page

            0x00455420, // call_sync_profile

            0x00418140, // call_fade_out_level

            0x004385d0, // call_wisdom_tree

            0x00418d70, // call_put_plant
            0x00475050, // call_put_plant_imitater
            0x004357d0, // call_put_plant_iz_style
            0x00435390, // call_put_zombie
            0x00419a60, // call_put_zombie_in_row
            0x00431900, // call_put_grave
            0x00414d10, // call_put_ladder
            0x00417710, // call_put_rake
            0x0041786a, // call_put_rake_row
            0x004177d3, // call_put_rake_col

            0x00466cf0, // call_start_lawn_mower
            0x00466c60, // call_delete_lawn_mower
            0x004179b0, // call_restore_lawn_mower

            0x00475e90, // call_delete_plant
            0x00458620, // call_delete_grid_item

            0x0046cb90, // call_set_plant_sleeping

            0x004350f0, // call_puzzle_next_stage_clear
            0x00415e90, // call_pick_background
            0x0052b620, // call_delete_particle_system

            0x004150c0, // call_pick_zombie_waves
            0x00419c50, // call_remove_cutscene_zombies
            0x00445d20, // call_place_street_zombies

            0x00469a10, // call_play_music
        };
