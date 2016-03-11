# -*- coding: utf-8 -*-
'''The app module, containing the app factory function.'''
from flask import Flask, render_template


def asset_path_context_processor():
    return {'asset_path': '/static/'}


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    register_errorhandlers(app)
    register_blueprints(app)
    app.context_processor(asset_path_context_processor)
    register_extensions(app)
    return app


def register_errorhandlers(app):

    def render_error(error):
        error_code = getattr(error, 'code', 500)
        return render_template("{}.html".format(error_code)), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)


def register_blueprints(app):
    from application.frontend.views import frontend
    app.register_blueprint(frontend)


def register_extensions(app):
    from application.assets import env
    env.init_app(app)

    from flask.ext.mongoengine import MongoEngine
    MongoEngine().init_app(app)
