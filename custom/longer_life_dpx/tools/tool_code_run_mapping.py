# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file
import os

class Tool(BaseTool):
    def __init__(self):
        self.name = "建图-运行"
        self.type = BaseTool.TYPE_CODE_RUN
        self.autor = 'qiuzhichang'

    def run(self):
        PrintUtils.print_info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>开始编译>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        old_dir = os.getcwd()
        PrintUtils.print_info("old_dir: " + old_dir)

        # 1. 运行代码
        src_dir = "~/Documents/1_code"
        PrintUtils.print_info("工作目录: " + src_dir)

        CmdTask("python run.py run --auto-trigger-start  --speed=3 --monitor \
                 --mapping-folder ~/Documents/1_code/ndm_envnav/output/ndm_envmodel \
                 --pack-folder ~/Documents/dataset/ruili_ent2_route1_case1", path=src_dir, os_command=True).run()

        # os.chdir(old_dir)
