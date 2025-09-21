import requests as r
import sys
import re

class OSDev:
    def __init__(self):
        self.__url = "https://api.osv.dev/v1/query"
        self.__product_regex = r"^(?:@[a-z0-9][a-z0-9-_.]*\/)?[a-z0-9][a-z0-9-_.]*$"
        self.__product_error = "Regex does not match the format of npm package"

    def osdev_engine(self, product: str, version:str):

        if re.match(self.__product_regex, product) is None:
            raise ValueError(self.__product_error)
        
        payload = {"version": version,"package": {"name": product, "ecosystem": "npm"}}

        return (r.post(self.__url, json=payload)).json()
        

# Tests from command line, not the prupose of this script
# Usage: python3 osv_dev.py '@art-ws/common' 2.0.22
if __name__ == "__main__":
    
    if len(sys.argv)<1 or sys.argv[1] is None or sys.argv[1] == "":
        exit("Not a valid product input")
        
    if len(sys.argv)<2 or sys.argv[2] is None or sys.argv[2] == "":
        exit("Not a valid version")

    s = OSDev()
    
    collected = s.osdev_engine(product:=sys.argv[1], version:=sys.argv[2])
    print("Found -> " + str((collected)))