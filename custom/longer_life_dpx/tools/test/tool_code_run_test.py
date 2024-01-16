# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file
import os

class Tool(BaseTool):
    def __init__(self):
        self.name = "模板工程-编译代码"
        self.type = BaseTool.TYPE_CODE_COMPILE
        self.autor = 'qiuzhichang'

    def run(self):
        PrintUtils.print_info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>开始编译>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        old_dir = os.getcwd()
        PrintUtils.print_info("old_dir: " + old_dir)

        src_dir = "/Users/aqiu/Documents/1_study/00_AllMyXX/AllMySlam/Slam-Course/VIO-Course/1"
        # os.chdir(src_dir)
        # src_dir = os.getcwd()
        PrintUtils.print_info("工作目录: " + src_dir)

        CmdTask("cd build && ./r_vs_q", path=src_dir,os_command=True).run()

        # (code,out,err) = CmdTask("./build/r_vs_q").run()
        # PrintUtils.print_info("{}".format(out))
        # os.chdir(old_dir)
