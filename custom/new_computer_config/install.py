# -*- coding: utf-8 -*-
import os

# url_prefix = 'http://fishros.com/install/install1s/'
url_prefix = '~/ctxmnt/D/dpx/tools/linux_install/custom/new_computer_config/'

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
    1: {'tip':'一键安装(推荐):ROS(支持ROS/ROS2,树莓派Jetson)',             'type':INSTALL_ROS,     'tool':url_prefix+'tools/tool_install_ros.py' ,'dep':[4,5] },
    2: {'tip':'一键安装:github桌面版(小鱼常用的github客户端)',             'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_github_desktop.py' ,'dep':[] },
    4: {'tip':'一键配置:ROS环境(快速更新ROS环境设置,自动生成环境选择)',     'type':INSTALL_ROS,     'tool':url_prefix+'tools/tool_config_rosenv.py' ,'dep':[] },
    3: {'tip':'一键安装:rosdep(小鱼的rosdepc,又快又好用)',                 'type':INSTALL_ROS,    'tool':url_prefix+'tools/tool_config_rosdep.py' ,'dep':[] },
    5: {'tip':'一键配置:系统源(更换系统源,支持全版本Ubuntu系统)',           'type':CONFIG_TOOL,    'tool':url_prefix+'tools/tool_config_system_source.py' ,'dep':[1] },
    6: {'tip':'一键安装:NodeJS环境',      'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_nodejs.py' ,'dep':[] },
    7: {'tip':'一键安装:VsCode开发工具',      'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_vscode.py' ,'dep':[] },
    8: {'tip':'一键安装:Docker',      'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_docker.py' ,'dep':[] },
    9: {'tip':'一键安装:Cartographer(内测版易失败)',      'type':INSTALL_ROS,     'tool':url_prefix+'tools/tool_install_cartographer.py' ,'dep':[3] },
    10: {'tip':'一键安装:微信(可以在Linux上使用的微信)',      'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_wechat.py' ,'dep':[8] },
    21: {'tip':'一键安装:ROS Docker版(支持所有版本ROS/ROS2)',                'type':INSTALL_ROS,    'tool':url_prefix+'tools/tool_install_ros_with_docker.py' ,'dep':[7,8] },
    12: {'tip':'一键安装:PlateformIO MicroROS开发环境(支持Fishbot)',      'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_micros_fishbot_env.py' ,'dep':[] },
    13: {'tip':'一键配置:python国内源','type':CONFIG_TOOL,'tool':url_prefix+'tools/tool_config_python_source.py' ,'dep':[] },
    14: {'tip':'一键安装:科学上网代理工具','type':INSTALL_SOFTWARE,'tool':url_prefix+'tools/tool_install_proxy_tool.py' ,'dep':[8] },
    15: {'tip':'一键安装: QQ for Linux', 'type':INSTALL_SOFTWARE, 'tool': url_prefix+'tools/tool_install_qq.py', 'dep':[]},

    # 77: {'tip':'测试模式:运行自定义工具测试'},
    101: {'tip':'一键安装: terminator/ZSH/git/autojump', 'type':INSTALL_SOFTWARE, 'tool': url_prefix+'tools/tool_install_terminal_zsh_git_autojump.py', 'dep':[]},
    102: {'tip':'一键配置: terminator/ZSH/git/autojump', 'type':CONFIG_TOOL, 'tool': url_prefix+'tools/tool_config_terminal_zsh_git_autojump.py', 'dep':[]},
    103: {'tip':'一键配置clash客户端', 'type':CONFIG_TOOL, 'tool': url_prefix+'tools/tool_config_proxy_clash.py', 'dep':[]},
    104: {'tip':'一键安装: lazygit', 'type':INSTALL_SOFTWARE, 'tool': url_prefix+'tools/tool_install_lazygit.py', 'dep':[]},
    105: {'tip':'一键安装: pdf', 'type':INSTALL_SOFTWARE, 'tool': url_prefix+'tools/tool_install_pdf.py', 'dep':[]},

    110: {'tip':'自动安装和配置环境(先全局科学上网, terminator/git/oh-my-zsh/lazygit)', 'type':INSTALL_SOFTWARE, 'tool': '', 'dep':[101, 102, 104, 105]},
    111: {'tip':'需要手动: 截屏工具(frameshot)文件管理器(krusader)文件搜索(fsearch)视频编辑和播放软件(openshot/vlc)', 'type':INSTALL_SOFTWARE, 'tool': '', 'dep':[]},

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

    (code,out,err) = CmdTask("ls /home/*/.bashrc", 0).run()
    print("1--->")
    print(out)
    (code,out,err) = CmdTask("ls /root/.bashrc", 0).run()
    print("2--->")
    print(out)
    out = FileUtils.getbashrc()
    print("3--->")
    print(out)
    # out = FileUtils.getusers()
    # print("4--->")
    # print(out)
    out = FileUtils.getusershome()
    print("5--->")
    print(out)
    # return

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
