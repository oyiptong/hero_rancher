import collections
from datetime import datetime, date
import uuid
import json

from flask import Flask
from flask.json import JSONEncoder
from werkzeug.routing import BaseConverter, ValidationError

# ## settings and setup


def get_env():
    from hero_rancher.environment import Environment
    return Environment.instance()


class SettingsObj(object):
    def __init__(self, **settings):
        self.update(**settings)

    def update(self, orig=None, **settings):
        """
        Merge settings into current object
        """
        if orig is None:
            orig = self.__dict__

        for k, v in settings.items():
            if isinstance(v, collections.Mapping):
                updated = self.update(orig.get(k, {}), **v)
                orig[k] = updated
            else:
                orig[k] = settings[k]

        return orig

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __contains__(self, key):
        return self.__dict__.__contains__(key)

    def update_from_json_file(self, file_path):
        with open(file_path, "r") as config_file:
            config = json.load(config_file)
            self.update(**config)

# ## HTTP Utils


class ReverseProxied(object):
    """
    Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        proto = environ.get("HTTP_X_FORWARDED_PROTO", "")
        if proto == "https":
            environ["wsgi.url_scheme"] = proto

        return self.app(environ, start_response)


class StaticNoCacheFlask(Flask):
    """
    For debug purposes, when this app serves static content,
    set max age to 1 second
    """
    def get_send_file_max_age(self, name):
        if name:
            if (name.lower().endswith(".js") or
                name.lower().endswith(".html") or
                name.lower().endswith(".css")):  # noqa
                return 1
        return super(StaticNoCacheFlask, self).get_send_file_max_age(name)


class FakeMailExtension:
    def send(self, message):
        print(message)


def circular_list_generator(items):
    index = 0
    while True:
        yield items[index]
        index = (index + 1) % len(items)


class UUIDConverter(BaseConverter):
    """
    Converter for Flask to parse uuid's in url mappings
    """
    def to_python(self, value):
        try:
            return uuid.UUID(value)
        except ValueError:
            raise ValidationError()

    def to_url(self, value):
        return value.hex


# ## Serialization

class JSONEncoderPlus(JSONEncoder):
    """
    Extend Flask's JSON Encoder to include the date type
    """
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, uuid.UUID):
            return o.hex
        return JSONEncoder.default(self, o)


def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


def unix_time_millis(dt):
    return unix_time(dt) * 1000.0


def utcnow_millis():
    return unix_time_millis(datetime.utcnow())
