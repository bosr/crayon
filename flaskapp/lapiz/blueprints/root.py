# -*- coding: utf-8 -*-
import requests
from flask import Blueprint, current_app, g, jsonify
from .. import tbclient

root = Blueprint('root', __name__)  # pylint: disable=invalid-name


@root.before_request
def before():
    g.version = current_app.config['version']
    g.tensorboard_folder = current_app.config['tensorboard_folder']
    g.tensorboard_url = current_app.config['tensorboard_url']


@root.route("/", methods=['GET'], strict_slashes=False)
@root.route("/status", methods=['GET'], strict_slashes=False)
def get_status():
    response = requests.get(g.tensorboard_url + '/data/logdir')

    if response.status_code != 200:
        return "Tensorboard server not responding at {}".format(g.tensorboard_url)

    response = response.json()
    if response.get("logdir") != g.tensorboard_folder:
        message = "Tensorboard running in an incorrect folder ({}) instead of {}"\
            .format(response.get("logdir"), g.tensorboard_folder)
        return message, 400

    message = "Tensorboard running at '{}' in folder '{}'"\
        .format(g.tensorboard_url, g.tensorboard_folder)
    return jsonify({
        'health': 'OK',
        'version': g.version,
        'message': message,
        'tensorboard': {
            'logdir': g.tensorboard_folder,
            'address': g.tensorboard_url,
        }
    })


@root.route('/plugins')
def get_plugins():
    active_supported_plugins = tbclient.active_plugins(g.tensorboard_url)
    return jsonify(active_supported_plugins), 200
