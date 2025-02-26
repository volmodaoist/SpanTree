# TraceSpanTree README

Hey developers! 🚀 Tired of dealing with complex nested trace data (or nested dict) in your projects? **TraceSpanTree** is here to help!

Quick install:

```shell
pip install -i https://test.pypi.org/simple/ TraceSpanTree==1.0.1
```

Give us a ⭐ and let's simplify your trace data management!


## 😎 Introduction
Hello, fellow developers and QA engineers! We've built **TraceSpanTree**, a Python library designed to simplify working with complex hierarchical trace data, which is often stored in JSON format during project execution (or Debug). Managing nested key-value pairs and writing assertions can be tedious, especially when the data structure changes frequently.

With **TraceSpanTree**, you can easily navigate, update, and retrieve key-value pairs within multi-level nested dictionaries and span structures. Our goal is to provide an efficient way to manage trace data, reducing code complexity and maintenance overhead.


## 🚀 Features Overview

The **TraceSpanTree** library includes the following core components:

1. **`Log`** – Simplified logging utility to track trace operations efficiently.
2. **`MultiNestDict`** – Enables easy retrieval and updates within deeply nested dictionaries.
3. **`SpanTree`** – Facilitates searching and retrieving values within complex trace hierarchies.
4. **`TraceGen`** – Provides the `Tracer` object with `@tracer.trace_gen` decorator to automatically generate span trees from function calls.



🌳 Concept of SpanTree
Think of trace data as a tree structure where:
- Each node (span) represents operational data from a specific service.
- Each span is stored as a JSON object, which itself can be treated as a tree.

The result? A “tree within trees” model that helps navigate trace data more efficiently. By leveraging this structure, TraceSpanTree provides robust tools to locate and interact with data at any level.




## 🛠️ Core Functional Implementation

Alright, so SpanTree's main functionality is brought to life by the following two functions:

### Inter Span Constraint

The `_recursive_inter_search` function is designed to help you navigate through the span tree:

- **Function Description**: It recursively searches for the `target_span_name` within the span tree. The `target_span_name` supports the '.' constraint, which can be quite handy when you're trying to pinpoint a particular span within that often-confusing tree structure. 

- **Usage Explanation**: Once you expand the entire set of spans, it forms a tree. Imagine you're walking from the root node to the leaf nodes, and the names of the spans form a path like `'span1.span2.span3.span4.span5.span6'`. In this case, the `target_span` can be a non-contiguous subsequence of this path, for example, `'span_name1.span_name3.span_name5'`. By using this path, you can locate the span corresponding to the `span_name`. Additionally, if the `is_type` parameter is set, the search will be conducted using the span type instead of the name. 

### Inner Span Constraint

The `_recursive_inner_search` function is focused on exploring within a single span:

- **Function Description**: It recursively searches for the `target_key` within a single span. The `target_key` also supports the '.' constraint. The `idx` parameter is useful for `List[Dict]` structures, allowing you to target only the fields within the `idx`-th `Dict` element. 

- **Usage Explanation**: Each span, when you look inside it, also forms a tree-like structure. Suppose you're traversing from the root node to the leaf nodes within a span, and the names of the keys form a path like `'key1.key2.key3.key4.key5.key6'`. Then, the `target_key` can be a non-contiguous subsequence of this path, such as `'key1. key3. key5'`. Through this path, you can find the value corresponding to `key5`. 





##  🧰 Key Functions for Users
###   Function `retrive`

This function is one of the key tools in the SpanTree arsenal for retrieving specific data. It takes advantage of both the inter and inner constraints to make it easier for you to access the values you need. For example:

```python
res1 = spantree.retrive(target_span_name='root.father_span_1.leaf_span_1', 
                        target_field='data.message')
res2 = spantree.retrive(target_span_name='root.leaf_span_1', 
                        target_field='data.message')
res3 = spantree.retrive(target_span_name='root.leaf_span_1', 
                        target_field='message')
```

With a simple call to this function, you can efficiently navigate through the complex tree structures and obtain the desired values. We've aimed to make it as straightforward as possible, but we're aware that everyone's use cases can vary. If you have any difficulties or ideas for improvement, don't hesitate to reach out. 



### Function  `batch_retrive`

When you need to retrieve multiple values from different parts of the SpanTree simultaneously, the `batch_retrive` function comes in handy. You can configure it with appropriate settings to fetch a variety of data in one go. This is especially beneficial for comprehensive testing scenarios where multiple aspects need to be verified at once. However, we understand that the configuration might seem a bit daunting at first, so if you need any help or have questions about how to use it best, just let us know. 





## Usage Example 📝

Here's a more detailed look at how you can use SpanTree with some sample data. First, let's consider the following `spans` structure represented in JSON:

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
        "message": "This is the root span.",
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
        "message": "This is a sub span under root.",
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
        "message": "This is a leaf span under father_span_1.",
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
        "message": "This is a sub span under root.",
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
        "message": "This is a leaf span under father_span_2.",
        "timestamp": "2024-01-01T00:00:35Z"
      }
    }
  ]
}
```

You can use the `retrive` function on this data quite easily. For instance:

```python
res1 = spantree.retrive(target_span_name='root.father_span_1.leaf_span_1', 
                        target_field='data.message')

res2 = spantree.retrive(target_span_name='root.leaf_span_1', 
                        target_field='data.message')


res3 = spantree.retrive(target_span_name='root.leaf_span_1',
                       target_field='message')

# res1, res2, res3 have the same value in this eaxmple.
```

Now, let's expand our example further. Consider a more complex `spans` structure:

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

And here's how you can use the `batch_retrive` function to handle more comprehensive data extraction:

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

In the `batch_retrive` function, `configs` is a crucial dictionary for configuration.

Take a `target_span_name` in `configs` (e.g., `"root"`):
- `idx` (optional): For `List[Dict]` data, set a value to retrieve fields only from the `idx`-th element. If `None`, no index limitation.
- `is_type` (optional): Default is `False`. Set to `True` to match the target span using `[span_name]` as `[span_type]`.
- `target_fields` (required): It's a list of tuples like `(target_field_name, default, callback)`.
  - `target_field_name`: The name of the field to retrieve, e.g., `"input.param_str"`, specifying the hierarchy.
  - `default`: The fallback value if the field isn't found, with a matching type.
  - `callback`: A lambda function to process the retrieved field value.

This way, whether you're using the simple `retrive` function for quick access to specific values or the more powerful `batch_retrive` function for handling multiple data extractions at once, SpanTree provides a convenient and efficient way to interact with hierarchical data. We hope it makes your testing work more efficient and less error-prone, but we're always open to feedback if you think there's something we could do better. After all, we're all in this together to make our testing workflows smoother and more effective! 😃 






## 📑 Conclusion 
SpanTree is our attempt to simplify the process of handling hierarchical data in test scripts for QA engineers and test development engineers. We've put a lot of thought into its design and functionality, but we know there's still a lot to learn and improve. By leveraging its features and functions, we hope you can focus more on the actual testing logic rather than getting bogged down in complex data access and maintenance issues. If you decide to give it a try in your projects, we'd love to hear your thoughts and experiences. Let's make our testing workflows better together! 



## 🤝 Contributing

If you'd like to contribute, fork the repository and submit a pull request. We welcome suggestions and improvements to make TraceSpanTree even better!
