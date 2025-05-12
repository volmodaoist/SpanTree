import json
import random
import warnings
import concurrent.futures

from typing import Any, Optional, Union
from collections.abc import Callable, Generator
from collections import OrderedDict

from tracespantree.utils.decorator import try_catch
from tracespantree.collections.kvtree import KVTree


class SpanTree:
    
    class SpanCache:
        def __init__(self, tree, max_size: int = 32):
            self._outter_tree = tree           # 引用外部的 SpanTree 对象
            self._cache_buf   = OrderedDict()  # 使用 OrderedDict 来保持插入顺序
            self._max_size    = max_size       # 设置缓存的最大大小

        def cache_key(self, target_span_name: Union[str, list]):
            if isinstance(target_span_name, list):
                return self._outter_tree.sep.join(target_span_name)
            return target_span_name
                
        # 添加缓存项
        def put(self, target_span_name, span):
            if self._max_size <= 0 or span is None:
                return self
            
            cv = span.get("span_id")      
            ck = self.cache_key(target_span_name)
            
            self._cache_buf[ck] = cv
            
            if len(self._cache_buf) >= self._max_size:
                self._cache_buf.popitem(last=False) 
            
            return self
            

        # 获取缓存项
        def get(self, target_span_name):
            span_id = self._cache_buf.get(target_span_name) 
            return self._outter_tree.span_map.get(span_id)
        
        def is_cache(self, target_span_name):
            ckey = self.cache_key(target_span_name)
            return ckey in self._cache_buf
        
    
    def __init__(self, spans: list = None, 
                       trace: dict = None, 
                       super_id: str = None,
                       sep: str = '.', 
                       keymaps: dict = None,
                       cache_size = 32):
        """ 用户只需要关心trace参数，传入Trace，自动建树，通过树上搜索增加trace抓取的灵活性

        :param spans:       Trace 里面的 spans 字段
        :param trace:       Trace 信息（如果不想手动提取span字段，可以直接传入整个trace）
        :param super_id:    树根节点，若不填写会自动分析哪个节点是树根，平时常用的 Doubao/Cici Trace 分析可忽略这个参数。
        :param sep:         分隔符，默认使用 '.' 进行分割，但是有一些 span name 会有 '.' 符号，这种情况我们可以修改默认的分隔符。
        :param cache_size:  缓存区大小，默认 32
        :param keymaps:     对于每个span必须 name, span_id, parent_id，如果使用其它名称，可以自己编写映射规则，
                            这个参数主要是为了通用性，平时 Doubao/Cici Trace 分析可以忽略这个参数。
        """
        
        if not spans and not trace: 
            raise ValueError("参数spans和trace至少要有一个不为空!")
        
        if trace is not None:
            spans = KVTree.find_key(trace, target_key="spans")

        # 初始化分割符信息
        self.sep = sep
        
        # 初始化SpanTree需要维护树上信息
        self.span_map     = None                        # 通过 span_id 获取整个span节点内容
        self.root         = None                        # 树根节点内容
        self.root_id      = None                        # 树根节点的 id
        self.parent_map   = None                        # 通过 span_id 访问其父节点id、
        self.sons         = None                        # 通过 span_id访问其所有孩子节点的 id
        self.components   = None                        # 树上联通分量的个数
        
        self._init_meta(spans, super_id, keymaps)
        self._cache_buf = SpanTree.SpanCache(tree = self, max_size=cache_size)


    def _init_meta(self, spans: list, super_id = None,  keymaps: dict = None):
        ''' 1.  首先展开所有的 span，重建 spans 
            2.  然后初始化重要树结构基本信息，再对 spans 建树
        '''
        def _build_tree(spans: list, super_id = None):
            ''' 此处的建树，是以span粒度构建的，每个服务的调用会产生一个span，换句话说，每个树节点是一个span，树节点展开之后仍然是一棵树
                    - span_id: 通过 span_id 访问树节点所有内容
                    - parent_id: 通过 span_id 访问树节点的父节点
                    - sons: 通过 span_id 访问每个树节点挂载的所有的孩子的节点，sons 是一个 dict[set] 结构
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
            
        
            self.components = []
            for span_id in span_map.keys():
                parent_id = parent_map.get(span_id)
                if parent_id not in span_map:
                    self.components.append(span_id)
            
        # 预处理 Trace 数据
        spans = self.setup_keys(spans, keymaps)
        spans = [self.expand_span(span) for span in spans]
        
        
        # 建树
        _build_tree(spans, super_id)
        
        
        return self
        
    
    def expand_span(self, span: dict):
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
 
    
    def get_parent(self, span = None, target_span_name: Union[str, list] = None, is_type: Union[bool, list] = False) -> dict:
        if not span and not target_span_name:
            raise Exception("参数 span 和 target_span_name 不可以同时为空！")
        
        # 如果传入 span 为空，则按 taget_span_name 规则查找
        span = span or self.retrieve_span(target_span_name, is_type)        
        
        span_id = span.get("span_id")
        parent_id = self.parent_map[span_id]
        return KVTree(self.span_map[parent_id])
    
    def get_sons(self, span = None, target_span_name: Union[str, list] = None, is_type: Union[bool, list] = False) -> Generator:
        if not span and not target_span_name:
            raise Exception("参数 span 和 target_span_name 不可以同时为空！")
        
        # 如果传入 span 为空，则按 taget_span_name 规则查找
        span = span or self.retrieve_span(target_span_name, is_type)        
        
        span_id = span.get("span_id")
        sons = self.sons[span_id]
        return (self.span_map[son_id] for son_id in sons)

    def get_ancestors(self, span_id: str) -> list[dict]:
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
 
       
    def _flatten_tags(self, span):
        """ 采用懒展开策略，只有当搜索了特定的 span 才会这个展开 span 并且获取其中关键的 tags 字段
            一旦展开 tags 将从 list 变成 dict，从而跳过下面的扁平化逻辑
        """
        if span is None:
            return span

        tags = span.get("tags", [])    
        span_id = span.get("span_id", None)
        
        if isinstance(tags, list):
            # 由于每个tag value字段仅有一个字典且这个字典仅有一个元素，可以使用迭代器获取包裹在内部的关键值
            tags = {tag.get("key"): next(iter(tag.get("value").values()))
                            for tag in tags}
            self.span_map[span_id]["tags"] = tags
            
        return self.span_map[span_id]
            
    def _where_inner_subtree(self, subtree, target_part, idx: int = None):
        if isinstance(subtree, dict):
            if target_part in subtree:
                return subtree[target_part]
            for _, value in subtree.items():
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
    

    def _recursive_inner_search(self, span: Union[dict, list], target_field: str, idx: int = None) -> Optional[Any]:
        ''' 函数作用: 在一个 span 内部递归搜索 target_key, 这个 target支持 '.' 约束。 idx 约束意思是说，是对List[Dict]而言的，
                    意思是说，只抓第idx个Dict元素里面的字段
        
            使用说明: 每个 span 内部展开也是一个树形结构，假设从根节点出发走到叶子节点的 key name 构成一个路径, 这条完整路径
                    记作: 'key1.key2.key3.key4.key5.key6'，那么 target_key 可以是这条路径的一个非连续子序列，
                    比如 'key1.key3.key5'，通过这个路径我们可以查找 key5 对应的 value
        '''
        
        if isinstance(target_field, list):
            parts = target_field
        else:
            parts = target_field.split(self.sep)
        
        subtree = span    
        for part in parts:
            if subtree is None or not isinstance(subtree, (list, dict)):
                break
            subtree = self._where_inner_subtree(subtree, part, idx)

        return subtree


    def _where_inter_subtree(self, subtree, target_span_key, is_type = False):
        """ 树上递归搜索，采用先宽后深的搜索策略，以此保证 target_span_name 序列存在歧义的时候，优先返回浅层的 span 节点  

        :param subtree:         搜索子树
        :param target_span_key: 树节点名称构成的约束序列
        :param is_type:         是否使用类型进行搜索
        """
        subtree = self._flatten_tags(subtree)
        span_name, span_type, span_id = subtree.get("name"), subtree.get("tags", {}).get("span_type"), subtree.get("span_id")
        
        if is_type:
            span_key = span_type
        else:
            span_key = span_name

        if span_key == target_span_key:
            return subtree
    
        # 当前层宽度优先搜索
        for child_id in self.sons.get(span_id, []):
            child_span = self.span_map[child_id]
            if is_type:
                child_span_key = child_span.get('type')
            else:
                child_span_key = child_span.get('name')
            if target_span_key == child_span_key:
                return child_span
        
        # 深度优先搜索
        for child_id in self.sons.get(span_id, []):
            child_span = self.span_map[child_id]
            result = self._where_inter_subtree(child_span, target_span_key, is_type)
            if result is not None:
                return result
            
        return None
    
    
    def _recursive_inter_search(self, target_span_name: Union[str, list], is_type: Union[bool, list] = False) -> Optional[Any]:
        ''' 函数作用: 在一个 span 之间递归搜索 target_span_name, 这个 target 支持 '.' 约束
        
            使用说明: 整个 spans 展开之后是一棵树，假设从根节点出发走到叶子节点的 span name 构成一个路径，这条完整路径
                    记作: 'span1.span2.span3.span4.span5.span6'，那么 target_span 可以是这条路径的一个非连续子序列，
                    比如 'span_name1.span_name3.span_name5'，通过这个路径可以查到 span_name 对应的 span，如果设置了
                    is_type 则以 type 取代 name 进行搜索
        '''
        
        if not is_type and self._cache_buf.is_cache(target_span_name):
            return self._cache_buf.get(target_span_name)
            
        if not isinstance(is_type, (bool, list)): 
            raise TypeError(f"Expected 'is_type' to be of type bool or list, but got {type(is_type).__name__}.")
        
        if isinstance(target_span_name, list):
            parts = target_span_name
        else:
            parts = target_span_name.split(self.sep)
        
        if isinstance(is_type, list): 
            is_types = is_type  
        else:
            is_types = [is_type for _ in range(len(parts))]
        
        # 一般情况只需考虑从根节点触发即可，但在发生断链之后，需要考虑所有联通分量
        if self.is_link_break():
            roots = (self.span_map[span_id] for span_id in self.components)
        else:
            roots = [self.root]

        node = None
        for r in roots:
            node = r
            for part, is_type in zip(parts, is_types):
                node = self._where_inter_subtree(node, part, is_type)
                if node is None:
                    break
            if node is not None:
                break

        node = self._flatten_tags(node)
        self._cache_buf.put(target_span_name=target_span_name, span = node)
        return node
        

    
    def retrieve_span(self, target_span_name: Union[str, list], is_type: Union[bool, list] = False):
        if not is_type and self._cache_buf.is_cache(target_span_name):
            return self._cache_buf.get(target_span_name)
        
        return KVTree(self._recursive_inter_search(target_span_name, is_type = is_type))

    def retrieve(self, target_span_name: Union[str, list], target_field: Union[str, list], callback: Callable = None, idx: int = None, is_type: Union[bool, list] = False):
        """
        param {str} target_span_name    Trace 里面我们期望抓取的 span 名称，若有多个span重名，我们可以使用 '.' 作为分隔符进行约束搜索，搜索规则详见下文
        param {str} target_field        Trace 里面我们期望抓取的 span 内部的某个字段，若有多个字段重名，我们可以使用 '.' 作为分隔符约束搜索，搜索规则详见下文
        param {int} idx                 如果填写了idx，那么搜索过程之中，遇到 list，我们只看 第idx个元素
        param {bool} is_type            如果填写了true，target_span_name 会按 span type 进行搜索，而不是按照 span name 进行搜索
        param {Callable} callback       对于抓取字段调用 callback 函数进行处理
        
        description: spans数组会被展开变成一棵树，从根节点到目标span节点，会有唯一的路径 [root, span1, span2, span3, ..., span5]，我们的搜索约束条件可以是这个路径的
                     任意子序列。使用搜索约束主要是为了避免重名的span造成干扰，举个例子。 如果存在重名的 span5，二者的路径: 
                        - [root, span1, span2, span3, ..., span5]
                        - [root, span1, span2, spanX, ..., span5]
                     
                     我们可以使用 span3.span5、spanX.span5 来区分上述两个span
        """ 
        span = self._recursive_inter_search(target_span_name, is_type)
        value = self._recursive_inner_search(span, target_field, idx)
        
        if callback is not None:
            decorated_callback = try_catch("Error occurred in Callback function")(callback)
            value = decorated_callback(value)
        
        return value

    
    def batch_retrieve(self, configs):
        """ 传入一个抓取配置，按照配置批量抓取

        :param configs: 配置参数，每个配置都要安装下面格式来写
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
            
            其中每个待抓取字段含义如下所示
                - target_field_name : 待抓取字段的名称
                - default           : 待抓取字段的默认值，如果抓不到指定字段则用默认值替代
                - callback          : 待抓取字段的回调函数，找到相应字段之后通过这个函数对其进行处理
        """
        
        # 存储批量抓取的结果
        results = {}  
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
                    # print(f"target_span_name = {target_span_name}, taget_fied_name = {target_field_name}")
                    value = default
                    value_got = self.retrieve(
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

        # 使用普通循环代替线程池，因为一次搜索耗时很短，完全没有必要并发
        for target_span_name, cfg in configs.items():
            try:
                span_results = process_one_span(target_span_name, cfg)
                results.update(span_results)
            except Exception as e:
                print(f"Error processing span '{target_span_name}': {e}")

        return results

   
    def get_components(self):
        """ 获取树上的所有联通分量的，
            通常联通分量只有一个，除非发生了断链的情况
        """               
        return self.components[:]
        
    def is_link_break(self):
        """ 检查是否存在断链的问题，断链通常是因 span 记录异常导致的，
            一旦出现断链，需要避免树上搜索退化
        """
        return len(self.get_components()) > 1

    def is_all_spans_ok(self):
        """ 检查是否所有树上的span节点状态码均正常
        """
        return any([span.get('status_code') == 0 for span in self.span_map.values()])
    
        
    def setup_keys(self, spans, keymaps = None):
        ''' 用户传入的trace信息，其中的 spans 未必包含 name, span_id, parent_id 这些信息(有可能是名字的不同), 
            因此允许用户通过映射的方式调整每个 span 键名，keymaps 含义与的构造函数相同
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