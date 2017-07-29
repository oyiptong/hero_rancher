import os
import sys
import multiprocessing
import logging
import json
from operator import itemgetter

from flask_script import Command, Option, Manager
from gunicorn.app.base import Application as GunicornApplication
from gunicorn.config import Config as GunicornConfig
from hero_rancher.utils import get_env
"""
from hero_rancher.models import (
    Character,
    Build,
    Weapon,
    Skill,
    Special,
    Assist,
)
"""
from hero_rancher.objects import (
    Color,
    WeaponType,
    MoveType,
    Weapon,
    Special,
    Assist,
    PassiveSkill,
    Character,
    Game,
)

command_logger_set = False


def setup_command_logger(loglevel=None):
    global command_logger_set
    if not command_logger_set:
        loglevel = loglevel or logging.INFO
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(loglevel)

        try:
            from colorlog import ColoredFormatter
            fmt = ColoredFormatter(
                "%(log_color)s%(message)s",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                }
            )
        except ImportError:
            # fall back to non-colored output
            fmt = logging.Formatter("%(message)s")

        handler.setFormatter(fmt)

        logger = logging.getLogger("command")
        logger.addHandler(handler)
        logger.setLevel(loglevel)
        command_logger_set = True
    else:
        logger = logging.getLogger("command")

    return logger


# ## List stuff

ListCommand = Manager(usage="List application info and data")


@ListCommand.command
def urls():
    """
    Return available endpoints
    """
    logger = setup_command_logger()

    endpoints = []
    from flask import current_app
    for rule in current_app.url_map.iter_rules():
        try:
            endpoints.append((
                rule.rule,
                sorted(list(rule.methods)),
            ))
        except Exception as e:
            logger.error(e)

    endpoints = sorted(endpoints, key=itemgetter(0))
    for url, methods in endpoints:
        logger.info("{0} {1}".format(
            url,
            json.dumps(methods),
        ))


# Data Commands

DataCommand = Manager(usage="Generate data and more")


@DataCommand.command
def purge_database():
    """
    Deletes everything from the database
    """
    setup_command_logger()
    from hero_rancher.database_utils import purge_database
    purge_database()


