from py2neo import ogm


class FEHObject(ogm.GraphObject):
    __primarykey__ = 'name'

    # strings
    name = ogm.Property()
    description = ogm.Property()


class Character(FEHObject):
    color = ogm.Property()
    weapon_type = ogm.Property()
    move_type = ogm.Property()

    build = ogm.RelatedTo("Build")


class Build(FEHObject):
    default = ogm.Property()
    weapon = ogm.RelatedTo("Weapon")
    special = ogm.RelatedTo("Special")
    assist = ogm.RelatedTo("Assist")
    passive_a = ogm.RelatedTo("Skill")
    passive_b = ogm.RelatedTo("Skill")
    passive_c = ogm.RelatedTo("Skill")

    character = ogm.RelatedFrom("Character")


class Weapon(FEHObject):
    # strings
    weapon_type = ogm.Property()
    color = ogm.Property()
    color_effective = ogm.Property()
    move_effective = ogm.Property()

    # integers
    full_hp_atk_recoil_dmg = ogm.Property()
    initiate_heal = ogm.Property()
    initiate_poison = ogm.Property()
    might = ogm.Property()
    rnge = ogm.Property()
    poison = ogm.Property()
    spec_cooldown = ogm.Property()
    spec_damage_bonus = ogm.Property()

    # floats
    heal_dmg = ogm.Property()

    # bools
    add_bonus = ogm.Property()
    adjacent_ally_bonus = ogm.Property()
    brave = ogm.Property()
    char_unique = ogm.Property()
    convert_penalties = ogm.Property()
    counter = ogm.Property()
    dragon_effective = ogm.Property()
    magical = ogm.Property()
    prevent_counter = ogm.Property()
    tri_advantage = ogm.Property()

    skills = ogm.RelatedTo("Skill")

    build = ogm.RelatedFrom("Build")


class Skill(FEHObject):
    skill = ogm.Label()
    slot = ogm.Property()

    # these are strings, could be a relations
    weapon_restrict = ogm.Property()
    color_restrict = ogm.Property()
    move_restrict = ogm.Property()
    weapon_unique = ogm.Property()
    move_unique = ogm.Property()
    range_unique = ogm.Property()
    dragon_unique = ogm.Property()
    char_unique = ogm.Property()

    # stat mods, integers
    mod_attack = ogm.Property()
    mod_defence = ogm.Property()
    mod_health_point = ogm.Property()
    mod_resistance = ogm.Property()
    mod_speed = ogm.Property()
    mod_special_cooldown = ogm.Property()

    # could be boost, curse, threaten, buff
    mod_type = ogm.Property()

    # booleans
    activation_player = ogm.Property()
    activation_enemy = ogm.Property()
    counter = ogm.Property()
    no_follow = ogm.Property()

    # set damage
    recoil_damage = ogm.Property()
    poison = ogm.Property()

    defend_bow = ogm.Property()
    defend_dagger = ogm.Property()
    defend_staff = ogm.Property()
    defend_blue_tome = ogm.Property()
    defend_green_tome = ogm.Property()
    defend_red_tome = ogm.Property()

    # advantage skills
    advantage_stat = ogm.Property()
    advantage_threshold = ogm.Property()

    cancel_effective = ogm.Property()
    triangle_multiplier = ogm.Property()  # float

    hp_threshold = ogm.Property()
    weapon_effective = ogm.Property()

    movement_skill = ogm.Label()

    self_healing_amount = ogm.Property()
    self_healing_turns = ogm.Property()

    build = ogm.RelatedFrom("Build")


class Special(Skill):
    build = ogm.RelatedFrom("Build")


class Assist(Skill):
    build = ogm.RelatedFrom("Build")
