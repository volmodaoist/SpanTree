import json
import pytest
import SpanTree as st


@pytest.fixture
def span_data():
    with open("demo2.json") as d1:
        spans = json.load(d1)['spans']
    return spans

@pytest.fixture
def spantree(span_data):
    return st.SpanTree(span_data)


# 测试批量抓取
def test_param_consistency(spantree):
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
    
    # 对于 inter 约束，取出末尾的 span_name
    for span_name, cfg in configs.items():
        span_name = span_name.split('.')[-1]
        
        # 对于 inner 约束，取出末尾的 field_name
        for (field, _, _) in cfg["target_fields"]:
            field_name = field.split('.')[-1]
            assert f"{span_name} {field_name}" in results


    assert results['leaf_span_1 result_key'] == 'leaf1_result_value, idx = 0'
    assert results['leaf_span_2 result_key'] == 'leaf2_result_value, idx = 1'
    


# 命令行运行: pytest 即可运行所有test开头的函数
if __name__ == '__main__':
    pass