from operator import attrgetter
from flask import Blueprint
import graphene
from flask_graphql import GraphQLView
from hero_rancher.utils import get_env
from hero_rancher.graphene_py2neo import Py2NeoObjectType
from hero_rancher.objects import (
    Color as ColorModel,
    WeaponType as WeaponTypeModel,
    MoveType as MoveTypeModel,
    Weapon as WeaponModel,
    Special as SpecialModel,
    Assist as AssistModel,
    PassiveSkill as PassiveSkillModel,
    Character as CharacterModel,
    Game as GameModel,
)

env = get_env()
bp = Blueprint("graphql", __name__, url_prefix="/api")
root = GameModel.select(env.graph).where(id='FireEmblemHeroes').first()


class Color(Py2NeoObjectType):
    class Meta:
        model = ColorModel


class WeaponType(Py2NeoObjectType):
    class Meta:
        model = WeaponTypeModel


class MoveType(Py2NeoObjectType):
    class Meta:
        model = MoveTypeModel


class Weapon(Py2NeoObjectType):
    class Meta:
        model = WeaponModel


class Special(Py2NeoObjectType):
    class Meta:
        model = SpecialModel


class Assist(Py2NeoObjectType):
    class Meta:
        model = AssistModel


class PassiveSkill(Py2NeoObjectType):
    class Meta:
        model = PassiveSkillModel


class Character(Py2NeoObjectType):
    class Meta:
        model = CharacterModel


class Query(graphene.ObjectType):
    all_characters = graphene.List(Character,
                                   limit=graphene.Int(),
                                   id=graphene.String())

    def resolve_all_characters(self, args, context, info):
        query = Character.get_query(context)
        if args.get('limit'):
            query = query.limit(args.get('limit'))
        if args.get('id'):
            query = query.where(id=args.get('id'))
        return query


schema = graphene.Schema(query=Query)

bp.add_url_rule(
    "/gql",
    view_func=(
        env.csrf.exempt(
            GraphQLView.as_view(
                "graphql", schema=schema, graphiql=env.is_debug()))))