"""
@DataCommand.option("dirname", type=str, help="Path to damage calculator data files")
def load_damage_calc_data(dirname):
    # Load data from rocketmo's damage calculator
    # https://github.com/rocketmo/feh-damage-calc/
    logger = setup_command_logger()

    if not os.path.isdir(dirname):
        logger.error("Invalid directory")
        return

    def name_to_key(name):
        return name.replace('.js', '')

    files = ['assist.js', 'char.js', 'skill.js', 'special.js', 'weapon.js']
    game_data = {name_to_key(f): {} for f in files}

    for f in files:
        filepath = os.path.join(dirname, f)
        if not os.path.isfile(filepath):
            logger.error("Cannot find file: {}".format(f))
            return
        txt = open(filepath).read().strip()

        # get rid of leading characters
        txt = txt[txt.find('{'):]

        # get rid of trailing characters
        if txt[-1] == ';':
            txt = txt[:-1]

        game_data[name_to_key(f)] = json.loads(txt)

    movement_skills = set(['Drag Back',
                           'Escape Route 1',
                           'Escape Route 2',
                           'Escape Route 3',
                           'Hit and Run',
                           'Knock Back'])
    env = get_env()

    for slot, skills in game_data['skill'].items():
        for name, details in skills.items():
            skill = Skill()

            skill.slot = slot
            skill.name = name
            skill.description = details.get('description')
            skill.weapon_restrict = details.get('weapon_restrict')
            skill.color_restrict = details.get('color_restrict')
            skill.move_restrict = details.get('move_restrict')
            skill.weapon_unique = details.get('weapon_unique')
            skill.move_unique = details.get('move_unique')
            skill.range_unique = details.get('range_unique')
            skill.dragon_unique = details.get('dragon_unique')
            skill.char_unique = details.get('char_unique')
            skill.counter = details.get('counter')
            skill.recoil_damage = details.get('recoil_dmg')
            skill.cancel_effective = details.get('cancel_effective')
            skill.triangle_multiplier = details.get('tri_advantage')
            skill.no_follow = details.get('no_follow')

            for stat_mod in ['initiate_mod', 'stat_mod', 'defiant', 'seal', 'threaten']:
                if stat_mod in details:
                    for stat, boost in details[stat_mod].items():
                        if stat == "atk":
                            skill.mod_attack = boost
                        elif stat == "def":
                            skill.mod_defence = boost
                        elif stat == "res":
                            skill.mod_resistance = boost
                        elif stat == "spd":
                            skill.mod_speed = boost

                if stat_mod == 'initiate_mod':
                    skill.activation_player = True

                if stat_mod in ['seal', 'threaten']:
                    skill.mod_type = stat_mod
                # do something about defiant

            # TODO handle: type_defend_mod, hp_adv_mod, sweeps
            if 'breaker' in details:
                skill.weapon_effective = details['breaker']['weapon_type']
                skill.hp_threshold = details['breaker']['threshold']

            if name in movement_skills:
                skill.movement_skill = True

            for hp_conditional in ['desperation', 'riposte', 'vantage', 'wary']:
                if hp_conditional in details:
                    skill.hp_threshold = details[hp_conditional].get('threshold')

            if 'heal' in details:
                skill.self_healing_amount = details['heal']['amount']
                skill.self_healing_turns = details['heal']['turn_counter']

            env.graph.create(skill)

    for name, details in game_data['assist'].items():
            assist = Assist()
            assist.name = name
            assist.description = details.get('description')
            env.graph.create(assist)

    for name, details in game_data['special'].items():
            special = Special()
            special.name = name
            special.description = details.get('description')
            special.weapon_restrict = details.get('weapon_restrict')
            special.range_unique = details.get('range_unique')
            env.graph.create(special)

    for name, details in game_data['weapon'].items():
            weapon = Weapon()
            weapon.name = name
            weapon.description = details.get('description')
            weapon.color = details.get('color')
            weapon.weapon_type = details.get('type')
            weapon.might = details.get('might')
            weapon.rnge = details.get('range')
            weapon.poison = details.get('poison')
            weapon.initiate_heal = details.get('initiate_heal')
            weapon.initiate_poison = details.get('initiate_poison')
            weapon.full_hp_atk_recoil_dmg = details.get('full_hp_atk_recoil_dmg')
            weapon.heal_dmg = details.get('heal_dmg')

            weapon.char_unique = details.get('char_unique')
            weapon.move_effective = details.get('move_effective')
            weapon.color_effective = details.get('color_effective')
            weapon.dragon_effective = details.get('dragon_effective')
            weapon.spec_cooldown = details.get('spec_cooldown_mod')
            weapon.add_bonus = details.get('add_bonus')
            weapon.adjacent_ally_bonus = details.get('adjacent_ally_bonus')
            weapon.spec_damage_bonus = details.get('spec_damage_bonus')

            weapon.brave = details.get('brave')
            weapon.tri_advantage = details.get('tri_advantage')
            weapon.prevent_counter = details.get('prevent_counter')
            weapon.convert_penalties = details.get('convert_penalties')

            # handle riposte, breaker, defend_mod, seal, threaten, defiant, initiate_mod, target_seal
            # foe_full_hp_mod, after_mod, desperation, stat_threshold, vantage
            env.graph.create(weapon)

    for name, details in game_data['char'].items():
        char = Character()
        char.name = name
        char.weapon_type = details.get('weapon_type')
        char.move_type = details.get('move_type')

        build = Build()
        build.name = "Default {}".format(name)
        build.default = True
        char.build.add(build)

        for attribute in ['weapon', 'special', 'passive_a', 'passive_b', 'passive_c', 'assist']:
            items = details.get(attribute)
            if items is None:
                continue

            num_items = len(items)
            if attribute.startswith('passive'):
                node_label = 'Skill'
            else:
                node_label = attribute.capitalize()

            for i, item_name in enumerate(items):
                klass = globals()[node_label]
                node = klass.select(env.graph).where("_.name = '{}'".format(item_name.replace("'", "\\'"))).first()
                relation = getattr(build, attribute)
                relation.add(node, {"seq": num_items - i})

        # do base stats, rarity restricts?
        env.graph.push(char)

    logger.info("Success!")
"""


