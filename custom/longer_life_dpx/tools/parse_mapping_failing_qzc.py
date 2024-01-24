import os
import sys
# import openpyxl
# import pandas as pd
# import collections
# import subprocess

import numpy as np

print(__file__)

# import sys
# sys.path.append(os.path.dirname(__file__)+"/../..")
# import common.file_operate as file_operate


np.set_printoptions(linewidth=200,
                    formatter={'float': lambda x: "{:6.3f}".format(x)})





import collections
# 3. 广度优先遍历，按层遍历  了解
def traverse_by_brand(path, prefix, suffix, depth=100, get_dir_only = False):
    allfile = []
    LogFileNames = []
    LogDirPath = []
    root_depth = len(path.split(os.path.sep))

    queue = collections.deque()
    queue.append(path)  # 先入队
    while len(queue) > 0:
        item = queue.popleft() #左边出队
        childs = os.listdir(item)  # 获取所有的项目（目录，文件）
        for current in childs:
            abs_path = os.path.join(item, current)  # 绝对路径

            # 大于给定深度，返回
            dir_depth = len(abs_path.split(os.path.sep))
            if dir_depth > root_depth + depth + 1:
                return allfile, LogFileNames, LogDirPath

            if os.path.isdir(abs_path) or get_dir_only == True:  # 如果是目录，则入队
                queue.append(abs_path)

                if get_dir_only == True:
                    if current.startswith(prefix) and current.endswith(suffix):
                        allfile.append(abs_path)
                        LogFileNames.append(current)
                        LogDirPath.append(item)
            else:
                print(current)  # 输出
                if current.startswith(prefix) and current.endswith(suffix):
                    allfile.append(abs_path)
                    LogFileNames.append(current)
                    LogDirPath.append(item)

    return allfile, LogFileNames, LogDirPath


def get_key (dict, value):
    """ 给定字典, 通过value, 返回key

    Args:
        dict (dict): 待查字典
        value (str): 待查value

    Returns:
        str: 返回对应的key
    """
    rst = [k for k, v in dict.items() if v == value]
    if len(rst) == 0:
        return ""
    else:
        return rst[0]

log_to_fail_result_map = {
    "found loop closure while mapping": "found loop closure while mapping, 回环>8m",
    "Error: signal": "pre_module.cc crash 崩溃",
    "abort mapping by user": "abort mapping by user, 用户中断",
    "vehicle backed too far": "vehicle backed too far, 倒车距离过长",
    "don't detect enter slope point": "don't detect enter slope point, 没找到入坡点",
    "2D odo state is abnormal": "2D odo state is abnormal, 2d里程计异常",
    "global planning planning failed": "global planning planning failed, 全局路径规划失败",
    # "Catch ctrl+c event": "Catch ctrl+c event",
    "Mapping.log is empty": "空目录, 无log",
    "underground-in/sp_map.ndm": "成功",
}

def parse_fail_result(log_file):
    """ 通过检查 日志文件中的每一行,是否包含 log_to_fail_result_map 中的日志,
        如果有, 则查找对应的原因, 并返回
        如果文件不存在, 直接返回 "空目录, 无log"

    Args:
        log_file (str): 输入的日志文件

    Returns:
        str:  输出失败原因
    """
    fail_result = ""
    if not os.path.exists(log_file):
        fail_result = log_to_fail_result_map['Mapping.log is empty']
    else:
        fail_results = []
        with open(log_file,'r') as f:    #设置文件对象
            while True:
                line = f.readline()  #读取一行文件，包括换行符
                # line = line[:-1]     #去掉换行符，也可以不去
                if line:
                    for key, value in log_to_fail_result_map.items():
                        if key in line:
                            # fail_result = value
                            fail_results.append(value)
                            # print(key, value)
                else:
                    break

        if len(fail_results) > 0:
            fail_result = fail_results[0]

    return fail_result

import pandas as pd
def read_csv_txt(csv_path):
    tfs = pd.read_csv(csv_path, encoding="utf8")
    return tfs

def save_map_to_csv(output_csv, key_to_vals_map, labels):
    # city = pd.DataFrame([['Sacramento', 'California'], ['Miami', 'Florida']], columns=['id', 'name'])
    pd_key_to_vals = pd.DataFrame({labels[0]: key_to_vals_map.keys(), labels[1]: key_to_vals_map.values()})
    pd_key_to_vals.to_csv(output_csv, index=False, header=True)

if __name__=="__main__":
    dir = os.path.dirname(__file__)
    src_dir = os.getcwd()
    print(sys.argv[0])
    print(__file__)
    print(dir)
    print(src_dir)
    dir = src_dir
    print("!!!")

    ##### 1 解析所有的数据
    dir_name_to_id_map = {}
    [logFiles, Filenames, LogDirPaths] = traverse_by_brand(dir+"/log", "", "", 0, True) # 0代表当前目录
    for idx in range(0, len(logFiles)):
        log_file = logFiles[idx]
        file_name = Filenames[idx]
        LogDirPath = LogDirPaths[idx]
        dir_name_to_id_map[file_name.split('daq_')[-1]] = idx
        # print("id :{}, file: {}".format(idx, log_file))

    mapping_result_csv = dir + "/0.0.16_1.csv"
    mapping_result_csv_out = dir + "/0.0.16_2.csv"
    log_name_to_fail_reason_out = dir + "/log_name_to_fail_reason_out_qzc.csv"
    if os.path.exists(mapping_result_csv):
        mapping_result_pd = read_csv_txt(mapping_result_csv)

        mapping_path = mapping_result_pd['数据路径']
        mapping_flag = mapping_result_pd['建图成功']
        # for k, v in zip(mapping_flag, mapping_flag):
        #     print("数据集路径: {}, 建图成功: {}".format(k, v))

        # mapping_flag_false = mapping_flag.isin(['否']).values
        index_false = np.where(mapping_flag.values == '否')[0]
        # mapping_flag_false = mapping_flag[index_false]

        cnt = 0

        log_name_to_fail_reason_map = {}

        csv_id_to_fail_result_map = {}
        for csv_id in index_false:
            #### 1 解析目录名称
            m_path_name = mapping_path[csv_id].split('/')[1]

            #### 2 查找对应目录
            find_it_id = dir_name_to_id_map.get(m_path_name)
            if find_it_id is not None:
                print("query: {} id {} dir {}".format(m_path_name, find_it_id, logFiles[find_it_id]))
                cnt = cnt + 1

                #### 3 判断失败原因: 目录为空 或 提取失败日志
                mapping_log = logFiles[find_it_id]+"/Mapping.log"
                csv_id_to_fail_result_map[csv_id] = parse_fail_result(mapping_log)

                log_name_to_fail_reason_map[m_path_name] = csv_id_to_fail_result_map[csv_id]


        # 4 写到新的csv文件中:
        # mapping_result_pd.insert(9, 'log', "")
        # mapping_result_pd.insert(10, "cause", "")
        mapping_result_pd.insert(11, 'log2', "")
        mapping_result_pd.insert(12, "cause2", "")
        for key, value in csv_id_to_fail_result_map.items():
                mapping_result_pd['log2'].iloc[key] = get_key(log_to_fail_result_map, value)
                mapping_result_pd['cause2'].iloc[key] = value

        mapping_result_pd.to_csv(mapping_result_csv_out, index=False, header=True)

        # 5 保存中间文件, 用于后续只跑失败的部分
        save_map_to_csv(log_name_to_fail_reason_out, log_name_to_fail_reason_map, ["log_name", "fail_reason"])
        print("一共解析{}个文件!".format(cnt))


    print("Finish!")
