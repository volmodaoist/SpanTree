import json
from typing import Any, Union


""" 特性梳理:
    1. 一个多层嵌套字典可以视为一棵树，由于 dict 不存在同名的 key，因此 KVTree 同一个层级不存在重名的子节点
    
    2. 如果这个字典的所有 key 均不同名，我们只要给定一个 key 即可对应的 value，由于树结构的每一层均为字典，因此每层查找key复杂度均为 O(1)，
       查找目标节点的整体复杂度仅有 O(h)，其中 h 代表目标节点所处树深度。
       
    3. 对于任意树结构，树根节点走到目标节点的路径是唯一的，这个路径key看成若干 key 构成的序列，我们记作 kpath
    
    4. 如果这个字典存在同名的节点（同名key） ，那么这些 key 必然位于不同层，因此我们可以通过 kpath 子序列作为约束条件，搜索我们想要找到的 key-value。
"""



class KVTree(dict):    
    ''' 通过递归的方式展开数据，能够展开字符串格式的JSON或Dict，展开之后的字典可以视为一棵树
        用户直接传入 key 即可搜索对应的 value，若有重名value，用户可以使用多个 key1.key3.key5 构成的子序列进行约束
        子序列搜索目标 value
    '''
    def __init__(self, data: Union[str, list[dict], dict], sep:str = '.'):
        self.sep = sep
        self.data = self.expand(data)
        self._pretty_str = None
        

    def __getitem__(self, key: Union[list, str]) -> Any:
        """ 重写 __getitem__ 方法，以便通过字符串路径（例如 'key1.key2.key3'）访问嵌套数据，默认行为等同于字典
        """
        res = self.find_key(self.data, target_key=key) 
        if res is None:
            raise KeyError(f"Key: {key} was Not Found!")
        return res
    
    def __str__(self):
        return self.data.__str__()
    

    @property
    def pretty_str(self):
        """ 获取格式化的树形字符串 """
        if self._pretty_str is not None:
            return self._pretty_str
        self._pretty_str = self._recursive_pretty_str(self.data, level=0)
        return self._pretty_str
    
    def _recursive_pretty_str(self, data, level: int = 0) -> str:
        """ 递归地将字典数据格式化为树形结构字符串 
            每层增加四个空格的缩进来确保可读性
        """
        result = list()
        indent = "    " * level  
        for key, value in data.items():
            if isinstance(value, dict):
                result.append(f"{indent}{key}:\n{self._recursive_pretty_str(value, level + 1)}")
            elif isinstance(value, list):
                result.append(f"{indent}{key}:\n")
                for item in value:
                    if isinstance(item, dict):
                        result.append(self._recursive_pretty_str(item, level + 1))
                    else:
                        result.append(f"{indent}    {item}\n")
            else:
                result.append(f"{indent}{key}: {value}\n")
        return str().join(result)
    
    
    def __setitem__(self, key: Union[str, list], val: Any) -> None:
        """ 重写 __setitem__ 方法，支持通过字符串路径设置嵌套字典的值 """
        self.update_key(self.data, target_key=key ,val=val)
        
    def get(self, key: Union[list, str], default: Any = None) -> Any:
        """ 重写 get 方法，以便通过字符串路径（例如 'key1.key2.key3'）访问嵌套数据
        
        :param key: 键值序列，用以查询 key 对应的 value
        :param default: 默认值，如果查找不到 key 对应的 value, 反应 None
        """
        val, data, parts = None, self.data, KVTree._split_key(key, self.sep)
        for part in parts:
            val = self._recursive_search(data, part)
            data = val
            if data is None:
                break
        return val or default
    
    def put(self, key: str, val: Any) -> Any:
        """ 
        :param key: 需要更新的 key，不支持重复key，不支持子序列约束
        :param val: 需要更新的 value

        """
        self._recursive_update(self.data, target_key=key ,val=val)
        return self

    @staticmethod
    def _split_key(key: Union[list, str], sep: str = '.'):
        if isinstance(key, list):
            return key
        return key.split(sep)
          
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
                    return KVTree.expand(parsed_value)
            except json.JSONDecodeError:
                return data
        
        elif isinstance(data, dict):
            for key, value in data.items():
                data[key] = KVTree.expand(value)
            return data
        
        elif isinstance(data, list):
            return [KVTree.expand(item) for item in data]
        

    @staticmethod
    def _recursive_search(d, target_key):
        if isinstance(d, dict):
            if target_key in d:
                return d[target_key]
            for v in d.values():
                res = KVTree._recursive_search(v, target_key)
                if res is not None:
                    return res
        elif isinstance(d, list):
            for x in d:
                res = KVTree._recursive_search(x, target_key)
                if res is not None:
                    return res
        return None
    
    @staticmethod
    def _recursive_update(d, target_key, val):
        if isinstance(d, dict):
            if target_key in d:
                d[target_key] = val
                return True
            return any(KVTree._recursive_update(v, target_key, val) for v in d.values())
        if isinstance(d, list):
            return any(KVTree._recursive_update(item, target_key, val) for item in d)
        return False
        
    @staticmethod
    def find_key(data:dict, target_key:str, default: Any = None, sep = '.') -> Any:
        ''' target_key 可以是多个key通过'.'连接在一起的序列，当这个子序列是根节点到目标节点的子序列时，
            能够实现缩小目标 key 范围的效果 (通常用于目标key存在同名的情况)
        ''' 
        val, data, target_key_parts = None, KVTree.expand(data), target_key.split(sep)
        for part in target_key_parts:
            val = KVTree._recursive_search(data, part)
            data = val
            if data is None:
                break
        return val or default
    
    @staticmethod
    def update_key(data:dict, target_key:str, val) -> bool:
        return KVTree._recursive_update(KVTree.expand(data), target_key, val)
    

    @staticmethod
    def update_batch_keys(raw_dict:dict, replace_dict:dict) -> dict:
        # NOTE: 使用 replace_dict 键值对批量更新 raw_dict 之中的键值对的，并返回更新之后的结果。
        if raw_dict is None or replace_dict is None:
            return raw_dict or replace_dict
        
        # 先把原始和替换数据都递归 expand 成为真正的 dict / list / 基础类型
        raw_json = KVTree.expand(raw_dict)
        replace_json = KVTree.expand(replace_dict)

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

        # NOTE: 仅当原始值、替换值都是 dict 才会深度合并，否则直接用替换值覆盖。
        if isinstance(raw_json, dict) and isinstance(replace_json, dict):
            return _merge_dicts(raw_json, replace_json)
        else:
            return replace_json
        

MultiNestDict = KVTree

    

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
    v = KVTree.find_key(nested_data, "key3")
    print(v)
    v = KVTree.find_key(nested_data, "key5")
    print(v)
    v = KVTree.find_key(nested_data, "key6")
    print(v)
    v = KVTree.find_key(nested_data, "key7-1.key8")
    print(v)
    v = KVTree.find_key(nested_data, "key7-2.key8")
    print(v)
    
    vt = KVTree(nested_data)
    print(vt.get("key3"))	# 结果: value3
    print(vt.get("key5"))	# 结果: value5
    
    # NOTE 更新key-value 
    KVTree.update_key(nested_data, target_key="level6", val = 'newval')
    print(json.dumps(nested_data, indent=4))
    KVTree.update_key(nested_data, target_key="level1", val = 'newval')
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
    updated = KVTree.update_batch_keys(raw_data, replace_data)
    print(json.dumps(updated, indent=4))
