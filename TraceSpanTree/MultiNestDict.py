import json

class MultiNestDict:    
    @staticmethod
    def expand(data):
        # 如果 data 不是 dict、list 或 str 这种可展开类型，直接返回
        if not isinstance(data, (dict, list, str)):
            return data
        
        # 如果是字符串，尝试将其解析为 JSON，
        # 如果解析得到 dict 或 list，递归展开，若是无法解析为 JSON，直接返回原始字符串
        if isinstance(data, str):
            try: 
                parsed_value = json.loads(data)
                if isinstance(parsed_value, (dict, list)):
                    return MultiNestDict.expand(parsed_value)
            except json.JSONDecodeError:
                return data
        
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = MultiNestDict.expand(value)
            return data
        
        if isinstance(data, list):
            return [MultiNestDict.expand(item) for item in data]
        
        return data

    @staticmethod
    def find_key(data, target_key, default = None):
        def recursive_search(d):
            if isinstance(d, (dict, list)):
                iterable = d.items() if isinstance(d, dict) else d
                for item in iterable:
                    k, v = item if isinstance(d, dict) else (None, item)
                    if k == target_key:
                        return v
                    result = recursive_search(v)
                    if result is not None:
                        return result
            return None
        return recursive_search(MultiNestDict.expand(data)) or default
    
    @staticmethod
    def update_key(data, target_key, val):
        def recursive_update(d):
            if isinstance(d, dict):
                if target_key in d:
                    d[target_key] = val
                    return True
                return any(recursive_update(v) for v in d.values())
            if isinstance(d, list):
                return any(recursive_update(item) for item in d)
            return False

        return recursive_update(MultiNestDict.expand(data))

    @staticmethod
    def update_key_batch(raw_dict, replace_dict):
        # NOTE: 使用 replace_dict 键值对批量更新 raw_dict 之中的键值对的，并返回更新后的结果。
        # NOTE: 仅当原始值、替换值都是 dict 时才会深度合并，否则直接用替换值覆盖。
        if raw_dict is None or replace_dict is None:
            return raw_dict or replace_dict
        
        # 先把原始和替换数据都递归 expand 成为真正的 dict / list / 基础类型
        raw_json = MultiNestDict.expand(raw_dict)
        replace_json = MultiNestDict.expand(replace_dict)

        def _merge_dicts(r, rep):
            result = {}
            for k, v in r.items():
                if k in rep:
                    if isinstance(v, dict) and isinstance(rep[k], dict):
                        result[k] = _merge_dicts(v, rep[k])
                    else:
                        result[k] = rep[k]
                else:
                    result[k] = v
            # rep 字典里面包含，但是 r 里面没有的 key 也要加进来
            for k, v in rep.items():
                if k not in r:
                    result[k] = v
            return result

        # 若二者都是 dict，则执行递归合并，否则直接用替换值覆盖
        if isinstance(raw_json, dict) and isinstance(replace_json, dict):
            return _merge_dicts(raw_json, replace_json)
        else:
            return replace_json
        

if __name__ == '__main__':
    nested_data = {
        'level1': {
            'level2': {
                'key1': 'value1',
                'key2': {'key3': 'value3'}
            },
            'level3': [
                {'key4': 'value4'},
                {'key5': 'value5'}
            ],
            'level6': '{"key6": "value6"}' 
        }
    }

    # NOTE 查找键值对
    v = MultiNestDict.find_key(nested_data, "key3")
    print(v)
    v = MultiNestDict.find_key(nested_data, "key5")
    print(v)
    v = MultiNestDict.find_key(nested_data, "key6")
    print(v)
    
    
    # NOTE 更新key-value 
    MultiNestDict.update_key(nested_data, target_key="level6", val = 'newval')
    print(json.dumps(nested_data, indent=4))
    MultiNestDict.update_key(nested_data, target_key="level1", val = 'newval')
    print(json.dumps(nested_data, indent=4))

    
    raw_data = {
        "a": {"nested": "value"},
        "b": 123,
        "c": "some string"
    }

    replace_data = {
        "a": {"nested": "new_value"},
        "d": [1, 2, 3]
    }

    # 批量更新
    updated = MultiNestDict.update_key_batch(raw_data, replace_data)
    print(json.dumps(updated, indent=4))
