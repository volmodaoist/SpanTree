
import os
import json


# 本地缓存相应的文件
def cache_json(data, fname, file_dir):
    if file_dir is None:
        return
    os.makedirs(file_dir, exist_ok=True)
    output_file = os.path.join(file_dir, fname)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data


# 打开本地的json文件
def open_json(fname, file_dir):
    file_path = os.path.join(file_dir, fname)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {}
        

def is_cache(fname, file_dir):
    target_file = os.path.join(file_dir, fname)
    return os.path.exists(target_file) 
