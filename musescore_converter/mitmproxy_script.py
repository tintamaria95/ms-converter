import os
import json
import requests
from mitmproxy import http
from pathlib import Path
from urllib.parse import urlparse
from config import config
from bs4 import BeautifulSoup

from Score import ScorePage


def is_content(flow: http.HTTPFlow, content_type: str):
    content_type = flow.response.headers.get("Content-Type", "")
    if content_type in content_type:
        return True
    return False


def is_html_content(flow: http.HTTPFlow):
    return is_content(flow, "text/html")


def is_svg_content(flow: http.HTTPFlow):
    return is_content(flow, "image/svg+xml")


def is_png_content(flow: http.HTTPFlow):
    return is_content(flow, "image/png")


def is_score_from_s3(flow: http.HTTPFlow):
    if flow.request.url.startswith(
        "https://s3.ultimate-guitar.com/musescore.scoredata/g/"
    ):
        if is_svg_content(flow) or is_png_content(flow):
            return True
    return False


def get_score_0_url(mp3_url: str):
    start = "https://s3.ultimate-guitar.com/musescore.scoredata/g/"
    score_id = mp3_url.split(start)[1].split("/")[0]
    return (
        score_id,
        f"https://musescore.com/static/musescore/scoredata/g/{score_id}/score_0",
    )


def get_score_0_headers():
    return {
        "Host": "musescore.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
        "TE": "trailers",
    }


def save_score_0(score_0_id: str, score_0_url: str, suffix: str):
    proxies = {
        "http": None,
        "https": None,
    }
    try:
        headers = get_score_0_headers()
        response = requests.get(score_0_url, headers=headers, proxies=proxies)
    except Exception as e:
        print(f"GET Request failed for url: {score_0_url}. ERROR:{e}")
        return
    response.raise_for_status()
    try:
        print(f"score id: {score_0_id}")
        score_dir = Path(f"{config['scores_directory']}/{score_0_id}")
        if not Path.exists(score_dir):
            score_dir.mkdir(exist_ok=True)
        with open(score_dir / f"0_{score_0_id}.{suffix}", "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print("Downloaded score_0 successfully!")
    except Exception as e:
        print(e)


def save_score_from_s3(flow: http.HTTPFlow, score_id: str, page_num: str, suffix: str):
    with open(
        f"{config['scores_directory']}/{score_id}/{page_num}_{score_id}.{suffix}", "wb"
    ) as f:
        f.write(flow.response.content)


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


def get_score_infos_from_html(response_text: str):
    with open("tmp.html", "w", encoding="utf-8") as f:
        f.write(response_text)
    soup = BeautifulSoup(response_text, "html.parser")

    meta_tags = soup.find_all("meta", attrs={"property": True})
    properties = {meta.get("property"): meta.get("content") for meta in meta_tags}
    searched_properties = ["og:title", "musescore:author", "musescore:composer"]
    score_infos = {
        p.split(":")[1]: properties[p]
        for p in searched_properties
        if p in properties.keys()
    }

    script_tags = soup.find_all("script", attrs={"type": True})
    for script in script_tags:
        if "application/ld+json" in script.get("type"):
            script_dict = json.loads(script.string)
            if "thumbnailUrl" in script_dict:
                score_infos["url"] = script_dict["thumbnailUrl"]
                break
    print(f"scraped score infos: {score_infos}")
    return score_infos


def intercept_score_0_from_html(flow: http.HTTPFlow):
    musescore_user_url = "https://musescore.com/user/"
    musescore_official_scores_url = "https://musescore.com/official_scores/"
    if flow.request.url.startswith(musescore_user_url) or flow.request.url.startswith(
        musescore_official_scores_url
    ):
        if is_html_content(flow):
            score_infos = get_score_infos_from_html(flow.response.text)
            print(score_infos)
            score_0_url = score_infos["url"]
            score_0_id = score_0_url.split(
                "https://musescore.com/static/musescore/scoredata/g/"
            )[1].split("/")[0]
            if ".png" in score_0_url:
                score_0_suffix = "png"
            elif ".svg" in score_0_url:
                score_0_suffix = "svg"
            else:
                raise ValueError(
                    "score_0 suffix is neither png or svg."
                    f"URL Found: {score_infos['url']}"
                )
            save_score_0(score_0_id, score_0_url, score_0_suffix)
            score_0 = ScorePage(
                id=score_0_id,
                page="0",
                title=score_infos["title"],
                composer=score_infos["composer"],
                author=score_infos["author"],
            )
            post_request_score(score_0)


def intercept_score_from_s3(flow: http.HTTPFlow):
    if is_score_from_s3(flow):
        parsed_url = urlparse(flow.request.url).path
        start = "/musescore.scoredata/g/"
        score_id = parsed_url.split(start)[1].split("/")[0]
        page_num = os.path.basename(parsed_url).split(".")[0].split("score_")[1]
        suffix = parsed_url.split(".")[-1]
        save_score_from_s3(flow, score_id, page_num, suffix)
        score_page = ScorePage(id=score_id, page=page_num)
        post_request_score(score_page)


class MyAddon:

    def response(self, flow: http.HTTPFlow):
        intercept_score_0_from_html(flow)
        intercept_score_from_s3(flow)


print("Called mitmproxy script")
addons = [MyAddon()]
post_request_status(True)
