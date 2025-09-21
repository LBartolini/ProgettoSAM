from typing import Mapping, List
from github_scraper.dependency_file import DependencyFile
from github_scraper.github import Github
import math
from time import sleep

class Builder:
    def __init__(self, 
                 language_dict: Mapping[str, List[DependencyFile]],
                 github: Github,
                 star_ranges: List[str] = ["19..22", "50..65", "150..240", "450..999", ">1800"],
                 output_folder: str = "/output"):
        self.language_dict = language_dict
        self.github = github
        self.output_folder = output_folder
        self.star_ranges = star_ranges
        
    def build_all_csv(self, results_per_page:int=100, verbose:bool=False):
        if verbose: print("Starting CSV build loop")
        
        for language in self.language_dict.keys():
            if verbose: print(f"\nStarting with language {language}")
            
            for star_range in self.star_ranges:
                if verbose: print(f"Star range {star_range}")
                total_repositories_found = self.github.call_repository_api(language=language, stars=star_range, per_page=1)["total_count"]
                total_github_repo_rounds = min(math.ceil(total_repositories_found/results_per_page), 10)
                
                if verbose: print(f"Found {total_repositories_found} repositories. Total rounds to do is {total_github_repo_rounds}")
                
                for github_repo_index in range(1, total_github_repo_rounds+1):
                    if verbose: print(f"Now GITHUB_REPO_INDEX={github_repo_index}")
                    repositories = self.github.call_repository_api(language=language, stars=star_range, page=github_repo_index)['items']
                    
                    for repo in repositories:
                        if verbose: print(f"Repo {repo['full_name']}")
                        
                        for dependency_file in self.language_dict[language]:
                            if verbose: print(f"Searching file {dependency_file.filename}.{dependency_file.extension}")
                            
                            print(self.github.call_code_api(repo['full_name'], dependency_file.filename, dependency_file.extension, per_page=1))
                            
                            total_dependency_file_found = self.github.call_code_api(repo['full_name'], dependency_file.filename, dependency_file.extension, per_page=1)["total_count"]
                            total_dependency_file_rounds = min(math.ceil(total_dependency_file_found/results_per_page), 10)
                            
                            for github_file_index in range(1, total_dependency_file_rounds+1):
                                self.github.call_code_api(repo['full_name'], dependency_file.filename, dependency_file.extension, page=github_file_index)
                    
            