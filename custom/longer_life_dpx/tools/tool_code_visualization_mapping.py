# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file
import os

class Tool(BaseTool):
    def __init__(self):
        self.name = "建图-可视化"
        self.type = BaseTool.TYPE_CODE_VISULIZATION
        self.autor = 'qiuzhichang'

    def run(self):
        PrintUtils.print_info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>开始编译>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        old_dir = os.getcwd()
        PrintUtils.print_info("old_dir: " + old_dir)

        # 2. 可视化代码
        map_name="~/Documents/1_code/log/latest/map/parking/20168942/31.283887-121.176075/underground-in/sp_map.ndm"
        src_dir = "~"
        PrintUtils.print_info("工作目录: " + src_dir)
        CmdTask("/home/HOBOT/qiu.zhichang-byd/Documents/5_soft/visualization/MapViewer/build/bin/MapViewer \
                --font /home/HOBOT/qiu.zhichang-byd/Documents/5_soft/visualization/MapViewer/config/Pangolin-Regular.ttf \
                {}".format(map_name),
                path=src_dir, os_command=True).run()

        # os.chdir(old_dir)
