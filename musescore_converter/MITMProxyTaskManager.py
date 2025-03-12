import asyncio
from pathlib import Path
import locale


class MITMProxyTaskManager:
    ENCODING = locale.getpreferredencoding()
    ACTIVATE_PROXY_SCRIPT_PATH = (
        Path(__file__).parent.parent / "ps_scripts" / "activate_windows_proxy.ps1"
    )
    DEACTIVATE_PROXY_SCRIPT_PATH = (
        Path(__file__).parent.parent / "ps_scripts" / "deactivate_windows_proxy.ps1"
    )

    def __init__(self, is_verbose=True):
        self.is_verbose = is_verbose

    async def print_mitmproxy_first_log(self, stream, prefix):
        async for line in stream:
            print(
                f"MITMProxy: {prefix}: {line.decode(self.ENCODING, errors='replace').strip()}"
            )
            return

    async def run_powershell_script(self, script_path: Path):
        """Run a PowerShell script asynchronously and capture output."""
        process = await asyncio.create_subprocess_exec(
            "powershell.exe",
            "-File",
            script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await process.wait()
        if self.is_verbose:
            print(f"{script_path.stem} exited with code {process.returncode}")

    async def run_mitmproxy(self):
        process = await asyncio.create_subprocess_exec(
            "mitmdump",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return process

    async def manage_proxy(self):
        try:
            if self.is_verbose:
                print("Activating Windows proxy...")
            await self.run_powershell_script(self.ACTIVATE_PROXY_SCRIPT_PATH)
            if self.is_verbose:
                print("Running mitmproxy...")
            mitmproxy_proc = await self.run_mitmproxy()
            if self.is_verbose:
                await self.print_mitmproxy_first_log(mitmproxy_proc.stdout, "STDOUT")
            await mitmproxy_proc.wait()

        except asyncio.CancelledError:
            raise
        finally:
            if self.is_verbose:
                print("Terminate mitmproxy process")
            mitmproxy_proc.terminate()
            if self.is_verbose:
                print("Deactivating Windows proxy")
            await self.run_powershell_script(self.DEACTIVATE_PROXY_SCRIPT_PATH)

    async def main(self):
        """Main function that runs tasks and handles graceful exit."""
        proxy_task = asyncio.create_task(self.manage_proxy())
        tasks = [proxy_task]
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    try:
        task_manager = MITMProxyTaskManager()
        asyncio.run(task_manager.main())
    except KeyboardInterrupt:
        pass  # Prevent traceback if Ctrl+C is pressed at the wrong moment
