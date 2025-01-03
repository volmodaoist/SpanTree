需要按照下面的结构组织项目

``` shell
SpanTree/
├── SpanTree/                # 主模块目录，库的代码应该放在这里
│   ├── __init__.py          # 模块的初始化文件，标识这是一个 Python 包
│   ├── SpanTree.py          # 你的主要代码文件
├── tests/                   # 测试目录
│   ├── __init__.py          # 可选，用于标识测试目录为一个包
│   ├── test_SpanTree.py     # 测试代码文件，通常以 test_ 开头
├── setup.py                 # 项目构建脚本，包含打包的元信息
├── pyproject.toml           # 可选，用于现代构建工具的配置
├── LICENSE                  # 许可证文件
├── README.md                # 项目说明文档
├── .gitignore               # Git 忽略文件列表
└── requirements.txt         # 项目依赖文件
```