from typing import Mapping, List

from github_scraper.dependency_file import DependencyFile
from github_scraper.github import Github

from vuln_scraper.shodan import Shodan
from vuln_scraper.sploitus import Sploitus
from vuln_scraper.deps_dev import DepsDev
from vuln_scraper.osv_dev import OSDev

import math

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
        self.shodan = Shodan()
        self.sploitus = Sploitus()
        self.deps_dev = DepsDev()
        self.os_dev = OSDev()
        
        
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
                                
                            os_dev_vulns = []
                            shodan_results = []
                            sploitus_results = []
                            deps_result = []
                            
                            for el in dependency_set:
                                product = el[0]
                                version = el[1]
                                
                                deps_response = self.deps_dev.depsdev_engine(product=product, version=version)
                                
                                if 'advisoryKeys' in deps_response and len(deps_response['advisoryKeys']) > 0:
                                    deps_result = deps_response['advisoryKeys']
                                
                                os_dev_engine_response = self.os_dev.osdev_engine(product=product, version=version)
                                
                                if len(os_dev_engine_response) > 0:
                                    for vuln in os_dev_engine_response['vulns']:
                                        os_dev_vulns.append({'id':vuln['id'], 'refs':vuln['references'], "score": vuln['severity'][0]['score']})
                                                                
                                s_r = self.shodan.shodan_engine(product=product,version=version)
    
                                if s_r is not None:
                                    shodan_results.append(s_r)
                                    for result in s_r: # result is in the format product:version:cve of vulnerables found
                                        cve = result.split(":")[-1] # get cve only
                                        sploitus , ll = self.sploitus.search_sploitus_by_cve(cve=cve)
                                        if ll > 0:
                                            sploitus_results.append(sploitus)
                                        
                            # export in csv
                            csv_output = {
                                          "repository" : repo['full_name'], 
                                          "star_range": star_range,
                                          "latest_push": repo['updated_at'],
                                          "files": files_found, 
                                          "total_dependencies": dependency_set,
                                          "number of vulnerabilities": (a if (a := max([deps_result, os_dev_vulns, shodan_results], key=len)) else 0),
                                          "deps_result": deps_result,
                                          "os_dev_vulns": os_dev_vulns,
                                          "shodan_result": shodan_results,
                                          "sploitus_result": sploitus_results,
                            }
                            
                            
                            print(csv_output)