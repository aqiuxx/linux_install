# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file
import os

class Tool(BaseTool):
    def __init__(self):
        self.name = "建图-编译"
        self.type = BaseTool.TYPE_CODE_COMPILE
        self.autor = 'qiuzhichang'

    def run(self):
        PrintUtils.print_info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>开始编译>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        old_dir = os.getcwd()
        PrintUtils.print_info("old_dir: " + old_dir)

        src_dir = "~/Documents/1_code/ndm_envnav/project_build/pilot"
        # os.chdir(src_dir)
        # src_dir = os.getcwd()
        PrintUtils.print_info("工作目录: " + src_dir)

        CmdTask("bash ./build.sh -j10", path=src_dir, os_command=True).run()
        CmdTask("bash ./package_envmodel_x86.sh", path=src_dir, os_command=True).run()

        # (code,out,err) = CmdTask("./build/r_vs_q").run()
        # PrintUtils.print_info("{}".format(out))
        # os.chdir(old_dir)
