# TraceSpanTree 项目说明

开发者们，你们好！🚀 是否厌倦了在项目中处理复杂的嵌套追踪数据？有时候JSON转为字典之后，需要连续好几个括号才能取出其中的value，而当研发代码变动，导致JSON结构层级关系变更的时候，自动化代码又要全部维护一遍！现在，**TraceSpanTree** 来帮您解决难题啦！

快速安装：

```shell
pip install -i https://test.pypi.org/simple/ TraceSpanTree==0.1.3
```

如果觉得不错，给我们点个 ⭐ 收藏吧！ ，让我们一起简化自动化代码编写、调用链路分析与追踪的工作！


## 😎 简介
**TraceSpanTree** 是一个 Python 三方库的，旨在简化处理复杂的分层追踪数据。在项目执行（或者调试）过程中，通常会有JSON 格式存储的调用链路数据。管理嵌套的键值对并编写断言可能会很繁琐，尤其是当数据结构频繁变化时。我们的目标是提供一种高效的方式来管理追踪数据，降低代码复杂度和维护成本。现在，借助 **TraceSpanTree**，您可以轻松地在多层嵌套字典和跨度结构中查找、更新和检索键值对。



## 🚀 功能概述

**TraceSpanTree** 库包含以下核心组件：

1. **`Log`**：简化的日志工具，可高效跟踪追踪操作。
2. **`MultiNestDict`**：支持在深度嵌套字典中轻松检索和更新数据。
3. **`SpanTree`**：便于在复杂的追踪层级结构中搜索和检索值。
4. **`TraceGen`**：通过 `@tracer.trace_gen` 装饰器为 `Tracer` 对象提供功能，以根据函数调用自动生成跨度树。



🌳 跨度树的概念
可以将追踪数据想象成一种树形结构，其中：
- 每个节点（跨度）代表来自特定服务的操作数据。
- 每个跨度都存储为一个 JSON 对象，其本身也可视为一棵树。

最终形成的是一种 “树套树” 模型，在这个树套树上面搜索key-value能够帮助我们更高效地浏览追踪数据。通过利用这种数据结构，TraceSpanTree 提供了强大的工具，可定位和操作任意层级的数据。


## 🛠️ 核心功能实现

SpanTree 主要功能由以下两个函数实现：

### 跨跨度约束

`_recursive_inter_search` 函数旨在帮助您在跨度树中导航：

- **函数描述**：它在跨度树中递归搜索 `target_span_name`。`target_span_name` 支持 “.” 约束，当您试图在复杂的树形结构中精确定位特定跨度时，这个功能非常实用。 

- **用法说明**：当展开整个跨度集时，会形成一棵树。想象一下，您从根节点走到叶节点，跨度的名称形成一条路径，如 `'span1.span2.span3.span4.span5.span6'`。在这种情况下，`target_span` 可以是这条路径的非连续子序列，例如 `'span_name1.span_name3.span_name5'`。通过使用此路径，您可以定位与 `span_name` 对应的跨度。此外，如果设置了 `is_type` 参数，搜索将使用跨度类型而不是名称进行。 

### 内部跨度约束

`_recursive_inner_search` 函数专注于在单个跨度内进行探索：

- **函数描述**：它在单个跨度内递归搜索 `target_key`。`target_key` 同样支持 “.” 约束。`idx` 参数对于 `List[Dict]` 结构很有用，可让您仅针对第 `idx` 个 `Dict` 元素内的字段进行操作。 

- **用法说明**：当查看单个跨度内部时，它也形成一种树状结构。假设您在跨度内从根节点遍历到叶节点，键的名称形成一条路径，如 `'key1.key2.key3.key4.key5.key6'`。那么，`target_key` 可以是这条路径的非连续子序列，比如 `'key1. key3. key5'`。通过这条路径，您可以找到与 `key5` 对应的 value。 



##  🧰 用户关键函数
###   `retrive` 函数

此函数是 SpanTree 中用于检索特定数据的关键工具之一。它利用了跨跨度和内部跨度约束，使您更轻松地访问所需的值。例如：

```python
res1 = spantree.retrive(target_span_name='root.father_span_1.leaf_span_1', 
                        target_field='data.message')
res2 = spantree.retrive(target_span_name='root.leaf_span_1', 
                        target_field='data.message')
res3 = spantree.retrive(target_span_name='root.leaf_span_1', 
                        target_field='message')
```

