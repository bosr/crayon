# -*- coding: utf-8 -*-
import os
import shutil  # rmtree
import requests
from flask import Blueprint, current_app, g, jsonify, request
from .. import tbclient
from .. import helpers

run = Blueprint('run', __name__, url_prefix='/runs')  # pylint: disable=invalid-name


@run.before_request
def before():
    g.tensorboard_folder = current_app.config['tensorboard_folder']
    g.tensorboard_url = current_app.config['tensorboard_url']


@run.route("/", methods=['GET'], strict_slashes=False)
def get_all_runs():
    response = requests.get(g.tensorboard_url + '/data/runs')
    if response.status_code != 200:
        message = "Error while retrieving runs: {}".format(response.text)
        return message, 500
    runs_list = response.json()

    all_existing_runs = existing_runs(g.tensorboard_folder)
    empty_runs = list(set(all_existing_runs).difference(runs_list))

    return jsonify({
        'runs': runs_list,
        'empty_runs': empty_runs,
    })


@run.route("/<runname>", methods=['DELETE'], strict_slashes=False)
def delete_run(runname):
    if runname not in existing_runs(g.tensorboard_folder):
        return unknown_run(runname)

    if runname in tbclient.tf_summary_writers:
        tbclient.tf_summary_writers.pop(runname)

    folder_path = os.path.join(g.tensorboard_folder, runname)
    shutil.rmtree(folder_path)
    return '', 204


@run.route("/<runname>", methods=['GET'], strict_slashes=False)
def get_run(runname):
    if runname not in existing_runs(g.tensorboard_folder):
        return unknown_run(runname)

    q_format = request.args.get('format', 'compact')
    q_last = int(request.args.get('last', '-1'))
    q_plugins = request.args.get('plugins')
    q_plugins = q_plugins.split(',') if q_plugins else []
    q_tags = request.args.get('tags', '')
    q_tags = q_tags.split(',') if q_tags else []

    data = helpers.get_run_tags(g.tensorboard_url, runname, (q_plugins, q_tags, q_format, q_last))

    return jsonify(data), 200


@run.route("/<runname>/tags", methods=['GET'], strict_slashes=False)
def get_tags(runname):
    if runname not in existing_runs(g.tensorboard_folder):
        return unknown_run(runname)

    run_tags = tbclient.run_tags_per_plugin(g.tensorboard_url, runname)
    return jsonify(run_tags), 200


@run.route("/<runname>/event", methods=['POST'], strict_slashes=False)
def post_event(runname):
    folder_path = os.path.join(g.tensorboard_folder, runname)
    payload = request.get_json()

    status = tbclient.write_summaries(runname, folder_path, payload)
    return ('', 204) if status else ('Error', 500)


def existing_runs(tensorboard_folder):
    # also collect empty folders, which correspond to created runs with no events yet
    runs_list = []
    for _, dirs, _ in os.walk(tensorboard_folder):
        for run_directory in dirs:
            runs_list.append(run_directory)
    return runs_list


def unknown_run(runname):
    message = "Unknown run: '{}'".format(runname)
    return message, 404
