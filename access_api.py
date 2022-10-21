import os
import requests
from github import Github
import re


def get_workflow(repo_name):
    url = "https://api.github.com/repos/" + repo_name + "/actions/workflows"
    headers = {"Authorization": "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",
               "Accept": "application/vnd.github+json", }
    response = requests.get(url, headers=headers)
    data_ori = response.json()
    g = Github("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")
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
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"}
    session = requests.session()
    # 下载页面
    down_response = session.get(down_url, headers=headers)
    flag = re.findall(r'" class="mb-1">(.*)</h3>', down_response.text)
    if len(flag) != 0 and flag[0] == "There are no workflow runs yet.":
        return True
    id_co = re.findall('(?<=actions/workflow-run/)\d+', down_response.text)
    # print(id_co)
    work_flow_name = re.findall(r'<span class="text-bold" >(.*)</span>', down_response.text)
    for log_id, name in zip(id_co, work_flow_name):
        project_name = repo_name.split("/")[1]
        path = project_name + "\\" + name
        is_exists = os.path.exists(path)
        if not is_exists:
            os.mkdir(path)  # 正常
        cookie = '_ga=GA1.2.2015594702.1511353957; _device_id=b42dbb502fa0351a74be9857a393ff2e; _octo=GH1.1.14320389.1643447003; user_session=Rgjwhvu_lt_Qxf_vEh7-L2pdpEbo85YnhfdOJ39LGLSlV55X; __Host-user_session_same_site=Rgjwhvu_lt_Qxf_vEh7-L2pdpEbo85YnhfdOJ39LGLSlV55X; logged_in=yes; dotcom_user=XIAOXIAODESHUTONG; has_recent_activity=1; color_mode={"color_mode":"auto","light_theme":{"name":"light","color_mode":"light"},"dark_theme":{"name":"dark","color_mode":"dark"}}; preferred_color_mode=light; tz=Asia/Shanghai; _gh_sess=wwthoHf03Uyq6eb3vdMwz8LRbTXP8ZQ9tjPSzcTYki+vr862/t7sqa0XhqW58bkBYO6OsS6bFNRBTtj36nxzkbdzjWzS0TuTSirDfiOry7yp7FuVphL7q8Fj0kSJdxVXm62Ip2jUTOCEbcIWfrqTg8wa47SB0XeAbVxTwjRDXyz4XMliUC/4GSqJxf/n3LPfj1eB+wY7KB6ihDRIwq6+A0kSqnsaqJtsmpOqn+oXfvoDI+2z2+6GAZqPSmffbudNtm/F1ylgaea/yh+xV7c/JgkQj4wioP+ndVMZZcT5cok=--Pdxupc/CTLTrJJqF--yLUtajaGX3m7e4xiLFTajA=='
        headers["cookie"] = cookie
        down_zip_url = "https://github.com/" + repo_name + "/suites/" + log_id + "/logs?attempt=1"
        r = requests.get(down_zip_url, headers=headers,)
        if r.status_code == 404:
            down_zip_url = "https://github.com/" + repo_name + "/suites/" + log_id + "/logs?attempt=2"
            r = requests.get(down_zip_url, headers=headers, )
        print(r)
        with open(path + "\\" + log_id + '.zip', 'wb') as f:
            f.write(r.content)
    return False


def run_get_log(repo_name):
    get_workflow(repo_name)
    for num in range(1, 100):
        print(num)
        down_url = "https://github.com/" + repo_name + "/actions?page=" + str(num)
        stop_flag = download_zip(repo_name, down_url)
        if stop_flag:
            print("exit ", num)
            break
