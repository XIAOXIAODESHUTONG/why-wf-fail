import access_api
import filter_error
import format_data
import pandas as pd
import display_data


if __name__ == '__main__':

    lists = ["PyGithub/PyGithub", "ytdl-org/youtube-dl", "rust-lang/rust", "httpie/httpie"]
    print("This is wcy's project")
    while True:
        print("Please select which function to use")
        print("1: Get workflow files and history log files from one repository in GitHub.")
        print("2: Get workflow files and history log files from repositories in GitHub.")
        print("3: Filter out the info with error from the log file and store it in the dataframe.")
        print("4: Display the data.")
        print("0: Press 0 to exit")
        select_num = input()
        if select_num == "1":
            print("Please select the repository you want to acquire.")
            print("We have these default repositories: ")
            print("1, PyGithub, 2, youtube-dl, 3, rust, 4, httpie, 5, type the repository u want")
            res_num = int(input())
            if 0 < res_num < 5:
                res_num -= 1
                res_name = lists[res_num]
                access_api.run_get_log(res_name, {"log_id": [], "commit_detail": []})
            elif res_num == 5:
                res_name = input("Please type the repository name. Like PyGithub/PyGithub")
                access_api.run_get_log(res_name, {"log_id": [], "commit_detail": []})
            else:
                print("Wrong number")
        if select_num == "2":
            for repo_name in lists:
                access_api.run_get_log(repo_name, {"log_id": [], "commit_detail": []})
        if select_num == "3":
            id_num = 0
            data_collection = pd.DataFrame()
            for name in ["PyGithub/PyGithub"]:
                # format_data.run(name.split("/")[1])
                data_collection = filter_error.run(name.split("/")[1], id_num, data_collection)
                id_num += 1
        if select_num == "4":
            display_data.run()
        if select_num == "0":
            break






