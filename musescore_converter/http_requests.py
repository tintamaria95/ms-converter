import requests
from Score import ScorePage
from config import config


def post_request_score(score_page: ScorePage):
    proxies = {
        "http": None,
        "https": None,
    }
    try:
        response = requests.post(
            f"http://{config['host']}:{config['port']}/api/score",
            json=score_page.to_json(),
            proxies=proxies,
        )
        print(response)
    except Exception as e:
        print(
            f"ERROR while trying to post request on http://{config['host']}:{config['port']}/api/score"
        )
        print(e)


def post_request_status(is_active: bool):
    proxies = {
        "http": None,
        "https": None,
    }
    try:
        response = requests.post(
            f"http://{config['host']}:{config['port']}/api/status",
            json={"is_active": is_active},
            proxies=proxies,
        )
        print(response)
    except Exception as e:
        print(
            f"ERROR while trying to post request on http://{config['host']}:{config['port']}/api/status"
        )
        print(e)