只需简单调用此函数，您就可以高效地在复杂的树形结构中导航，并获取所需的值。我们力求使其尽可能简单易用，但也知道每个用户的用例可能不同。如果您遇到任何困难或有改进的想法，请随时联系我们。 



### `batch_retrive` 函数

当您要从 SpanTree 不同部分检索多个值时，可以使用 `batch_retrive` 函数。通过适当的设置进行配置，一次性获取各种数据。这在需要同时验证多个方面的综合测试场景中特别有用: 


## 用法示例 📝

下面通过一些示例数据，更详细地了解如何使用 SpanTree。首先，考虑以下以 JSON 格式表示的 `spans` 结构：

```json
{
  "spans": [
    {
      "name": "root",
      "type": "root",
      "span_id": "1",
      "parent_id": "0",
      "state_code": 0,
      "data": {
        "message": "这是根跨度。",
        "timestamp": "2024-01-01T00:00:00Z"
      }
    },
    {
      "name": "father_span_1",
      "type": "father",
      "span_id": "2",
      "parent_id": "1",
      "state_code": 0,
      "data": {
        "message": "这是根跨度下的子跨度。",
        "timestamp": "2024-01-01T00:00:10Z"
      }
    },
    {
      "name": "leaf_span_1",
      "type": "leaf",
      "span_id": "3",
      "parent_id": "2",
      "state_code": -1,
      "data": {
        "message": "这是 father_span_1 下的叶跨度。",
        "timestamp": "2024-01-01T00:00:15Z"
      }
    },
    {
      "name": "father_span_2",
      "type": "father",
      "type": "father",
      "span_id": "5",
      "parent_id": "1",
      "state_code": 0,
      "data": {
        "message": "这是根跨度下的子跨度。",
        "timestamp": "2024-01-01T00:00:30Z"
      }
    },
    {
      "name": "leaf_span_2",
      "type": "leaf",
      "span_id": "6",
      "parent_id": "5",
      "state_code": -1,
      "data": {
        "message": "这是 father_span_2 下的叶跨度。",
        "timestamp": "2024-01-01T00:00:35Z"
      }
    }
  ]
}
```

您可以很轻松地在此数据上使用 `retrive` 函数。例如：

```python
res1 = spantree.retrive(target_span_name='root.father_span_1.leaf_span_1', 
                        target_field='data.message')

res2 = spantree.retrive(target_span_name='root.leaf_span_1', 
                        target_field='data.message')


res3 = spantree.retrive(target_span_name='root.leaf_span_1',
                       target_field='message')

# 在这个示例中，res1、res2、res3 的值相同。
```

现在，进一步扩展我们的示例。考虑一个更复杂的 `spans` 结构：

```json
{
    "spans": [
        {
            "name": "root",
            "type": "root",
            "span_id": "1",
            "parent_id": "0",
            "state_code": 0,
            "input": {
                "param_str": "123",
                "param_int": 123
            },
            "output": [
                {
                    "result_key": "root_result_value, idx = 0",
                    "sub_result": [
                        {
                            "sub_key": "root_sub1_value, idx = 0"
                        }
                    ]
                },
                {
                    "result_key": "root_result_value, idx = 1",
                    "sub_result": [
                        {
                            "sub_key": "root_sub_value, idx = 1"
                        }
                    ]
                }
            ]
        },
        {
            "name": "father_span_1",
            "type": "father",
            "span_id": "2",
            "parent_id": "1",
            "state_code": 0,
            "input": {
                "param_str": "456",
                "param_int": 456
            },
            "output": [
                {
                    "result_key": "father_result_value",
                    "sub_result": [
                        {
                            "sub_key": "father_sub_value"
                        }
                    ]
                }
            ]
        },
        {
            "name": "leaf_span_1",
            "type": "leaf",
            "span_id": "3",
            "parent_id": "2",
            "state_code": -1,
            "input": {
                "param_str": "789",
                "param_int": 789
            },
            "output": [
                {
                    "result_key": "leaf1_result_value, idx = 0",
                    "sub_result": [
                        {
                            "sub_key": "leaf1_sub_value, idx = 0"
                        }
                    ]
                },
                {
                    "result_key": "leaf1_result_value, idx = 1"
                }
            ]
        },
        {
            "name": "father_span_2",
            "type": "father",
            "span_id": "4",
            "parent_id": "1",
            "state_code": 0,
            "input": {
                "param_str": "1011",
                "param_int": 1011
            },
            "output": [
                {
                    "result_key": "father2_result_value",
                    "sub_result": [
                        {
                            "sub_key": "father2_sub_value"
                        }
                    ]
                }
            ]
        },
        {
            "name": "leaf_span_2",
            "type": "leaf",
            "span_id": "5",
            "parent_id": "4",
            "state_code": -1,
            "input": {
                "param_str": "1213",
                "param_int": 1213
            },
            "output": [
                {
                    "result_key": "leaf2_result_value, idx = 0",
                    "sub_result": [
                        {
                            "sub_key": "leaf2_sub_value, idx = 0"
                        }
                    ]
                },
                {
                    "result_key": "leaf2_result_value, idx = 1"
                }
            ]
        }
    ]
}
```

