import os
import requests
from github import Github
import re
import pandas as pd

token = ''
fine_grained_token = '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'
cookie = '_ga=GA1.2.2015594702.1511353957; _device_id=b42dbb502fa0351a74be9857a393ff2e; _octo=GH1.1.14320389.1643447003; user_session=Rgjwhvu_lt_Qxf_vEh7-L2pdpEbo85YnhfdOJ39LGLSlV55X; __Host-user_session_same_site=Rgjwhvu_lt_Qxf_vEh7-L2pdpEbo85YnhfdOJ39LGLSlV55X; logged_in=yes; dotcom_user=XIAOXIAODESHUTONG; color_mode={"color_mode":"auto","light_theme":{"name":"light","color_mode":"light"},"dark_theme":{"name":"dark","color_mode":"dark"}}; preferred_color_mode=light; tz=Asia/Shanghai; has_recent_activity=1; _gh_sess=WstAZjDqOHaSgz63A4DV1ndkTcQIv77AGLltRw516OYed2Cn2RyP5qi2blMDQfzlu7kH3cYbJi5F99pZu6MMqCLRASa5wCz28xuq9lIF7Biu/wt4V1As7x5KVg9MrZuX5zsYw24AViE1fZQO9LWPZ58zuP8THz4IUuuscwLBTRnZDe6tF4V8J3NA+9MkMRCX3I18IuHLI6wpYDoQ0msGA+Wvhu1US+p/vNW+o9UM3zmQhQjRRUN2j63zqKdlGXtoaKFoSHH919zpw14Kc1QKsi/p8iSJomZYIWBDbonoQQaHFi+Yqex+sRW5DLg8y0I3u/tFEqISa1G9h52dLQl/SJO/Q6KEYSuB--vdYRwYxWF8NsyqWe--uxLRCWZJrSoGUhokqZ0ByQ=='
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'


def get_workflow(repo_name):
    url = "https://api.github.com/repos/" + repo_name + "/actions/workflows"
    headers = {"Authorization": token,
               "Accept": "application/vnd.github+json", }
    response = requests.get(url, headers=headers)
    data_ori = response.json()
    g = Github(token)
    repo = g.get_repo(repo_name)
    workflow_runs = repo.get_workflows()
    workflow_list = {}
    for num in range(100):
        data = workflow_runs.get_page(num)
        if len(list(data)) == 0:
            break
        for work in data_ori["workflows"]:
            try:
                workflow_list[work['name']] = work['id']
                content_file = repo.get_contents(work["path"])
                workflow = content_file.decoded_content.decode()
                project_name = repo_name.split("/")[1]
                is_exists = os.path.exists(project_name)
                if not is_exists:
                    os.mkdir(project_name)
                with open(project_name + "\\" + work['name'] + ".txt", "w+") as f:
                    f.writelines(workflow)
            except Exception:
                print("no yml file")
                continue


def download_zip(repo_name, down_url, commit_detail):
    res_id = r'actions/workflow-run/(.*?)"'
    headers = {"user-agent": user_agent}
    down_response, flag = get_required_data(down_url, headers)
    headers["cookie"] = cookie
    if len(flag) != 0 and flag[0] == "There are no workflow runs yet.":
        save_commit(repo_name.split("/")[1] + "\\", commit_detail)
        return True
    id_co = re.findall(res_id, down_response.text)
    path_coll = filter_job_path(down_response.text)
    status = check_if_out_of_date(path_coll)
    climb_path(path_coll, id_co, commit_detail)
    work_flow_name = re.findall(r'<span class="text-bold" >(.*)</span>', down_response.text)

    for log_id, name in zip(id_co, work_flow_name):
        data_co = {"repo_name": repo_name, "log_id": log_id, "headers": headers,
                   "path": repo_name.split("/")[1] + "\\" + name}
        create_folder(data_co)
        data_co["zip_package"] = download(data_co, "1")
        if data_co["zip_package"].status_code == 404:
            data_co["zip_package"] = download(data_co, "2")
        save_zip_file(data_co)
        print(data_co["zip_package"])
    if status:
        save_commit(repo_name.split("/")[1] + "\\", commit_detail)
        return True
    return False


def check_if_out_of_date(path_coll):
    res_li = r'<li data-test-selector="job-link" data-turbo="false"(.*?) data-view-component="true" class="ActionListContent'
    res_href = r'href="(.*?)"'
    res_h4 = r'<h4 class="color-fg-muted text-mono f5 text-normal">(.*?)</h4>'
    headers = {"user-agent": user_agent}
    for path in path_coll:
        url = "https://github.com/" + path
        session = requests.session()
        down_response = session.get(url, headers=headers)
        need_an = re.findall(res_li, down_response.text, re.S | re.M)
        if len(need_an) > 0:
            sub_job_url = re.findall(res_href, need_an[0], re.S | re.M)
            url = "https://github.com/" + sub_job_url[0]
            down_response = session.get(url, headers=headers)
            status = re.findall(res_h4, down_response.text, re.S | re.M)
            if len(status) > 0 and status[0] == "The logs for this run have expired and are no longer available.":
                return True
    return False


def get_required_data(down_url, headers):
    session = requests.session()
    down_response = session.get(down_url, headers=headers)
    flag = re.findall(r'" class="mb-1">(.*)</h3>', down_response.text)
    return down_response, flag


def create_folder(data_co):
    is_exists = os.path.exists(data_co["path"])
    if not is_exists:
        os.mkdir(data_co["path"])


def download(data_co, num):
    down_zip_url = "https://github.com/" + data_co["repo_name"] + "/suites/" + data_co["log_id"] + "/logs?attempt=" + num
    print(down_zip_url)
    print(data_co["headers"])
    zip_package = requests.get(down_zip_url, headers=data_co["headers"], )
    return zip_package


def save_zip_file(data_co):
    with open(data_co["path"] + "\\" + data_co["log_id"] + '.zip', 'wb') as f:
        f.write(data_co["zip_package"].content)


def run_get_log(repo_name, commit_detail):
    get_workflow(repo_name)
    for num in range(1, 100):
        print(num)
        down_url = "https://github.com/" + repo_name + "/actions?page=" + str(num)
        stop_flag = download_zip(repo_name, down_url, commit_detail)
        if stop_flag:
            print("exit ", num)
            break


def save_commit(path, commit_detail):
    df = pd.DataFrame(commit_detail)
    df.to_csv(path + 'log_commit_detail.csv', index=False)
    commit_detail["log_id"] = []
    commit_detail["commit_detail"] = []


def climb_path(path_coll, id_co, commit_detail):
    commit_detail_coll = climb_log_commit_path(path_coll)
    for log_id, commit in zip(id_co, commit_detail_coll):
        commit_detail["log_id"].append(log_id)
        commit_detail["commit_detail"].append(commit)


def climb_log_commit_path(path_coll):
    res_href = r'<a href="(.*?)" class="text-mono Link--secondary no-underline">'
    res_span = r'<span >(.*?)</span>'
    res_exec = r'<span class="color-fg-muted" style="font-weight: 400">(.*?)</span>'
    commit_detail_coll = []
    for log_path in path_coll:
        url = "https://github.com/" + log_path + "/workflow"
        session = requests.session()
        down_response = session.get(url, headers={"user-agent": user_agent})
        path = re.findall(res_href, down_response.text)
        exec_co = re.findall(res_exec, down_response.text)
        if len(exec_co) > 0:
            exec_num = exec_co[0]
        else:
            exec_num = ""
        if len(path) > 0:
            path = "https://github.com/" + path[0]
            commit_name = re.findall(res_span, down_response.text, re.S | re.M)
            commit_name = commit_name[0].strip()
            commit_detail_coll.append([commit_name, path, exec_num, url])
        else:
            commit_detail_coll.append(["", "", exec_num, url])
    return commit_detail_coll


def filter_job_path(text):
    # 先从主界面爬取编号，跟log文件编号不同
    res_span = r'<span class="h4 d-inline-block text-bold lh-condensed mb-1 width-full">(.*?)</span>'
    m_span = re.findall(res_span, text, re.S | re.M)
    path_coll = []
    for line in m_span:
        path = re.findall(r'href="(.*?)"', line)
        path_coll.extend(path)
    return path_coll


def api_log():
    url = "https://api.github.com/repos/rust-lang/rust/actions/runs/3388085006/logs"
    headers = {"Authorization": token,
               "Accept": "application/vnd.github+json", }
    response = requests.get(url, headers=headers)
    data_ori = response.json()
    print()
    print("requested url: ", url)
    print(data_ori)
    url = "https://api.github.com/repos/rust-lang/rust/actions/runs/3387819190/jobs"
    headers = {"Authorization": token,
               "Accept": "application/vnd.github+json", }
    response = requests.get(url, headers=headers)
    data_ori = response.json()
    print()
    print("requested url: ", url)
    print(data_ori)

