import uuid
import pprint
import functools

from contextvars import ContextVar


class Tracer:
    def __init__(self):
        # 存放所有 Span 的列表（也可自行替换成数据库/文件等）
        self.spans = []

        # 在上下文中记录当前 span_id，用来实现嵌套调用时的父子关系
        self._current_span_id_var = ContextVar("current_span_id", default=None)

    def trace_gen(self, func):
        """
        用于装饰需要追踪的函数。
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 读取当前上下文中的 parent_span_id
            parent_span_id = self._current_span_id_var.get()

            # 生成新的 span_id
            span_id = str(uuid.uuid4())

            # 将当前函数的 span_id 写入上下文，并获取“令牌”以便稍后恢复
            token = self._current_span_id_var.set(span_id)

            # 记录输入
            input_data = {
                "args": args,
                "kwargs": kwargs
            }

            # 捕获输出或异常
            try:
                output_data = func(*args, **kwargs)
            except Exception as e:
                output_data = f"Exception: {e}"
            finally:
                # 记录本次函数调用信息
                self.spans.append({
                    "parent_id": parent_span_id,
                    "span_id": span_id,
                    "name": func.__name__,
                    "input": input_data,
                    "output": output_data,
                })
                # 恢复正常的 span_id
                self._current_span_id_var.reset(token)

            return output_data

        return wrapper





tracer = Tracer()

# 使用 tracer.trace_gen 来装饰想要追踪的函数
@tracer.trace_gen
def example_func_add(x, y):
    return x + y

@tracer.trace_gen
def example_func_sub(x, y):
    return x - y

@tracer.trace_gen
def example_func_div(x, y):
    return (x + y) / 0

@tracer.trace_gen
def nested_function(a, b):
    r1 = example_func_add(a, b)
    r2 = example_func_sub(a, b)
    example_func_div(r1, r2)
    return r1 + r2



# 使用实例，创建一个tracer对象用于跟踪调用链路，然后正常调用函数即可
if __name__ == "__main__":
    try:
        nested_function(2, 3)
    finally:
        pprint.pprint(tracer.spans)
