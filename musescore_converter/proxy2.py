from mitmproxy import http, ctx
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
import asyncio


class InterceptAddon:

    def request(self, flow: http.HTTPFlow):
        """This method is called for every HTTP request."""

        print(f"Intercepted request to: {flow.request.url}")

    def response(self, flow: http.HTTPFlow):
        """This method is called for every HTTP response."""

        print(f"Intercepted response from: {flow.request.url}")


async def start_proxy():
    opts = Options(
        listen_host="127.0.0.1",
        listen_port=8080,
        )
    proxy = DumpMaster(opts)
    proxy.addons.add(InterceptAddon())

    try:
        print("Starting mitmproxy...")
        await proxy.run()  # Run inside the event loop
    except KeyboardInterrupt:
        print("Stopping mitmproxy...")
        proxy.shutdown()


def main():
    asyncio.run(start_proxy())


if __name__ == "__main__":
    main()
