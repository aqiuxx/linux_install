# -*- coding: utf-8 -*-
import os

# url_prefix = 'http://fishros.com/install/install1s/'
url_prefix = '~/ctxmnt/D/dpx/tools/linux_install/custom/longer_life_dpx/'

# base_url = url_prefix+'tools/base.py'

INSTALL_ROS = 0         # 安装ROS相关
INSTALL_SOFTWARE = 1    # 安装软件
CONFIG_TOOL = 2         # 配置相关
CODE_COMPILE = 3        # 代码编译
CODE_RUN = 4            # 代码运行
CODE_VISUALIZATION = 5  # 代码可视化


tools_type_map = {
    INSTALL_ROS: "ROS相关",
    INSTALL_SOFTWARE: "常用软件",
    CONFIG_TOOL: "配置工具",
    CODE_COMPILE: "编译代码",
    CODE_RUN: "运行程序",
    CODE_VISUALIZATION: "可视化程序",
}


tools ={
    1: {'tip':'编译建图代码', 'type':CODE_COMPILE, 'tool': url_prefix+'tools/tool_code_compile_mapping.py', 'dep':[]},
    2: {'tip':'编译建图代码-arm', 'type':CODE_COMPILE, 'tool': url_prefix+'tools/tool_code_compile_mapping_arm.py', 'dep':[]},
    3: {'tip':'运行建图代码', 'type':CODE_RUN, 'tool': url_prefix+'tools/tool_code_run_mapping.py', 'dep':[]},
    4: {'tip':'运行建图代码-arm', 'type':CODE_RUN, 'tool': url_prefix+'tools/tool_code_run_mapping_arm.py', 'dep':[]},
    5: {'tip':'可视化建图代码', 'type':CODE_VISUALIZATION, 'tool': url_prefix+'tools/tool_code_visualization_mapping.py', 'dep':[]},
    6: {'tip':'可视化建图代码-arm', 'type':CODE_VISUALIZATION, 'tool': url_prefix+'tools/tool_code_visualization_mapping_arm.py', 'dep':[]},
    7: {'tip':'运行-可视化建图代码', 'type':CODE_VISUALIZATION, 'tool': '', 'dep':[3,5]},
    8: {'tip':'编译-运行-可视化建图代码', 'type':CODE_VISUALIZATION, 'tool': '', 'dep':[1,3,5]},
    9: {'tip':'运行建图代码', 'type':CODE_RUN, 'tool': url_prefix+'tools/tool_code_run_mapping_with_loc.py', 'dep':[]},


    # 77: {'tip':'测试模式:运行自定义工具测试'},
    78: {'tip':'编译模板代码', 'type':CODE_COMPILE, 'tool': url_prefix+'tools/test/tool_code_compile_test.py', 'dep':[]},
    79: {'tip':'运行模板代码', 'type':CODE_RUN, 'tool': url_prefix+'tools/test/tool_code_run_test.py', 'dep':[]},
}


# 创建用于存储不同类型工具的字典
tool_categories = {}

# 遍历tools字典，根据type值进行分类
for tool_id, tool_info in tools.items():
    tool_type = tool_info['type']
    # 如果该类型还没有在字典中创建，则创建一个新的列表来存储该类型的工具
    if tool_type not in tool_categories:
        tool_categories[tool_type] = {}
    # 将工具信息添加到相应类型的列表中
    tool_categories[tool_type][tool_id]=tool_info


import argparse
def parse_args():
    tool_id = -1
    # nargs='*' 表示参数可设置零个或多个
    # nargs='+' 表示参数可设置一个或多个
    # nargs='?' 表示参数可设置零个或一个
    parser = argparse.ArgumentParser(description='mapping tools.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-id', '--id', type=int, default=tool_id,
                        help='设置想运行的脚本, id 可设置为：\n\
    -1 : 默认值， 用户在命令行选择id \n\
    1 : 仅编译建图-x86 \n\
    2 : 仅编译建图-arm \n\
    3 : 仅运行建图-x86 \n\
    4 : 仅运行建图-arm \n\
    5 : 仅可视化建图-x86 \n\
    6 : 仅可视化建图-arm \n\
    7 : 运行+可视化建图-x86 \n\
    8 : 编译+运行+可视化建图-x86 \n\
    ')
    args = parser.parse_args()

    return args

def main():
    args = parse_args()

    # download base
    # os.system("wget {} -O /tmp/fishinstall/{} --no-check-certificate".format(base_url,base_url.replace(url_prefix,'')))
    from tools.base import CmdTask,FileUtils,PrintUtils,ChooseTask,ChooseWithCategoriesTask
    from tools.base import encoding_utf8,osversion,osarch
    from tools.base import run_tool_file,download_tools
    from tools.base import config_helper

    # check base config
    if not encoding_utf8:
        print("Your system encoding not support ,will install some packgaes..")
        CmdTask("sudo apt-get install language-pack-zh-hans -y",0).run()
        CmdTask("sudo apt-get install apt-transport-https -y",0).run()
        FileUtils.append("/etc/profile",'export LANG="zh_CN.UTF-8"')
        print('Finish! Please Try Again!')
        print('Solutions: https://fishros.org.cn/forum/topic/24 ')
        return False
    PrintUtils.print_success("基础检查通过...")

    print("input id: ", args.id)
    if args.id == -1:
        id, result = \
        ChooseWithCategoriesTask(tool_categories, tips="---众多工具，等君来用---",categories=tools_type_map).run()
    else:
        id = args.id
    PrintUtils.print_delay("tool id: " + str(id), 0.001)

    if id==0: PrintUtils().print_success("是觉得没有合胃口的菜吗？自己动手吧~")
    else :
        # 1. run dependence
        for dep in  tools[id]['dep']:
            url = tools[dep]['tool']
            PrintUtils.print_delay("================================================>", 0.001)
            PrintUtils.print_delay(url, 0.001)
            PrintUtils.print_delay("================================================>", 0.001)
            run_tool_file(url.replace(url_prefix,'').replace("/","."))

        # 2. run main code
        url = tools[id]['tool']
        # print(url.replace(url_prefix,'').replace("/","."))
        PrintUtils.print_delay("================================================>", 0.001)
        PrintUtils.print_delay(url, 0.001)
        PrintUtils.print_delay("================================================>", 0.001)
        run_tool_file(url.replace(url_prefix,'').replace("/","."))

    config_helper.gen_config_file()
    PrintUtils.print_success("see you !",0.001)

if __name__=='__main__':
    main()
