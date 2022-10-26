import os
import requests
from github import Github
import re

token = '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'
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


def download_zip(repo_name, down_url):
    headers = {"user-agent": user_agent}
    down_response, flag = get_required_data(down_url, headers)
    headers["cookie"] = cookie
    if len(flag) != 0 and flag[0] == "There are no workflow runs yet.":
        return True
    id_co = re.findall('(?<=actions/workflow-run/)\d+', down_response.text)
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


def run_get_log(repo_name):
    get_workflow(repo_name)
    for num in range(1, 100):
        print(num)
        down_url = "https://github.com/" + repo_name + "/actions?page=" + str(num)
        stop_flag = download_zip(repo_name, down_url)
        if stop_flag:
            print("exit ", num)
            break
