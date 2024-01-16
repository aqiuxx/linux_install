# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file
import os

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "安装lazygit"
        self.autor = 'qiuzhichang'

    def install_lazygit(self):
        """
        LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
        curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
        tar xf lazygit.tar.gz lazygit
        """
        PrintUtils.print_info(os.getcwd())
        CmdTask('sudo chmod a+x install_lazygit.sh', path="tools", os_command=True).run()
        CmdTask('sh install_lazygit.sh', path="tools", os_command=True).run()
        (code, out, err) = CmdTask('ls /usr/local/bin/lazygit').run()
        if out:
            PrintUtils.print_info("install sucessfull !")
        else:
            PrintUtils.print_error("install fail !")

    def run(self):
        #正式的运行
        self.install_lazygit()
