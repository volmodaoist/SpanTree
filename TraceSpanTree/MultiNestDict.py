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
    