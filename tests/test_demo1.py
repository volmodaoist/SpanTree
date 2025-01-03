import json
import pytest
import SpanTree as st


@pytest.fixture
def span_data():
    with open("demo1.json") as d1:
        spans = json.load(d1)['spans']
    return spans

@pytest.fixture
def spantree(span_data):
    return st.SpanTree(span_data)


# 测试单个抓取
def test_retrive_methods(spantree):
    # 通过inter约束、inner约束搜索
    res1 = spantree.retrive(target_span_name='root.father_span_1.leaf_span_1', target_field='data.message')
    res2 = spantree.retrive(target_span_name='root.leaf_span_1', target_field='data.message')
    res3 = spantree.retrive(target_span_name='root.leaf_span_1', target_field='message')

    assert res1 == "This is a leaf span under father_span_1."
    assert res1 == res2 and res2 == res3
    
    
    # 通过inter约束、inner约束搜索
    res1 = spantree.retrive(target_span_name='root.father_span_2.leaf_span_2', target_field='data.message')
    res2 = spantree.retrive(target_span_name='root.leaf_span_2', target_field='data.message')
    res3 = spantree.retrive(target_span_name='root.leaf_span_2', target_field='message')
    assert res1 == "This is a leaf span under father_span_2."
    assert res1 == res2 and res2 == res3


# 测试批量抓取
def test_batch_retrive_methods(spantree):
    configs = {
        "root.father_span_1": {
            "idx": None,
            "is_type": False,
            "target_fields": [
                ("data.message", "default_message", lambda x: x),
                ("state_code", -1, lambda x:x)
            ]
        }, 
        "root.father_span_2": {
            "idx": None,
            "is_type": False,
            "target_fields": [
                ("data.message", "default_message", lambda x: x),
                ("state_code", -1, lambda x:x)
            ]
        },
        "root.leaf_span_1": {
            "idx": None,
            "is_type": False,
            "target_fields": [
                ("data.message", "default_message", lambda x: x),
                ("state_code", -1, lambda x:x)
            ]
        }, 
        "root.leaf_span_2": {
            "idx": None,
            "is_type": False,
            "target_fields": [
                ("data.message", "default_message", lambda x: x),
                ("state_code", -1, lambda x:x)
            ]
        }
    }
    
    res = spantree.batch_retrive(configs)
    
    assert isinstance(res, dict)
    assert res['father_span_1 message'] == res['father_span_2 message']
    assert res['father_span_1 state_code'] == 0 
    assert res['father_span_2 state_code'] == 0




# 命令行运行: pytest 即可运行所有test开头的函数
if __name__ == '__main__':
    pass