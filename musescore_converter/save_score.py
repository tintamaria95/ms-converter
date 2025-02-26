import requests




def get_score_id(score_url: str):
    first_part_url = "https://musescore.com/static/musescore/scoredata/g/"
    return score_url.split(first_part_url)[1].split("/")[0]


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
    save_score(
        "https://musescore.com/static/musescore/scoredata/g/8fbceb3e46eb0cf31b7f20922556d3f5ebcfa43d/space.jsonp?revisio"
    )
