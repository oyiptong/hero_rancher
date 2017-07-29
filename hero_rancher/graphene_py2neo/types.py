import six
import inspect
from collections import OrderedDict
from graphene import Field, ObjectType
from graphene.relay import is_node
from graphene.types.objecttype import ObjectTypeMeta
from graphene.types.options import Options
from graphene.types.utils import merge, yank_fields_from_attrs
from graphene.utils.is_base_type import is_base_type
import py2neo
from .utils import get_query, is_mapped
from .registry import Registry, get_global_registry


class ResultNotFound(Exception):
    pass


from .converter import (convert_py2neo_property,
                        convert_py2neo_relationship)


def construct_fields(options):
    only_fields = options.only_fields
    exclude_fields = options.exclude_fields

    fields = OrderedDict()

    def is_property(obj):
        return obj.__class__ == py2neo.ogm.Property

    for name, prop in inspect.getmembers(options.model, is_property):
        is_not_in_only = only_fields and name not in only_fields
        is_already_created = name in options.fields
        is_excluded = name in exclude_fields or is_already_created
        if is_not_in_only or is_excluded:
            # We skip this field if we specify only_fields and is not
            # in there. Or when we excldue this field in exclude_fields
            continue
        converted_property = convert_py2neo_property(prop, options.registry)
        fields[name] = converted_property

    def is_relationship(obj):
        return obj.__class__ in (py2neo.ogm.RelatedTo, py2neo.ogm.RelatedFrom)

    # Get all the columns for the relationships on the model
    for name, relationship in inspect.getmembers(options.model, is_relationship):
        is_not_in_only = only_fields and name not in only_fields
        is_already_created = name in options.fields
        is_excluded = name in exclude_fields or is_already_created
        if is_not_in_only or is_excluded:
            # We skip this field if we specify only_fields and is not
            # in there. Or when we excldue this field in exclude_fields
            continue
        converted_relationship = convert_py2neo_relationship(relationship,
                                                             options.registry,
                                                             options.model)
        fields[name] = converted_relationship

    return fields


class Py2NeoObjectTypeMeta(ObjectTypeMeta):
    @staticmethod
    def __new__(cls, name, bases, attrs):
        if not is_base_type(bases, Py2NeoObjectTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=name,
            description=attrs.pop('__doc__', None),
            model=None,
            local_fields=None,
            only_fields=(),
            exclude_fields=(),
            id='id',
            interfaces=(),
            registry=None
        )

        if not options.registry:
            options.registry = get_global_registry()
        assert isinstance(options.registry, Registry), (
            'The attribute registry in {}.Meta needs to be an'
            ' instance of Registry, received "{}".'
        ).format(name, options.registry)
        assert is_mapped(options.model), (
            'You need to pass a valid Py2Neo Model in '
            '{}.Meta, received "{}".'
        ).format(name, options.model)

        cls = ObjectTypeMeta.__new__(cls, name, bases, dict(attrs, _meta=options))

        options.registry.register(cls)

        options.sqlalchemy_fields = yank_fields_from_attrs(
            construct_fields(options),
            _as=Field,
        )
        options.fields = merge(
            options.interface_fields,
            options.sqlalchemy_fields,
            options.base_fields,
            options.local_fields
        )

        return cls


class Py2NeoObjectType(six.with_metaclass(Py2NeoObjectTypeMeta, ObjectType)):

    @classmethod
    def is_type_of(cls, root, context, info):
        if isinstance(root, cls):
            return True
        if not is_mapped(type(root)):
            raise Exception((
                'Received incompatible instance "{}".'
            ).format(root))
        return isinstance(root, cls._meta.model)

    @classmethod
    def get_query(cls, context):
        model = cls._meta.model
        return get_query(model, context)

    @classmethod
    def get_node(cls, id, context, info):
        return cls.get_query(context).where(id=id).first()

    def resolve_id(self, args, context, info):
        graphene_type = info.parent_type.graphene_type
        if is_node(graphene_type):
            keys = self.__mapper__.primary_key_from_instance(self)
            return tuple(keys) if len(keys) > 1 else keys[0]
        return getattr(self, graphene_type._meta.id, None)
