import json


def deep_equal(input_json, output_json):
    return not json.dumps(input_json, sort_keys=True) == json.dumps(output_json, sort_keys=True)