import access_api


def run():
    lists = ["PyGithub/PyGithub", "ytdl-org/youtube-dl", "aria2/aria2", "httpie/httpie"]
    for repo_name in lists:
        access_api.run_get_log(repo_name)


if __name__ == '__main__':
    run()

