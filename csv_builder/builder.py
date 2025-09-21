from typing import Mapping, List
from github_scraper.dependency_file import DependencyFile, PackageJson
from github_scraper.github import Github
import os

class Builder:
    def __init__(self, 
                 language_dict: Mapping[str, List[DependencyFile]],
                 github: Github,
                 output_folder: str = "/output"):
        self.language_dict = language_dict
        self.github = github
        self.output_folder = output_folder
        
    def build_all_csv(self, repositories_per_page:int=100, verbose:bool=False):
        if verbose: print("Starting CSV build loop")
        
        for language in self.language_dict.keys():
            if verbose: print(f"\nStarting with language {language}")
            
            total_repositories_found = self.github.call_repository_api(language=language)["total_count"]
            total_github_repo_rounds = int(total_repositories_found/repositories_per_page)
            #TODO "message": "Only the first 1000 search results are available"
            
            if verbose: print(f"Found {total_repositories_found} repositories. Total rounds to do is {total_github_repo_rounds}")
            
            for github_repo_index in range(total_github_repo_rounds):
                if verbose: print(f"Now GITHUB_REPO_INDEX={github_repo_index}")
            
    

# Tests from command line, not the purpose of this script
if __name__ == "__main__":
    if (token := os.environ.get("GITHUB_ACCESS_TOKEN")) is None:
        exit("Please set environment variable GITHUB_ACCESS_TOKEN")
        
    b = Builder({"js": [PackageJson()]}, Github(token))
    
    b.build_all_csv(verbose=True)