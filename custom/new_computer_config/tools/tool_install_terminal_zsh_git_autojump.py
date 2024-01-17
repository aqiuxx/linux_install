# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "安装terminator/ZSH/git/autojump"
        self.autor = 'qiuzhichang'

    def install_terminal_git_zsh_autojump(self):
        """
        sudo apt install terminator
        sudo apt install git zsh autojump
        # 安装oh-my-zsh
        sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
        """
        CmdTask('sudo apt install tree iputils-ping -y', os_command=True).run()
        CmdTask('sudo apt install terminator -y', os_command=True).run()
        CmdTask('sudo apt install git zsh -y', os_command=True).run()
        CmdTask('sudo apt install autojump -y', os_command=True).run()
        CmdTask('sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"', os_command=True).run()

    def run(self):
        #正式的运行
        self.install_terminal_git_zsh_autojump()
