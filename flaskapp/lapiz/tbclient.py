import requests
import tensorflow as tf

supported_plugins = ['scalars', 'histograms']

tf_summary_writers = {}


# def get_summary_writer(runname):
def get_summary_writer(runname, run_folder):
    if runname in tf_summary_writers:
        return tf_summary_writers[runname]

    writer = tf.summary.FileWriter(run_folder, flush_secs=1)
    tf_summary_writers[runname] = writer
    return writer


def write_summaries(runname, run_folder, json_payload):
    writer = get_summary_writer(runname, run_folder)

    wall_time = json_payload.get('wall_time')
    step = json_payload.get('step')

    summaries = []
    for jsum in json_payload['summaries']:
        if jsum.get('plugin') == 'scalar':
            s = tf.Summary.Value(tag=jsum['tag'], simple_value=jsum['value'])
        elif jsum.get('plugin') == 'histogram':
            s = tf.Summary.Value(tag=jsum['tag'], histo=jsum['histo'])
        summaries.append(s)

    summary = tf.Summary(value=summaries)
    event = tf.Event(wall_time=wall_time, step=step, summary=summary)
    writer.add_event(event)
    writer.flush()

    return True


def active_plugins(tensorboard_url):
    response = requests.get(tensorboard_url + '/data/plugins_listing')
    if response.status_code != 200:
        message = "Error while retrieving plugins: {}".format(response.text)
        return message, 500

    plugins = {plugin for plugin, active in response.json().items() if active}
    return list(plugins.intersection(supported_plugins))


def run_tags_per_plugin(tensorboard_url, runname):
    tags = {}
    for plugin in active_plugins(tensorboard_url):
        response = requests.get(tensorboard_url + '/data/plugin/' + plugin + '/tags')
        if response.status_code != 200:
            message = "Error while retrieving plugin '{}' data: {}".format(plugin, response.text)
            return message, 500
        tags[plugin] = response.json().get(runname, {})  # tags for the run
    return tags
