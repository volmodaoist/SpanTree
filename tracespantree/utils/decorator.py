import time
import asyncio

import urllib3
import warnings
import functools



def try_catch(error_msg):
    ''' 柯里化错误信息捕获装饰器，捕获被装饰函数中抛出的异常，
        并以指定的错误信息包装后重新抛出。
    '''
    def decorator(func):
        if asyncio.iscoroutinefunction(func): 
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    raise Exception(f"{error_msg}: {e}") from e
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    raise Exception(f"{error_msg}: {e}") from e
            return sync_wrapper
    return decorator



# 测量函数的执行时间，并且根据 return_time 参数决定是否返回耗时。
def time_calc(return_time=False):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                result = await func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"异步函数 {func.__name__} 执行完成，耗时 {execution_time:.6f} 秒")
                if return_time:
                    return result, execution_time
                return result
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)  # 执行同步函数
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"同步函数 {func.__name__} 执行完成，耗时 {execution_time:.6f} 秒")
                if return_time:
                    return result, execution_time
                return result
            return sync_wrapper
    return decorator





def deprecated(reason: str = ""):
    """标记函数为废弃，调用时发出警告"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"Function {func.__name__}() is deprecated. {reason}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator