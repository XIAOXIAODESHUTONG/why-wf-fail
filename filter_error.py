import ast
import os
import re

import pandas as pd
from format_data import get_file_name, get_txt_file, unzip_file


def run(name, id_num, data_collection):
    work_flow_co = {}
    list_wf = get_file_name(name, "txt")
    dic_path = read_path_csv(name)
    for wl in list_wf:
        file_content = get_txt_file(name + "\\" + wl)
        wl = wl.split(".")[0]
        work_flow_co[wl] = file_content
        list_log = get_file_name(name + "\\" + wl, "zip")
        for log_name in list_log:
            # log_content = pd.DataFrame()
            flag = unzip_file(name + "\\" + wl, log_name)
            if not flag:
                continue
            data_collection = get_folder_content(data_collection, name + "\\" + wl + "\\" + log_name.split(".")[0],
                                                 log_name.split(".")[0], name, id_num, dic_path, wl)
    return data_collection


def get_folder_content(data_co, path, log_number, repo_name, id_num, dic_path, wl):
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
                    # sub_column = {"job name": file, "log number": log_number, "file step": file_step.split(".")[0],
                    #               "error collection": error_coll}
                    for error in error_coll:
                        num = str(log_number)
                        if num in dic_path.keys():
                            commit = ast.literal_eval(dic_path[num])
                            sub_column = {"repo name": repo_name, "id number": id_num, "workflow name": wl,
                                          "workflow path": commit[3], "execution number": commit[2],
                                          "commit message": commit[0], "commit path": commit[1],
                                          "job name": file_step.split(".")[0], "log number": log_number,
                                          "error message": error}
                        else:
                            sub_column = {"repo name": repo_name, "id number": id_num, "workflow name": wl,
                                          "workflow path": "", "execution number": "",
                                          "commit message": "", "commit path": " ",
                                          "job name": file_step.split(".")[0], "log number": log_number,
                                          "error message": error}
                        if len(data_co) == 0:
                            data_co = pd.DataFrame([sub_column])
                        else:
                            data_co.loc[len(data_co)] = sub_column
                f.close()
    return data_co


def sort_store_data(data_co, content, step_name, file_num):
    df_co = pd.DataFrame(content)
    if step_name not in data_co:
        data = {file_num: df_co}
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


def read_path_csv(name):
    dic_path = {}
    df = pd.read_csv(name + '//log_commit_detail.csv')
    for num, commit in zip(df["log_id"], df["commit_detail"]):
        dic_path[str(num)] = commit
    return dic_path

