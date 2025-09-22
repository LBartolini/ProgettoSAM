from typing import Mapping, List
from github_scraper.dependency_file import DependencyFile
from github_scraper.github import Github
import math
from time import sleep

class Builder:
    def __init__(self, 
                 language_dict: Mapping[str, Mapping[str, DependencyFile]],
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
                        
                        files_to_search = [v.filename for v in self.language_dict[language].values()]
                        
                        files_found = self.github.get_files_from_repo(repo['full_name'], files_to_search=files_to_search)
                        
                        for file_searched in files_found.keys():
                            dependency_set = set()
                            
                            for url_to_download in files_found[file_searched]:
                                content = self.language_dict[language][file_searched].download_file(url_to_download)
                                dependency_set.update(self.language_dict[language][file_searched].extract_dependencies(content))
                                
                            print(dependency_set)
                            