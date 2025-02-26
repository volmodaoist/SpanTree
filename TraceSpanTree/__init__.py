''' 导入说明: 

    此处说明两个基本概念:
        1. Package（包）: 包含 __init__.py 文件的文件夹，这个文件夹里面可以包含其它模块，或者子包，
        能够构建多层嵌套结构（e.g. parent_package/child_package/ 等形式访问，各级目录都需有对应的 __init__.py 文件）
        方便组织大型项目代码。对于一个包，Python 加载的时候，首先会加载其中的 __init__.py 文件，在这个文件中可以进行一些包初始化操作，
        比如定义包级别的变量、函数，也可以导入子模块等。一个包能方便外部访问的模块或对象，常见是要在其 __init__.py 文件里面进行合适导入，
        但也可通过完整路径形式（e.g. from my_package.sub_module import some_function）访问包内子模块内容，无需提前在 __init__.py 
        里面导入该子模块。

        2. Module（模块）: 包含 Python 代码的文件，使用.py 结尾，作为 Python 代码组织的基本单元。通常导入模块即可访问模块内部的变量、类、函数等，
        但是，如果模块内部存在 __all__ 列表，那么只有 __all__ 列表里面列出的名称对应的对象（函数、类、变量等），才能通过 from module import * 导入

    然后说明两类导入的概念: 
        - from x import xxx 这是绝对导入 (导入模块或包)
        - from.x import xxx 这是相对导入 (导入模块)

    绝对导入: Python 会从 sys.path 所包含的目录路径中去查找包，或者模块 x 进行导入。  

            - 如果 x 是一个包，通常情况之下，需要在其 __init__.py 文件里面导入相应内容，外部才能通过 from module import xxx 便捷地访问 xxx，
              但也可通过完整路径形式访问内部子模块内容。
              
            - 如果 x 是一个模块，只要 xxx 已在这个模块里面声明，外部即可通过 from module import xxx 访问 xxx 变量或函数，
              不过若是使用 from module import * 形式导入，模块内部的 __all__ 列表会限定导出的变量、函数、对象等。


    相对导入: 相对导入是用于在包内部的模块之间进行导入的方式， '.' 代表当前模块所在的目录位置 (在包结构中)，e.g. “from.x import xxx 这种形式，
             是从当前模块所在的包中导入同层级的 x 模块里的 xxx，类似的操作也有 '..' (上级目录)
            
'''

from .utils import (
  try_catch
)
from .Log import Log as Log
from .SpanTree import SpanTree as SpanTree
from .MultiNestDict import MultiNestDict as MultiNestDict
from .TraceGen import Tracer
