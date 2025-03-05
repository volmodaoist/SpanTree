import json
from typing import Any



class MultiNestDict:    
    ''' 通过递归的方式展开数据，主要用于展开字符串格式的JSON或Dict
    '''
    @staticmethod
    def expand(data: dict) -> dict:
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
    def find_key(data:dict, target_key:str, default:Any = None, sep = '.') -> Any:
        ''' target_key 可以是多个key通过'.'连接在一起的序列，当这个子序列是根节点到目标节点的子序列时，
            能够实现缩小目标 key 范围的效果 (通常用于目标key存在同名的情况)
        ''' 
        def recursive_search(d, target_key):
            if isinstance(d, (dict, list)):
                iterable = d.items() if isinstance(d, dict) else d
                for item in iterable:
                    k, v = item if isinstance(d, dict) else (None, item)
                    if k == target_key:
                        return v
                    result = recursive_search(v, target_key)
                    if result is not None:
                        return result
            return None
        
        data, target_key_parts = MultiNestDict.expand(data), target_key.split(sep)
        for part in target_key_parts:
            val = recursive_search(data, part)
            data = val
            if data is None:
                break
        return val or default
    
    @staticmethod
    def update_key(data:dict, target_key:str, val) -> bool:
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
    def update_key_batch(raw_dict:dict, replace_dict:dict) -> dict:
        # NOTE: 使用 replace_dict 键值对批量更新 raw_dict 之中的键值对的，并返回更新之后的结果。
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

        # NOTE: 仅当原始值、替换值都是 dict 时才会深度合并，否则直接用替换值覆盖。
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
            'level6': '{"key6": "value6"}',
            'level5': {
                'key7-1': {'key8': 'k-78'},
                'key7-2': {'key8': 'k-88'},
            }
        }
    }

    # NOTE 查找键值对
    v = MultiNestDict.find_key(nested_data, "key3")
    print(v)
    v = MultiNestDict.find_key(nested_data, "key5")
    print(v)
    v = MultiNestDict.find_key(nested_data, "key6")
    print(v)
    v = MultiNestDict.find_key(nested_data, "key7-1.key8")
    print(v)
    v = MultiNestDict.find_key(nested_data, "key7-2.key8")
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
