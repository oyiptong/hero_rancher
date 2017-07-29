#!/usr/bin/env python
from flask.ext.script import Server, Manager, Shell
from hero_rancher.commands import ListCommand, DataCommand, GunicornServerCommand
from hero_rancher.webapp import create_webapp

manager = Manager(create_webapp)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command('list', ListCommand)
manager.add_command('data', DataCommand)
manager.add_command('runserver_gunicorn', GunicornServerCommand())

if __name__ == "__main__":
    manager.run()
