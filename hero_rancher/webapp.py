import traceback
from hero_rancher.environment import Environment


def setup_routes(env):
    app = env.application
    try:
        from hero_rancher.api.graphql import bp as graphql_blueprint
        app.register_blueprint(graphql_blueprint)
    except Exception as e:
        traceback.print_exc()


def create_webapp(*args, **kwargs):
    env = Environment.instance()

    setup_routes(env)
    return env.application
