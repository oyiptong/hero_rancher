from py2neo import ogm
from hero_rancher.utils import get_env

env = get_env()


class FEHObject(ogm.GraphObject):
    __primarykey__ = 'id'
    id = ogm.Property()
    graph = env.graph


class Color(FEHObject):
    character = ogm.RelatedFrom('Character', 'COLOR')


class WeaponType(FEHObject):
    character = ogm.RelatedFrom('Character', 'WEAPON_TYPE')


class MoveType(FEHObject):
    character = ogm.RelatedFrom('Character', 'MOVE_TYPE')


class Weapon(FEHObject):
    character = ogm.RelatedFrom('Character', 'WEAPON')


class Special(FEHObject):
    character = ogm.RelatedFrom('Character', 'SPECIAL')


class Assist(FEHObject):
    character = ogm.RelatedFrom('Character', 'ASSIST')


class PassiveSkill(FEHObject):
    slot = ogm.Property()
    character = ogm.RelatedFrom('Character', 'PASSIVE_SKILL')


class Character(FEHObject):
    color = ogm.RelatedTo("Color")
    weapon_type = ogm.RelatedTo("WeaponType")
    move_type = ogm.RelatedTo("MoveType")
    weapon = ogm.RelatedTo("Weapon")
    special = ogm.RelatedTo("Special")
    assist = ogm.RelatedTo("Assist")
    passive_skill = ogm.RelatedTo("PassiveSkill")
    game = ogm.RelatedFrom('Game', 'CHARACTER')


class Game(FEHObject):
    character = ogm.RelatedTo("Character")
