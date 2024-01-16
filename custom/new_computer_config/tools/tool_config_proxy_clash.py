# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file


class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_CONFIG
        self.name = "替换配置参数"
        self.autor = 'qiuzhichang'

    def add_proxy(self):
        '''
        1.桌面快捷方式：需要先右击允许执行才能使用
        2.可以在终端中直接运行脚本启动,直接输入:$HOME/.clash/start_clash.sh
            启动脚本配置完成，你可以在目录: /root.clash/  运行 start_clash.sh 启动工具，启动后可通过网页：http://127.0.0.1:1234/ 进行管理
        3.终端通过环境变量设置: export http_proxy=http://127.0.0.1:7890 && export https_proxy=http://127.0.0.1:7890
        4.配置系统默认代理方式: 系统设置->网络->网络代理->手动->HTTP(127.0.0.1 7890)->HTTPS(127.0.0.1 7890)
        '''
        out = FileUtils.getusershome()[0]
        file = ".zshrc"
        FileUtils.append(out+file, "export http_proxy=http://127.0.0.1:7890")
        FileUtils.append(out+file, "export https_proxy=http://127.0.0.1:7890")

        # out = FileUtils.getusershome()[0]
        # file = ".bashrc"
        # FileUtils.append(out+file, "export http_proxy=http://127.0.0.1:7890")
        # FileUtils.append(out+file, "export https_proxy=http://127.0.0.1:7890")

    def run(self):
        self.add_proxy()
