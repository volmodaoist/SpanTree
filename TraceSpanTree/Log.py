''' 调试专用的 Log 对象，用于打印不同级别的日志信息，目前支持以下级别：
        - warning: 黄色输出，用于警告信息
        - error: 红色输出，用于错误信息
        - success: 绿色输出，用于成功信息
        - verbose: 默认颜色输出，用于普通且不太需要注意的日志
        - info: 蓝色输出，用于普通信息且值得关注的信息
        - highlight: 紫色输出，用于强调或高亮信息
'''
class Log:
    color_codes = {
        "default": "\033[0m",  # 默认颜色
        "yellow": "\033[33m",  # 黄色
        "red": "\033[31m",     # 红色
        "blue": "\033[34m",    # 蓝色
        "green": "\033[32m",   # 绿色
        "purple": "\033[35m",  # 紫色
    }
    

    '''
    param {*} text: 需要打印的日志内容
    description: 打印 warning 级别日志，使用黄色显示
    '''
    @staticmethod
    def warning(text):
        Log._print_colorful(text, color="yellow")


    '''
    param {*} text: 需要打印的日志内容
    description: 打印 error 级别日志，使用红色显示
    '''
    @staticmethod
    def error(text):
        Log._print_colorful(text, color="red")
    
    
    '''
    param {*} text: 需要打印的日志内容
    description: 打印成功运行的日志，使用绿色显示
    '''  
    @staticmethod
    def success(text):
        Log._print_colorful(text, color="green")


    '''
    param {*} text: 需要打印的日志内容
    description: 打印 info 级别日志，使用蓝色显示
    '''
    @staticmethod
    def info(text):
        Log._print_colorful(text, color="blue")



    '''
    param {*} text: 需要打印的日志内容
    description: 打印 highlight 级别日志，使用蓝色显示（与 info 相同）
    '''
    @staticmethod
    def highlight(text):
        Log._print_colorful(text, color="purple")



    '''
    param {*} text: 需要打印的日志内容
    description: 打印 verbose 级别日志，使用默认颜色显示
    '''
    @staticmethod
    def verbose(text):
        Log._print_colorful(text, color="default")




    '''
    param {*} text: 打印内容
    param {*} color: 打印颜色，可选 "yellow", "red", "blue" ... "default"
    description: 私有方法，用于根据指定颜色打印日志
    '''
    @staticmethod
    def _print_colorful(text, color="default"):
        color_code = Log.color_codes.get(color.lower(), Log.color_codes["default"])
        print(f"{color_code}{text}\033[0m") 