from git import Repo, InvalidGitRepositoryError


class GitHubConnector:

    def __init__(self, working_dir, github_url):
        self.__working_dir = working_dir
        self.__github_url = github_url

    def getSourceFiles(self):
        # Try to load the existing repository. If that fails, clone the repo instead.
        try:
            repo = Repo(self.__working_dir)
        except InvalidGitRepositoryError:
            repo = Repo.clone_from(self.__github_url, self.__working_dir)

        repo.heads.master.checkout(True)  # forced
        del repo  # see 'Limitations: Leakage of System Resources' in GitPythin documentation.
