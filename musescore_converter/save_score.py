import requests


def get_score_id(score_url: str):
    first_part_url = "https://musescore.com/static/musescore/scoredata/g/"
    return score_url.split(first_part_url)[1].split("/")[0]


def get_cookies(ms_url: str):
    headers = {
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
    try:
        response = requests.get(ms_url, headers=headers)
    except Exception as e:
        print(f"An error occured: {e}")
        return
    cookies = response.cookies
    cookies_dict = requests.utils.dict_from_cookiejar(cookies)
    # print(cookies_dict)
    return cookies_dict


def get_mp3_link(score_url: str, cookies: dict):

    score_id = score_url.split("/")[-1]
    # Define the URL
    # url = "https://musescore.com/api/jmuse?id=3854486&index=0&type=mp3"
    mp3_api_url = f"https://musescore.com/api/jmuse?id={score_id}&index=0&type=mp3"

    # Define the headers
    headers = {
        "Host": "musescore.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Accept": "*/*",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": score_url,
        "Authorization": "83bc",
        "X-MU-FRONTEND-VER": "mu-web_app_0.48.56",
        "X-Mu-Unified-Id": cookies["_mu_unified_id"],
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
        "TE": "trailers",
    }

    # Send the request
    response = requests.get(mp3_api_url, headers=headers, cookies=cookies)

    # Print the response status code and content
    print("Status Code:", response.status_code)
    # response_dict = json.loads(response.json())
    # mp3_url = response_dict["info"]["url"]
    # print(mp3_url)


def save_score(score_url: str):
    score_id = get_score_id(score_url)
    url = f"https://musescore.com/static/musescore/scoredata/g/{score_id}/score_0.png"
    filename = f"./scores/{score_id}.png"
    headers = {
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
    print(url)
    # IMPORTANT SETTINGS TO NOT HAVE A BLOCKING LOOP WITH MITMPROXY
    proxies = {
        "http": None,
        "https": None,
    }
    try:
        response = requests.get(
            url, headers=headers, proxies=proxies
        )  # , verify=False)
    except Exception as e:
        print(f"An error occured: {e}")
        return
    print(response)
    response.raise_for_status()

    with open(filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"Downloaded {filename} successfully!")


if __name__ == "__main__":
    # score_url = "https://musescore.com/user/48323/scores/3854486"
    score_url = "https://musescore.com/user/8835606/scores/20279584"
    cookies = get_cookies(score_url)
    get_mp3_link(score_url=score_url, cookies=cookies)
