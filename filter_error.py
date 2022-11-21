import os
import re

import pandas as pd
from format_data import get_file_name, get_txt_file, unzip_file


def run(name):
    data_collection = pd.DataFrame()
    work_flow_co = {}
    list_wf = get_file_name(name, "txt")
    for wl in list_wf:
        file_dic = pd.DataFrame()
        file_content = get_txt_file(name + "\\" + wl)
        wl = wl.split(".")[0]
        work_flow_co[wl] = file_content
        list_log = get_file_name(name + "\\" + wl, "zip")
        for log_name in list_log:
            # log_content = pd.DataFrame()
            flag = unzip_file(name + "\\" + wl, log_name)
            if not flag:
                continue
            file_dic = get_folder_content(file_dic, name + "\\" + wl + "\\" + log_name.split(".")[0], log_name.split(".")[0])
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 100)
        pd.set_option('display.width', 1000)
        print(file_dic)
        file_dic.to_csv(name + "\\" + wl + '_log_error.csv', index=False)


def get_folder_content(data_co, path, log_number):
    for file in os.listdir(path):
        # file is also the job name
        if file.endswith(".txt"):
            continue
        for file_step in os.listdir(path + "\\" + file):
            if file_step.endswith(".txt"):
                f = open(path + "\\" + file + "\\" + file_step, 'r', encoding="utf-8")
                content = f.readlines()
                error_coll = deal_log_content(content)
                if len(error_coll) != 0:
                    sub_column = {"job name": file, "log number": log_number, "file step": file_step.split(".")[0],
                                  "error collection": error_coll}
                    if len(data_co) == 0:
                        data_co = pd.DataFrame(sub_column)
                    else:
                        data_co.loc[len(data_co)] = sub_column
                f.close()
        # print(data_co)
    return data_co


def sort_store_data(data_co, content, step_name, file_num):
    df_co = pd.DataFrame(content)
    if step_name not in data_co:
        data = {file_num: df_co}
        # df[file_num] = pd.DataFrame(content)
        data_co[step_name] = data
    else:
        data_co[step_name][file_num] = df_co


def deal_log_content(content):
    error_coll = []
    for row in content:
        error = re.findall(r'\[error\](.*)', row)
        if len(error) != 0:
            error_coll.extend(error)
    return error_coll
