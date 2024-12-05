import requests

def test_get_issues():
    owner = "mrhappyasthma"
    repo = "IsThisStockGood"
    url = f"https://api.github.com/search/issues?q=repo:{owner}/{repo}+is:issue&per_page=100'"

    res = requests.get(
        url,
        headers={
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    assert len(res.json()['items']) > 0
