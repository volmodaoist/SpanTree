import json


def open_json(fname, file_dir):
    try:
        with open(f"{file_dir}/{fname}.json") as f:
            f  = json.load(f)
        return f      
    except Exception as e:
        return {}