import asyncio
import subprocess
from pathlib import Path
import locale

from http_requests import post_request_status


class ProxyTaskManager:
    """
    This task manager is used to start/stop mitmproxy process and
    activate/deactivate Windows proxy which allows mitmproxy to listens on same port.

    Warning: This changes Windows proxy as it is set in config.py.
    Be sure to not use Windows proxy for another use-case.
    """

    ENCODING = locale.getpreferredencoding()
    # ACTIVATE_PROXY_SCRIPT_PATH = (
    #     Path(__file__).parent.parent / "ps_scripts" / "activate_windows_proxy.ps1"
    # )
    ACTIVATE_PROXY_SCRIPT_PATH = Path(
        r"C:\Users\tinta\Documents\CODE\Musescore Converter\ps_scripts\activate_windows_proxy.ps1"
    )
    # DEACTIVATE_PROXY_SCRIPT_PATH = (
    #     Path(__file__).parent.parent / "ps_scripts" / "deactivate_windows_proxy.ps1"
    # )
    DEACTIVATE_PROXY_SCRIPT_PATH = Path(
        r"C:\Users\tinta\Documents\CODE\Musescore Converter\ps_scripts\deactivate_windows_proxy.ps1"
    )

    def __init__(self, is_verbose=True):
        self.is_verbose = is_verbose
        self.mitmproxy_process = None

    async def get_is_proxy_listening(self, stream):
        async for line in stream:
            first_log = f"{line.decode(self.ENCODING, errors='replace').strip()}"
            return "proxy listening" in first_log

    async def run_powershell_script(self, script_path: Path):
        """Run a PowerShell script asynchronously and capture output."""
        process = subprocess.Popen(
            ["powershell.exe", "-File", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = await asyncio.to_thread(process.communicate)
        return stdout.strip(), stderr.strip()

    async def run_mitmproxy(self):
        """Run a PowerShell script asynchronously and capture output."""
        self.mitmproxy_process = subprocess.Popen(
            ["mitmdump", "-s", "mitmproxy_script.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    async def start_proxy(self):
        try:
            if self.is_verbose:
                print("Activating Windows proxy...")
            await self.run_powershell_script(self.ACTIVATE_PROXY_SCRIPT_PATH)
            if self.is_verbose:
                print("Running mitmproxy...")
            await self.run_mitmproxy()
        except asyncio.CancelledError:
            self.stop_proxy()
            raise

    async def stop_proxy(self):
        if self.mitmproxy_process:
            if self.is_verbose:
                print("Terminate mitmproxy process")
            self.mitmproxy_process.terminate()
        if self.is_verbose:
            print("Deactivating Windows proxy")
        await self.run_powershell_script(self.DEACTIVATE_PROXY_SCRIPT_PATH)
        # post_request_status(False)

    async def main(self):
        """Main function that runs tasks and handles graceful exit."""
        await self.start_proxy()

        await asyncio.sleep(5)
        await self.stop_proxy()
        while True:
            await asyncio.sleep(1000)


if __name__ == "__main__":
    try:
        task_manager = ProxyTaskManager()
        asyncio.run(task_manager.main())

    except KeyboardInterrupt:
        pass  # Prevent traceback if Ctrl+C is pressed at the wrong moment
