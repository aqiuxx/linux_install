# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "安装pdf"
        self.autor = 'qiuzhichang'

    def install_pdf(self):
        CmdTask('sudo apt-get install okular -y').run()

    def run(self):
        #正式的运行
        self.install_pdf()
