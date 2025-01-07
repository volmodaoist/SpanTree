import json
import random
import warnings
import concurrent.futures
from typing import Any, Dict, List, Optional, Callable, Union


class SpanTree:     
    def __init__(self, spans: List, super_id = None, sep = '.', keymaps: Dict = None):
        if spans is None or len(spans) == 0:
            warnings.warn("'spans' is empty. Please provide a non-empty list.", UserWarning)
            
        self._init_meta(spans, super_id, sep, keymaps)

    def expand_span(self, span: Dict):
        ''' 展开 span，递归地解析 JSON 字符串为字典。如果解析失败，保留原始值
        '''
        if not isinstance(span, dict):
            return span
        
        for key, value in span.items():
            if isinstance(value, str):
                try:
                    parsed_value = json.loads(value)
                    if isinstance(parsed_value, (dict, list)):
                        span[key] = self.expand_span(parsed_value)
                except json.JSONDecodeError:
                    pass  
            elif isinstance(value, dict):
                span[key] = self.expand_span(value)
            elif isinstance(value, list):
                span[key] = [self.expand_span(item) if isinstance(item, dict) else item for item in value]
        return span

    def _init_meta(self, spans: List, super_id = None, sep = '.', keymaps: Dict = None):
        ''' 1.  首先展开所有的 span，重建 spans 
            2.  然后初始化重要树结构基本信息，再对 spans 建树
        '''
        def _build_tree(spans: List, super_id = None):
            ''' 此处的建树，是以span粒度构建的，每个服务的调用会产生一个span，换句话说，每个树节点是一个span，树节点展开之后仍然是一棵树
                    - span_id: 通过 span_id 访问树节点所有内容
                    - parent_id: 通过 span_id 访问树节点的父节点
                    - son: 通过 span_id 访问每个树节点挂载的所有的孩子的节点
            '''
            # 维护每个节点的入度与出度，使用 span_id 作为key
            span_map, parent_map, sons = {}, {}, {}
            for span in spans:
                if isinstance(span, dict):
                    span_id = span.get("span_id")
                    parent_id = span.get("parent_id")
                    
                    span_map[span_id], parent_map[span_id] = span, parent_id
                    
                    if super_id and parent_id == super_id:
                        self.root = span
                        self.root_id = span_id
                        
                    # 初始化或更新子节点集合
                    if parent_id not in sons:
                        sons[parent_id] = set()
                    
                    sons[parent_id].add(span_id)
            
            ''' 如果用户没有指定树结构的超根节点 (根节点虚设的父节点称为超根节点)，则要手动寻找，规则如下:
                如果当前树节点的父节点没有父节点，说明这是一个根节点，具体方案: 
                    1. 循环遍历所有 spans 去找父节点不在 parent_map 里面的树节点，时间复杂度 O(N)
                    2. 随机选取一个 span 树节点，循环往上去找父节点，必然能够走到根节点、超根节点，时间复杂度 O(h), 其中h代表树高度
                    3. 直接通过集合相减的方式，直接拿到超根节点，代码写法最简洁，但是时间复杂度 O(M + N + min(M,N))， M 与 N 分别是非叶子结点、树节点key个数。
            '''
            
            if super_id is None and len(spans) > 0:
                random_span = random.choice(spans) 
                current_id = random_span.get("span_id")
                while current_id in parent_map:
                    parent_id = parent_map[current_id]
                    if parent_id not in parent_map:
                        self.root = span_map[current_id]
                        self.root_id = current_id
                        break
                    current_id = parent_id
                                            
            self.span_map, self.parent_map, self.sons = span_map, parent_map, sons
            
        # 初始化分割符信息
        self.sep = sep
        
        # 预处理Trace数据
        spans = self.setup_keys(spans, keymaps)
        spans = [self.expand_span(span) for span in spans]
        
        # 初始化SpanTree需要维护树上信息
        self.span_map = None
        self.root_id, self.root = None, None
        self.parent_map, self.sons = None, None
        
        # 建树
        _build_tree(spans, super_id)
        
        return self
        
            
    def _where_inner_subtree(self, subtree, target_part, idx: int = None):
        if isinstance(subtree, dict):
            if target_part in subtree:
                return subtree[target_part]
            for key, value in subtree.items():
                result = self._where_inner_subtree(value, target_part, idx)
                if result is not None:
                    return result

        elif isinstance(subtree, list):
            if idx is not None and -idx <= len(subtree) and idx < len(subtree):
                return self._where_inner_subtree(subtree[idx], target_part, idx)
            
            for item in subtree:
                result = self._where_inner_subtree(item, target_part, idx)
                if result is not None:
                    return result
    
        return None
    

    def _recursive_inner_search(self, span: Union[Dict, List], target_field: str, idx: int = None) -> Optional[Any]:
        ''' 函数作用: 在一个 span 内部递归搜索 target_key, 这个 target支持 '.' 约束。 idx 约束意思是说，是对List[Dict]而言的，
                    意思是说，只抓第idx个Dict元素里面的字段
        
            使用说明: 每个 span 内部展开也是一个树形结构，假设从根节点出发走到叶子节点的 key name 构成一个路径, 这条完整路径
                    记作: 'key1.key2.key3.key4.key5.key6'，那么 target_key 可以是这条路径的一个非连续子序列，
                    比如 'key1.key3.key5'，通过这个路径我们可以查找 key5 对应的 value
        '''
        subtree, parts = span, target_field.split(self.sep)
        for part in parts:
            if subtree is None or not isinstance(subtree, (list, dict)):
                break
            subtree = self._where_inner_subtree(subtree, part, idx)

        return subtree


    def _where_inter_subtree(self, subtree, target_span_key, is_type):
        span_name, span_type, span_id = subtree.get("name"), subtree.get("type"), subtree.get("span_id")
        if is_type:
            span_key = span_type
        else:
            span_key = span_name
        
        if span_key == target_span_key:
            return subtree
        
        for child_id in self.sons.get(span_id, []):
            child_span = self.span_map[child_id]
            result = self._where_inter_subtree(child_span, target_span_key, is_type)
            if result is not None:
                return result
            
        return None
    

    def _recursive_inter_search(self, target_span_name: str, is_type: Union[bool, List] = False) -> Optional[Any]:
        ''' 函数作用: 在一个 span 之间递归搜索 target_span_name, 这个 target 支持 '.' 约束
        
            使用说明: 整个 spans 展开之后是一棵树，假设从根节点出发走到叶子节点的 span name 构成一个路径，这条完整路径
                    记作: 'span1.span2.span3.span4.span5.span6'，那么 target_span 可以是这条路径的一个非连续子序列，
                    比如 'span_name1.span_name3.span_name5'，通过这个路径可以查到 span_name 对应的 span，如果设置了
                    is_type 则以 type 取代 name 进行搜索
        '''
        
        parts = target_span_name.split(self.sep)
        
        if not isinstance(is_type, (bool, list)): 
            raise TypeError(f"Expected 'is_type' to be of type bool or list, but got {type(is_type).__name__}.")

        if isinstance(is_type, list): 
            is_types = is_type  
        else:
            is_types = [is_type for _ in range(len(parts))]
        
             
        node = self.root
        for part, is_type in zip(parts, is_types):
            node = self._where_inter_subtree(node, part, is_type)
            if node is None:
                break
        return node



    def retrive(self, target_span_name: str, target_field, idx: int = None, is_type: bool = False, 
                callback: Callable = None):
        span = self._recursive_inter_search(target_span_name, is_type)
        value = self._recursive_inner_search(span, target_field, idx)
        
        if callback is not None:
            value = callback(value)
        
        return value

    def batch_retrive(self, configs):
        ''' 每个配置都要安装下面格式来写，其中每个待抓取字段含义如下所示: 
                - field_name : 待抓取字段的名称
                - default    : 待抓取字段的默认值，如果抓不到指定字段则用默认值替代
                - callback   : 待抓取字段的回调函数，找到相应字段之后通过这个函数对其进行处理

            {
                "[target_span_name]": {
                    "idx": None,                            `可选配置`: 通过索引约束List[Dict]类型的数据，只抓取第idx个元素的字段
                    "is_type": False,                       `可选配置`: 允许使用 Bool 或 List[Bool]，如果设为True, 则把 [span_name] 当做 [span_type] 来做匹配
                    "target_fields": [                      `必填配置`: 允许使用 List 或 Dict，按照三元组形式编写待抓取的字段，如果使用 Dict 会把 key 作为所抓字段的名字，若用List 则会按照默认规则取名
                        (target_field_name, default, callback),
                        (target_field_name, default, callback),
                        ...
                    ]
                },
                ...
            }
        '''

        results = {}  # 用于存储批量抓取的结果

        def process_one_span(target_span_name, cfg):
            span_results = {}
            
            idx = cfg.get("idx", None)
            is_type = cfg.get("is_type", False)
            target_fields = cfg.get("target_fields", [])

            if not target_fields:
                raise ValueError(
                    f"Configuration for '{target_span_name}' must include 'target_fields'. "
                    f"'target_fields' can be a list or a dict, and each entry must follow the format: "
                    f"(field_name, default, callback)."
                )


            if isinstance(target_fields, list):
                name_prefix = target_span_name.split(self.sep)[-1]
                target_fields = [(f"{name_prefix} {value[0].split(self.sep)[-1]}", *value) for value in target_fields]
                
            elif isinstance(target_fields, dict):
                target_fields = [(key, *value) for key, value in target_fields.items()]                
            

            for _, field in enumerate(target_fields):
                diy_name, target_field_name, default, callback = field

                try:
                    value = default
                    value_got = self.retrive(
                        target_span_name=target_span_name,
                        target_field=target_field_name,
                        idx=idx,
                        is_type=is_type,
                        callback=callback
                    )
                    if value_got is not None:
                        value = value_got
                except Exception as e:
                    print(f"Failed to retrieve '{target_field_name}' from span '{target_span_name}': {e}")
                
                span_results[diy_name] = value

            return span_results


        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_span = {
                executor.submit(process_one_span, target_span_name, cfg): target_span_name
                for target_span_name, cfg in configs.items()
            }

            for future in concurrent.futures.as_completed(future_to_span):
                target_span_name = future_to_span[future]
                try:
                    span_results = future.result()
                    results.update(span_results)  # 展开合并到 results
                except Exception as e:
                    print(f"Error processing span '{target_span_name}': {e}")

        return results




    def _get_ancestors(self, span_id: str) -> List[Dict]:
        ''' 获取指定 span_id 所有祖先节点。
        '''
        ancestors = []
        current_id = span_id
        while current_id in self.parent_map:
            parent_id = self.parent_map[current_id]
            parent_span = self.span_map.get(parent_id)
            if parent_span:
                ancestors.append(parent_span)
            current_id = parent_id
        return ancestors
    
    def setup_keys(self, spans, keymaps = None):
        ''' 用户传入的trace信息，其中的 spans 未必包含 name, span_id, parent_id 这些信息(有可能是名字的不同), 
            因此允许用户通过映射的方式调整每个 span 键名
        '''
        if keymaps is None:
            return spans
        
        required_keys = {"name", "span_id", "parent_id"}
        if not required_keys.issubset(keymaps.values()):
            raise ValueError("keymaps must contain mappings for 'name', 'span_id', and 'parent_id'.")
    
        remapped_spans = []
        reversed_keymaps = {v: k for k, v in keymaps.items()}
        
        for span in spans:
            remapped_span = {}
            for key, value in span.items():
                if key in reversed_keymaps:
                    remapped_span[reversed_keymaps[key]] = value
                else:
                    remapped_span[key] = value
            remapped_spans.append(remapped_span)

        return remapped_spans
    
    
    
    
    