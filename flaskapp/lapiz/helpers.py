# -*- coding: utf-8 -*-
from collections import defaultdict
import requests
from . import tbclient


def get_run_tags(tensorboard_url, runname, requested):
    q_plugins, q_tags, q_format, q_last = requested
    run_tags = tbclient.run_tags_per_plugin(tensorboard_url, runname)
    # e.g. {'scalars': ['accuracy', 'loss'], 'histograms': ['w_l1']}

    # keep requested plugins and tags
    requested_run_tags = {}
    for plugin, taglist in run_tags.items():
        if (plugin in q_plugins) or not q_plugins:
            # do not filter if q_tags is empty
            requested_run_tags[plugin] = \
                [tag for tag in taglist if tag in q_tags] if q_tags else taglist

    # get samples for each plugin & each tag in the run
    data = defaultdict(dict)
    for plugin, taglist in requested_run_tags.items():
        for tag in taglist:
            url = '{tu}/data/plugin/{p}/{p}/?run={r}&tag={t}'\
                  .format(tu=tensorboard_url, p=plugin, r=runname, t=tag)
            samples = requests.get(url).json()
            # dot not filter if q_last == -1
            data[plugin][tag] = samples[-q_last:] if q_last != -1 else samples

    # reformatting if needed to json
    # from
    #
    # {
    # "scalars": {
    #   "accuracy": [
    #     [ 1502217057.323536, 7, 39.20000076293945 ],
    #
    # to
    #
    # {
    # "scalars": {
    #   "accuracy": [
    #     { "step": 7, "value": 39.20000076293945, "wall_time": 1502217057.323536 },

    if q_format == 'compact':
        return data

    json_data = defaultdict(dict)
    for plugin, tag_dict in data.items():
        for tag, samples in tag_dict.items():
            json_data[plugin][tag] = \
                [{'wall_time': s[0], 'step': s[1], 'value': s[2]} for s in samples]
    return json_data
