# 0 本地的电脑配置
## 0.1 科学上网
最好科学上网，安装流程会更简单， 因为要访问github等
方式1：直接在host中挂一个梯子，开全局（推荐这种！！！！！）
方式2：如果是启动的docker，请使用：
https://www.notion.so/docker-546bb665d06e40d195067d127365c8c7?pvs=4#db93b04358284d1393ef9c5342ce1766
这个docker是ros-noetic的版本，有网页端的可视化界面，详情请看上面的链接
- 对应的github为： https://github.com/aqiugroup/docker-ubuntu-desktop.git
- 下载镜像后，需要配置一下容器的配置参数：
  - -p 5901:5901 -p 6901:6901
  - -v /var/run/docker.sock:/var/run/docker.sock
  - -e VNC_PASSWORDLESS=true \

## 0.2 下载 terminal_config 仓库
git clone https://github.com/aqiuxx/terminal_config.git tools/terminal_config


## 0.3 配置新电脑
python3 install.py --id 110
python3 install.py --id 110 (运行两次， 一次因为安装oh-my-zsh的时候，会退出终端)
安装ros（可选）：
python3 install.py --id 1

## 0.4 其他
只要配置下
1. vim ~/.gitconfig 中的email的user
2. vim ~/.config/terminator/config 中的终端默认路径，按自己的实际需要来


# 1 工具
正常的流程应该为：
1. （如果在host中挂载了梯子，请直接直行下面的流程！）安装proxy，14:  tool_install_proxy_tool.py （会将端口export到bashrc中）, 然后手动启动clash： /root.clash/clash
   1. python3 install.py --id
      1. 方式1(第一次需要)： 启动脚本配置完成，你可以在目录: /root.clash/  运行 start_clash.sh 启动工具，启动后可通过网页：http://127.0.0.1:1234/ 进行管理
      2. 方式2： 启动脚本配置完成，你可以在目录: /root.clash/clash
2. 安装terminal等软件，101： tool_install_terminal_zsh_git_autojump.py
3. 配置terminal等软件，102： tool_config_terminal_zsh_git_autojump.py
   1. 如果装zsh插件失败，请打开103
4. 下载其他软件，如
   1. 103： tool_config_proxy_clash.py (如果在host中挂载了梯子，请直接直行下面的流程！)
   2. 104： tool_install_lazygit.py
   3. 105： tool_install_pdf.py
   4. 7: tool_install_vscode.py


## proxy ： clash
'''
1.桌面快捷方式：需要先右击允许执行才能使用
2.可以在终端中直接运行脚本启动,直接输入:$HOME/.clash/start_clash.sh
    方式1(第一次需要)： 启动脚本配置完成，你可以在目录: /root.clash/  运行 start_clash.sh 启动工具，启动后可通过网页：http://127.0.0.1:1234/ 进行管理
    方式2： 启动脚本配置完成，你可以在目录: /root.clash/clash
3.终端通过环境变量设置: export http_proxy=http://127.0.0.1:7890 && export https_proxy=http://127.0.0.1:7890
4.配置系统默认代理方式: 系统设置->网络->网络代理->手动->HTTP(127.0.0.1 7890)->HTTPS(127.0.0.1 7890)
'''

## 1.1 terminal、zsh、git、autojump

## 1.2 lazygit
如果lazygit的压缩包下载不下来， 就直接手动下载一份到tools目录下， 重命名为lazygit.tar.gz
可以先运行看下，最新的版本号
```
sh install_lazygit.sh
# 假设输出为 0.40.2， 则 手动下载即可：
https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_0.40.2_Linux_x86_64.tar.gz
```

## 1.3 zsh插件
如果下载不下来先安装， proxy
```
git clone https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions'
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting'
```
