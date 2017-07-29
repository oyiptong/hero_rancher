import os
from typing import TypeVar
from flask import Flask
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from py2neo import Graph

import hero_rancher.default_settings as settings
from hero_rancher.utils import (
    SettingsObj,
    StaticNoCacheFlask,
    UUIDConverter,
    FakeMailExtension,
)


class EnvironmentUninitializedError(Exception):
    pass


T = TypeVar('T', bound='Environment')
F = TypeVar('F', bound='Flask')


class Environment(object):
    _instance = None

    @classmethod
    def read_configuration(cls, config_filename: str = None) -> SettingsObj:
        """
        Load configuration from different sources.
        In order of precedence:

        1. environment variables
        2. in /etc/hero_rancher/settings.json
        2. settings.json file in an expected path
        3. external json file specified by command-line
        4. defaults in settings.py

        The expected path is at one directory level before this file
        """
        config_obj = SettingsObj()

        # defaults
        config_obj.__dict__.update(settings.__dict__)

        # external JSON
        if config_filename is not None and os.path.isfile(config_filename):
            config_obj.update_from_json_file(config_filename)

        # json file in expected paths
        expected_paths = [
            os.path.join(os.path.dirname(__file__), "../settings.json"),
            "/etc/hero_rancher/settings.json",
        ]
        for path in expected_paths:
            if os.path.isfile(path):
                config_obj.update_from_json_file(path)

        # environment variables
        if "ENV" in os.environ:
            config_obj.server.environment = os.environ["ENV"]

        return config_obj

    @classmethod
    def instance(cls, test: bool = False, test_db_uri: str = None, *args, **kwargs) -> T:
        if cls._instance is None:
            config = cls.read_configuration()
            cls._instance = cls(config, test, test_db_uri)

        return cls._instance

    def __init__(self,
                 config: SettingsObj,
                 test: bool = False,
                 test_db_uri: str = None,
                 *args, **kwargs) -> T:
        if self.__class__._instance is not None:
            raise EnvironmentUninitializedError(
                "Environment should only be initted once")

        self.config = config
        if test:
            self.config.server["environment"] = "test"

        # Application server setup
        self.__application = self.__get_server_instance()

        self.__application.debug = self.is_debug
        self.__application.secret_key = self.config.server["secret_key"]
        self.__application.server_name = self.config.server["server_name"]
        self.__application.url_map.converters['uuid'] = UUIDConverter

        # Setup Flask-Security
        for key, val in self.config.server["security"].items():
            if type(val) == bytes:
                val = str(val)
            self.__application.config[key] = val

        self.__application.extensions["mail"] = FakeMailExtension()

        # Setup py2neo
        self.graph = Graph(**self.config.py2neo)

    def __get_server_instance(self) -> F:
        if self.is_development:
            server_class = StaticNoCacheFlask
        else:
            server_class = Flask

        application = server_class(
            'hero_rancher',
            template_folder=self.config.server["template_dir"],
            static_folder=self.config.server["static_dir"],
        )

        CORS(application)
        self.csrf = CSRFProtect()
        self.csrf.init_app(application)

        return application

    def is_development(self) -> bool:
        return self.config.server["environment"] == "dev"

    def is_debug(self) -> bool:
        return self.config.server["debug"]

    @property
    def application(self) -> F:
        return self.__application
