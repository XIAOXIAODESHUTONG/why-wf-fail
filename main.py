import access_api
import filter_error
import format_data


def run():
    lists = ["PyGithub/PyGithub", "ytdl-org/youtube-dl", "aria2/aria2", "httpie/httpie", "rust-lang/rust"]
    lists = ["PyGithub/PyGithub"]
    # for repo_name in lists:
    #     access_api.run_get_log(repo_name)
    for name in lists:
        # format_data.run(name.split("/")[1])
        filter_error.run(name.split("/")[1])


if __name__ == '__main__':
    run()

