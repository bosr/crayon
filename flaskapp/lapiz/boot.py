# -*- coding: utf-8 -*-
"""
Boot module takes care of configuring and instantiating the app
"""
from flask import Flask
from .flaskrun import flaskrun
from .blueprints.root import root
from .blueprints.run import run
from .blueprints.backup import backup

app = Flask(__name__)  # pylint: disable=invalid-name
app.register_blueprint(root)
app.register_blueprint(run)
app.register_blueprint(backup)

flaskrun(app)
