from py2neo.ogm import GraphObject


def get_query(model, context):
    graph = getattr(model, 'graph', None)
    if not graph:
        graph = context.get('graph')
        if not graph:
            raise Exception('No graph Found')
    return model.select(graph)


def is_mapped(obj):
    return issubclass(obj, GraphObject)
