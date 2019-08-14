import requests
import tarfile
import json
from urllib.request import urlretrieve
from pprint import pprint as pp

def update(version):
    url = f"https://ddragon.leagueoflegends.com/cdn/dragontail-{version}.tgz"
    print("getting requests...")
    req = requests.get(url)
    if req.status_code != 200:
        print("unavailable url!")
        return False
    with open(f"dragontail-{version}.tgz", "wb") as code:
        print("downloading...")
        code.write(req.content)
    urlretrieve(url, f"dragontail-{version}.tgz")
    with tarfile.open(f"dragontail-{version}.tgz") as dragontail:
        print("unpacking...")
        dragontail.extractall(f"dragontail-{version}")
        print("successfully downloaded!")

def check_version(config):
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    req = requests.get(url)
    if req.status_code != 200:
        print("unavailable url!")
        return False
    versions = req.json()
    version = versions[0]
    if version != config['version']:
        update(version)
        config['version'] = version
        with open("config.json", "w") as f:
            json.dump(config, f)
    
