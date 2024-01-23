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
        src_dir = "~/ctxmnt/D/dpx/code/tools/linux_install/custom/longer_life_dpx/tools/run.py"
        dst_dir = "~/Documents/1_code"
        CmdTask("cp {} {}".format(src_dir, dst_dir), os_command=True).run()

        src_dir = "~/ctxmnt/D/dpx/code/tools/linux_install/custom/longer_life_dpx/tools/output/log_name_to_fail_reason_out.csv"
        dst_dir = "~/Documents/1_code/output"
        CmdTask("cp {} {}".format(src_dir, dst_dir), os_command=True).run()

        dst_dir = "~/Documents/1_code"
        PrintUtils.print_info("工作目录: " + dst_dir)
        CmdTask("python run.py run --speed=3 --monitor \
                --no-use-maprec-line \
                --pack-folder ~/Documents/dataset/pilot_daq \
                --save-folder ~/Documents/dataset/log \
                --bole-pack-folder ~/Documents/5_soft/bolepack \
                --mapping-folder ~/Documents/1_code/ndm_envnav/output/ndm_envmodel \
                --loc-folder ~/Documents/dataset/navinet_superparking \
                ", path=dst_dir, os_command=True).run()


        # CmdTask("python run.py run --speed=3 --monitor \
        #         --no-use-maprec-line \
        #         --pack-folder ~/Documents/dataset/sample/ruili_ent2_route1_case1 \
        #         --save-folder ~/Documents/dataset/log \
        #         --bole-pack-folder ~/Documents/5_soft/bolepack \
        #         --mapping-folder ~/Documents/1_code/ndm_envnav/output/ndm_envmodel \
        #         --loc-folder ~/Documents/dataset/navinet_superparking \
        #         ", path=dst_dir, os_command=True).run()

        # os.chdir(old_dir)
