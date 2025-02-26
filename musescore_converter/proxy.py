from mitmproxy import http


from save_score import save_score


class MyAddon:
    def request(self, flow: http.HTTPFlow):
        musescore_score_url = "https://musescore.com/static/musescore/scoredata/g/"
        if flow.request.pretty_url.startswith(musescore_score_url):
            print(f"Intercepted request to: {flow.request.url}")
            save_score(flow.request.url)


addons = [MyAddon()]
