from hero_rancher.utils import get_env


def purge_database():
    env = get_env()
    env.graph.delete_all()
