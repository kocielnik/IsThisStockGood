#!/usr/bin/env python3

from requests import get

url = "https://api.github.com/repos/mrhappyasthma/IsThisStockGood/issues"
headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}
res = get(url, headers=headers)
print(res.text)