@DataCommand.option("dirname", type=str, help="Path to damage calculator data files")
def load_damage_calc_chars(dirname):
    logger = setup_command_logger()

    if not os.path.isdir(dirname):
        logger.error("Invalid directory")
        return
    filepath = os.path.join(dirname, 'char.js')
    if not os.path.isfile(filepath):
        logger.error("Cannot find file: {}".format('char.js'))
        return
    txt = open(filepath).read().strip()
    # get rid of leading characters
    txt = txt[txt.find('{'):]

    # get rid of trailing characters
    if txt[-1] == ';':
        txt = txt[:-1]

    game_data = json.loads(txt)
    env = get_env()

    def get_or_create_node(node_type, name):
        obj = node_type.select(env.graph, name).first()
        if obj is None:
            obj = node_type()
            obj.id = name
        return obj

    feh = get_or_create_node(Game, 'FireEmblemHeroes')
    feh.version = 1.3
    feh.number = 5

    for name, details in game_data.items():
        if details.get('color') is None:
            continue

        char = Character()
        char.id = name

        color = get_or_create_node(Color, details['color'])
        char.color.add(color)

        weapon_type = get_or_create_node(WeaponType, details['weapon_type'])
        char.weapon_type.add(weapon_type)

        move_type = get_or_create_node(MoveType, details['move_type'])
        char.move_type.add(move_type)

        for item_name in details['weapon']:
            node = get_or_create_node(Weapon, item_name)
            char.weapon.add(node)

        for item_name in details.get('special', []):
            node = get_or_create_node(Special, item_name)
            char.special.add(node)

        for item_name in details.get('assist', []):
            node = get_or_create_node(Assist, item_name)
            char.assist.add(node)

        for item_name in details.get('passive_a', []):
            node = get_or_create_node(PassiveSkill, item_name)
            node.slot = "A"
            char.passive_skill.add(node)

        for item_name in details.get('passive_b', []):
            node = get_or_create_node(PassiveSkill, item_name)
            node.slot = "B"
            char.passive_skill.add(node)

        for item_name in details.get('passive_c', []):
            node = get_or_create_node(PassiveSkill, item_name)
            node.slot = "C"
            char.passive_skill.add(node)

        feh.character.add(char)
    env.graph.push(feh)

    logger.info("Success!")


class GunicornServerCommand(Command):
    """
    Run the server using gunicorn
    """
    def __init__(self, host="127.0.0.1", port=5000, workers=1,
                 access_logfile="-", max_requests=0, debug=True, reload=False):
        self.options = {
            "host": host,
            "port": port,
            "workers": workers,
            "reload": False,
            "access_logfile": access_logfile,
            "max_requests": max_requests,
            "debug": debug,
        }

    def get_options(self):
        options = (
            Option("-H", "--host",
                   dest="host",
                   type=str,
                   default=self.options["host"],
                   help="hostname to bind server to"),
            Option("-p", "--port",
                   dest="port",
                   type=int,
                   default=self.options["port"],
                   help="port to bind server to"),
            Option("-w", "--workers",
                   dest="workers",
                   type=int,
                   default=self.options["workers"],
                   help="set the number of workers"),
            Option("--access-logfile",
                   dest="access_logfile",
                   type=str,
                   default=self.options["access_logfile"],
                   help="set the access log output location"),
            Option("--max-requests",
                   dest="max_requests",
                   type=int,
                   default=self.options["max_requests"],
                   help="set the maximum number of requests " +
                        "to serve before reloading"),
            Option("--no-debug",
                   dest="debug",
                   action="store_false",
                   default=self.options["debug"],
                   help="turn off debug mode"),
            Option("--reload",
                   dest="reload",
                   action="store_true",
                   default=self.options["reload"],
                   help="live-reload server when files change"),
        )
        return options

    def run(self, **kwargs):
        self.options.update(kwargs)
        if not kwargs.get("debug"):
            self.options["workers"] = multiprocessing.cpu_count() * 2 + 1

        options = self.options

        class GunicornServer(GunicornApplication):
            def init(self):
                config = {
                    "bind": "{0}:{1}".format(
                        options["host"],
                        options["port"]
                    ),
                    "workers": options["workers"],
                    "worker_class": "gevent",
                    "reload": options["reload"],
                    "accesslog": options["access_logfile"],
                    "max_requests": options["max_requests"],
                }
                return config

            def load(self):
                env = get_env()
                return env.application

            def load_config(self):
                # Overriding to prevent Gunicorn from reading
                # the command-line arguments
                self.cfg = GunicornConfig(self.usage, prog=self.prog)
                cfg = self.init()
                if cfg and cfg is not None:
                    for k, v in cfg.items():
                        self.cfg.set(k.lower(), v)

        GunicornServer().run()
