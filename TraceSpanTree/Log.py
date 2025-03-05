''' 调试专用的 Log 对象，用于打印不同级别的日志信息，目前支持以下级别：
        - verbose: 默认颜色输出，使用 logging.DEBUG 级别，适用于详细信息的日志记录，通常用于开发阶段的低优先级信息。
        - debug: 紫色输出，使用 logging.DEBUG 级别，等同于 highlight 方法，适用于调试信息或需要强调的内容。
        - info: 蓝色输出，使用 logging.INFO 级别，适用于普通信息且值得关注的日志记录。
        - success: 绿色输出，使用 logging.INFO 级别，适用于成功操作或关键事件的通知。
        - warning: 黄色输出，使用 logging.WARNING 级别，适用于警告信息，表明某些意外情况发生但程序仍可运行。
        - error: 红色输出，使用 logging.ERROR 级别，适用于错误信息，表明某些功能无法正常工作。
        - critical: 红色输出，使用 logging.CRITICAL 级别，适用于严重错误信息，表明程序遇到非常严重的问题可能无法继续运行。
        - highlight: 紫色输出，使用 logging.DEBUG 级别，适用于需要强调或高亮显示的信息，日志级别等于 debug 方法的级别。

    注意事项：日志的颜色和级别通过 ANSI 转义序列实现，适用于支持彩色输出的终端。
        可以通过 Log.set_level(level) 动态调整日志的最低输出等级（e.g. logging.DEBUG、logging.INFO 等），
        从而控制日志的显示范围。这个 Log 对象为单例模式，全局唯一实例可通过 Log 访问。
'''

import logging

class LogX:
    # 颜色代码
    color_codes = {
        "default": "\033[0m",  # 默认颜色
        "yellow": "\033[33m",  # 黄色 (WARNING)
        "red": "\033[31m",     # 红色 (ERROR, CRITICAL)
        "blue": "\033[34m",    # 蓝色 (INFO)
        "green": "\033[32m",   # 绿色 (SUCCESS)
        "purple": "\033[35m",  # 紫色 (DEBUG, HIGHLIGHT)
    }

    # 单例模式：存储唯一的 Log 实例
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LogX, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        """初始化 logger"""
        self.logger = logging.getLogger("ColorLogger")
        self.logger.setLevel(logging.DEBUG)  # 设置默认日志等级为 DEBUG

        # 防止重复添加处理器
        if not self.logger.handlers:
            # 创建控制台处理器
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            # 设置格式化器
            formatter = logging.Formatter("%(message)s")  # 只输出消息内容
            ch.setFormatter(formatter)

            # 添加处理器到 logger
            self.logger.addHandler(ch)

    @staticmethod
    def set_level(level):
        """
        动态设置日志输出等级
        :param level: 日志等级，比如  logging.DEBUG, logging.INFO,  logging.WARNING, logging.ERROR, logging.CRITICAL
        """
        logger = logging.getLogger("ColorLogger")
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)

    def verbose(self, text):
        """打印 VERBOSE 级别日志，使用默认颜色显示"""
        color_code = self.color_codes["default"]
        reset_code = self.color_codes["default"]
        self.logger.debug(f"{color_code}{text}{reset_code}")
    
    def debug(self, text):
        self.highlight(text)
        
    def highlight(self, text):
        """打印 DEBUG 级别日志，使用紫色显示"""
        color_code = self.color_codes["purple"]
        reset_code = self.color_codes["default"]
        self.logger.debug(f"{color_code}{text}{reset_code}") 
        
        
    def success(self, text):
        """打印 SUCCESS 级别日志，使用绿色显示"""
        color_code = self.color_codes["green"]
        reset_code = self.color_codes["default"]
        self.logger.info(f"{color_code}{text}{reset_code}")
        
    def info(self, text):
        """打印 INFO 级别日志，使用蓝色显示"""
        color_code = self.color_codes["blue"]
        reset_code = self.color_codes["default"]
        self.logger.info(f"{color_code}{text}{reset_code}")
        
    def warning(self, text):
        """打印 WARNING 级别日志，使用黄色显示"""
        color_code = self.color_codes["yellow"]
        reset_code = self.color_codes["default"]
        self.logger.warning(f"{color_code}{text}{reset_code}")


    def error(self, text):
        """打印 ERROR 级别日志，使用红色显示"""
        color_code = self.color_codes["red"]
        reset_code = self.color_codes["default"]
        self.logger.error(f"{color_code}{text}{reset_code}")

    def critical(self, text):
        """打印 CRITICAL 级别日志，使用红色显示"""
        color_code = self.color_codes["red"]
        reset_code = self.color_codes["default"]
        self.logger.critical(f"{color_code}{text}{reset_code}")


# 全局 Log 实例
Log = LogX()


if __name__ == '__main__':
    Log.critical("Hey")
    Log.error("Hey")
    Log.warning("Hey")
    Log.success("Hey")
    Log.debug("Hey")
    Log.highlight("Hey")
    Log.verbose("Hey")