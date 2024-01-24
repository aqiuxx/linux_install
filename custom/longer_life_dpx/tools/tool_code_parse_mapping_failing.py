# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file
import os

class Tool(BaseTool):
    def __init__(self):
        self.name = "分析Mapping.log,查看失败原因"
        self.type = BaseTool.TYPE_CODE_VISULIZATION
        self.autor = 'qiuzhichang'

    def run(self):
        PrintUtils.print_info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>开始编译>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # old_dir = os.getcwd()
        # PrintUtils.print_info("old_dir: " + old_dir)

        src_dir = "~/ctxmnt/D/dpx/code/tools/linux_install/custom/longer_life_dpx/tools/output/0.0.16_1.csv"
        dst_dir = "~/Documents/dataset"
        CmdTask("cp {} {}".format(src_dir, dst_dir), os_command=True).run()

        src_dir = "~/ctxmnt/D/dpx/code/tools/linux_install/custom/longer_life_dpx/tools/parse_mapping_failing_qzc.py"
        dst_dir = "~/Documents/dataset"
        CmdTask("cp {} {}".format(src_dir, dst_dir), os_command=True).run()

        # 2. 解析代码
        PrintUtils.print_info("工作目录: " + dst_dir)
        CmdTask("python3 parse_mapping_failing_qzc.py",
                path=dst_dir, os_command=True).run()

        # os.chdir(old_dir)
