import os
import zipfile
from tool import tools
import pandas as pd


def run(name):
    data_collection = {}
    work_flow_co = {}
    list_wf = get_file_name(name, "txt")
    for wl in list_wf:
        file_dic = {}
        file_content = get_txt_file(name + "\\" + wl)
        wl = wl.split(".")[0]
        work_flow_co[wl] = file_content
        list_log = get_file_name(name + "\\" + wl, "zip")
        for log_name in list_log:
            flag = unzip_file(name + "\\" + wl, log_name)
            if not flag:
                continue
            get_folder_content(file_dic, name + "\\" + wl + "\\" + log_name.split(".")[0], log_name.split(".")[0])
        data_collection[wl] = file_dic
    log_df = pd.DataFrame(data_collection)
    wf_df = pd.DataFrame(work_flow_co)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('max_colwidth', 100)
    pd.set_option('display.width', 1000)
    log_df.to_csv(name + '_log.csv', index=False)
    wf_df.to_csv(name + '_workflow.csv', index=False)


def get_txt_file(name):
    file_content = []
    with open(name, "r") as f:
        for line in f.readlines():
            line = line.strip('\n')  # 去掉列表中每一个元素的换行符
            file_content.append(line)
    return file_content


def get_folder_content(data_co, path, log_number):
    for file in os.listdir(path):
        if file.endswith(".txt"):
            continue
        for file_step in os.listdir(path + "\\" + file):
            if file_step.endswith(".txt"):
                f = open(path + "\\" + file + "\\" + file_step, 'r', encoding="utf-8")
                content = f.readlines()
                sort_store_data(data_co, deal_log_content(content), file_step.split(".txt")[0], log_number)
                f.close()


def sort_store_data(data_co, content, step_name, file_num):
    df_co = pd.DataFrame(content)
    if step_name not in data_co:
        data = {file_num: df_co}
        data_co[step_name] = data
    else:
        data_co[step_name][file_num] = df_co


def add_top_column(df, top_col, inplace=False):
    if not inplace:
        df = df.copy()

    df.columns = pd.MultiIndex.from_product([[top_col], df.columns])
    return df


def deal_log_content(content):
    file_content = {}
    time_co = []
    content_co = []
    for row in content:
        time_stamp = row[:28]
        content = row[29:]
        time_co.append(time_stamp)
        content_co.append(content)
    file_content["time_stamp"] = time_co
    file_content["log_content"] = content_co
    return file_content


def get_file_name(path, suffix):
    list_wf = []
    for file in os.listdir(path):
        if file.endswith("." + suffix):
            list_wf.append(file)
    return list_wf


def unzip_file(path, log_name):
    zip_file_name = path + '\\' + log_name
    if zipfile.is_zipfile(zip_file_name):
        out_path = path + '\\' + log_name.split(".")[0]
        tools.create_folder(zip_file_name)
        extracting_zip_content(zip_file_name, out_path)
        return True
    return False


def extracting_zip_content(zip_file_name, out_path):
    with zipfile.ZipFile(zip_file_name, 'r') as z_file:
        z_file.extractall(out_path)
    z_file.close()