以下是如何使用 `batch_retrive` 函数处理更全面的数据提取：

```python
  configs = {
      "root": {
          "idx": None,
          "is_type": False,
          "target_fields": [
              ("input.param_str", "default_root_param_str", lambda x: x),
              ("input.param_int", "default_root_param_int", lambda x: x)
          ]
      },
      "father_span_1": {
          "idx": None,
          "is_type": False,
      "target_fields": [
              ("input.param_str", "default_father1_param_str", lambda x: x),
              ("input.param_int", "default_father1_param_int", lambda x: x)
          ]
      },
      "leaf_span_1": {
          "idx": 0,
          "is_type": False,
          "target_fields": [
              ("input.param_str", "default_leaf1_param_str", lambda x: x),
              ("input.param_int", "default_leaf1_param_int", lambda x: x),
              ("result_key", "default_result_key", lambda x: x)
          ]
      },
      "leaf_span_2": {
          "idx": 1,
          "is_type": False,
      "target_fields": [
              ("input.param_str", "default_leaf1_param_str", lambda x: x),
              ("input.param_int", "default_leaf1_param_int", lambda x: x),
              ("result_key", "default_result_key", lambda x: x)
          ]
      }
  }
  results = spantree.batch_retrive(configs)
```

对于 `batch_retrive` 函数来说，`configs` 是一个至关重要的配置字典。

以 `configs` 中的一个 `target_span_name`（例如 `"root"`）为例：
- `idx`（可选）：对于 `List[Dict]` 数据，设置一个值可仅从第 `idx` 个元素中检索字段。如果为 `None`，则无索引限制。
- `is_type`（可选）：默认值为 `False`。设置为 `True` 时，将使用 `[span_name]` 作为 `[span_type]` 来匹配目标跨度。
- `target_fields`（必填）：这是一个元组列表，格式为 `(target_field_name, default, callback)`。
  - `target_field_name`：要检索的字段名称，例如 `"input.param_str"`，指定层级结构。
  - `default`：如果未找到该字段时的回退值，需与字段类型匹配。
  - `callback`：一个 lambda 函数，用于处理检索到的字段值。

这样，无论您是使用简单的 `retrive` 函数快速访问特定值，还是使用功能更强大的 `batch_retrive` 函数一次性处理多个数据提取，SpanTree 都提供了一种便捷高效的方式来与分层数据进行交互。我们希望它能让您的测试工作更高效、更少出错，但如果您认为有可以改进的地方，我们随时欢迎反馈。毕竟，我们共同的目标是让测试工作流程更顺畅、更有效！ 😃 






## 📑 结论 
SpanTree 是我们为质量保证工程师和测试开发工程师简化测试脚本中分层数据处理过程所做的尝试。我们在其设计和功能上投入了大量的思考，但也深知还有很多需要学习和改进的地方。希望通过利用它的特性和功能，您能更多地专注于实际的测试逻辑，而不是被复杂的数据访问和维护问题所困扰。如果您决定在项目中试用它，我们很乐意听取您的想法和经验。让我们一起让测试工作流程变得更好！ 



## 🤝 贡献

如果您想贡献代码，请先 fork 此仓库，然后提交拉取请求。我们欢迎各种建议和改进，让 TraceSpanTree 变得更出色！ 