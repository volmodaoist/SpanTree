from functools import wraps

def try_catch(error_msg):
    ''' 柯里化错误信息捕获装饰器，捕获被装饰函数中抛出的异常，
        并以指定的错误信息包装后重新抛出。
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise Exception(f"{error_msg}: {e}") from e
        return wrapper
    return decorator