# -*- coding: utf-8 -*-
from flask import Flask
from .flaskrun import flaskrun
from .blueprints.root import root
from .blueprints.run import run
from .blueprints.backup import backup

app = Flask(__name__)
app.register_blueprint(root)
app.register_blueprint(run)
app.register_blueprint(backup)

flaskrun(app)
