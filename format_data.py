import os
import zipfile
import tools
import pandas as pd


def run(name):
    data_collection = {}
    work_flow_co = {}
    list_wf = get_file_name(name, "txt")
    for wl in list_wf[:1]:
        file_content = get_txt_file(name + "\\" + wl)
        wl = wl.split(".")[0]
        work_flow_co[wl] = file_content
        # data_collection[wl] = file_content
        list_log = get_file_name(name + "\\" + wl, "zip")
        for log_name in list_log:
            file_dic = {}
            flag = unzip_file(name + "\\" + wl, log_name)
            if not flag:
                continue
            get_folder_content(file_dic, name + "\\" + wl + "\\" + log_name.split(".")[0])
            data_collection[wl + "_" + log_name.split(".")[0]] = file_dic

    log_df = pd.DataFrame(data_collection)
    wf_df = pd.DataFrame(work_flow_co)
    print(log_df)
    print(wf_df)


def get_txt_file(name):
    file_content = []
    with open(name, "r") as f:
        for line in f.readlines():
            line = line.strip('\n')  # 去掉列表中每一个元素的换行符
            file_content.append(line)
    return file_content


def get_folder_content(data_co, path):
    for file in os.listdir(path):
        if file.endswith(".txt"):
            f = open(path + "\\" + file, 'r', encoding="utf-8")
            content = f.readlines()
            data_co[file.split(".txt")[0]] = content
        else:
            get_folder_content(data_co, path + "\\" + file)
    return


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
