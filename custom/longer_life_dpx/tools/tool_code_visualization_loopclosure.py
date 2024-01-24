# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file
import os

class Tool(BaseTool):
    def __init__(self):
        self.name = "可视化轨迹， 分析回环"
        self.type = BaseTool.TYPE_CODE_VISULIZATION
        self.autor = 'qiuzhichang'

    def run(self):
        PrintUtils.print_info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>开始编译>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        old_dir = os.getcwd()
        PrintUtils.print_info("old_dir: " + old_dir)
        src_dir = "~/ctxmnt/D/dpx/code/tools/linux_install/custom/longer_life_dpx/tools/analyze_loop_trajectory_qzc.py"
        dst_dir = "~/Documents/dataset"
        CmdTask("cp {} {}".format(src_dir, dst_dir), os_command=True).run()

        # 2. 可视化代码
        dataset_name="P100_ent1_route3_case2"
        dataset_name="P16_ent1_route1_case1"
        dataset_name="P16_ent1_route1_case2"
        dataset_name="P18_ent1_route3_case2"
        dataset_name="P19_ent1_route1_case1"
        dataset_name="P59_ent1_route1_case1"
        PrintUtils.print_info("工作目录: " + dst_dir)
        CmdTask("python3 analyze_loop_trajectory_qzc.py \
                --dataset_name {}".format(dataset_name),
                path=dst_dir, os_command=True).run()

        # os.chdir(old_dir)
