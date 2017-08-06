# -*- coding: utf-8 -*-
import os
import shutil  # rmtree
import requests
from flask import Blueprint, current_app, g, jsonify, request
from .. import tbclient

run = Blueprint('run', __name__)


@run.before_request
def before():
    g.tensorboard_folder = current_app.config['tensorboard_folder']
    g.tensorboard_url = current_app.config['tensorboard_url']


@run.route("/runs", methods=['GET'], strict_slashes=False)
def get_all_runs():
    # folder_path = os.path.join(g.tensorboard_folder, runname)

    response = requests.get(g.tensorboard_url + '/data/runs')
    if response.status_code != 200:
        message = "Error while retrieving runs: {}".format(response.text)
        return message, 500
    runs_list = response.json()

    all_existing_runs = existing_runs(g.tensorboard_folder)
    empty_runs_list = [r for r in all_existing_runs if r not in runs_list]

    return jsonify({
        'runs': runs_list,
        'empty_runs': empty_runs_list,
    })


@run.route("/runs/<runname>", methods=['DELETE'], strict_slashes=False)
def delete_run(runname):
    all_existing_runs = existing_runs(g.tensorboard_folder)
    if runname not in all_existing_runs:
        message = "Unknown run: '{}'".format(runname)
        return message, 400

    if runname in tbclient.tf_summary_writers:
        tbclient.tf_summary_writers.pop(runname)

    folder_path = os.path.join(g.tensorboard_folder, runname)
    shutil.rmtree(folder_path)
    return '', 204


@run.route("/runs/<runname>", methods=['GET'], strict_slashes=False)
def get_run(runname):
    all_existing_runs = existing_runs(g.tensorboard_folder)
    if runname not in all_existing_runs:
        message = "Unknown run: '{}'".format(runname)
        return message, 400

    q_format = request.args.get('format', 'compact')
    q_plugins = request.args.get('plugins')
    if q_plugins:
        q_plugins = q_plugins.split(',')
    q_tags = request.args.get('tags', [])
    if q_tags:
        q_tags = q_tags.split(',')
    q_last = request.args.get('last', '-1')
    q_last = int(q_last)

    run_tags = tbclient.run_tags_per_plugin(g.tensorboard_url, runname)
    # e.g. {'scalars': ['accuracy', 'loss'], 'histograms': ['w_l1']}

    # keep requested plugins and tags
    requested_run_tags = {}
    for plugin, taglist in run_tags.items():
        if plugin in q_plugins:
            if q_tags:  # do not filter if q_tags is empty
                taglist = [tag for tag in taglist if tag in q_tags]
            requested_run_tags[plugin] = taglist

    # get samples for each plugin & each tag in the run
    data = {}
    for plugin, taglist in requested_run_tags.items():
        if not data.get(plugin):
            data[plugin] = {}
        for tag in taglist:
            url = g.tensorboard_url + '/data/plugin/' + plugin + '/' + plugin + '?run=' + runname + '&tag=' + tag
            response = requests.get(url)
            samples = response.json()
            if q_last != -1:
                samples = samples[-q_last:]
            data[plugin][tag] = samples

    # reformatting if needed
    if q_format == 'json':
        pass

    return jsonify(data), 200


@run.route("/runs/<runname>/tags", methods=['GET'], strict_slashes=False)
def get_tags(runname):
    all_existing_runs = existing_runs(g.tensorboard_folder)
    if runname not in all_existing_runs:
        message = "Unknown run: '{}'".format(runname)
        return message, 400

    run_tags = tbclient.run_tags_per_plugin(g.tensorboard_url, runname)
    return jsonify(run_tags), 200


@run.route("/runs/<runname>/event", methods=['POST'], strict_slashes=False)
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
