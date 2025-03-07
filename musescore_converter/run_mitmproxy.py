import asyncio
import locale

ENCODING = locale.getpreferredencoding()


async def read_output(process):
    while True:
        stdout_line = await process.stdout.readline()
        if stdout_line:
            print(f"stdout: {stdout_line.decode(ENCODING, errors='replace').strip()}")
        else:
            break
        stderr_line = await process.stderr.readline()
        if stderr_line:
            print(f"stderr: {stderr_line.decode().strip()}")
        else:
            break


async def is_port_listening(port, timeout=10):
    for _ in range(timeout):
        process = await asyncio.create_subprocess_exec(
            "netstat",
            "-ano",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, _ = await process.communicate()

        if stdout:
            lines = stdout.decode(ENCODING, errors="replace").splitlines()
            for line in lines:
                if f":{port}" in line and "LISTENING" in line:
                    return True
        await asyncio.sleep(1)
    return False


async def run_mitmdump(port=8080, timeout=10):
    try:
        process = await asyncio.create_subprocess_exec(
            "mitmdump",
            "-p",
            f"{port}",
            "-s",
            "proxy.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as e:
        print(f"Could not create mitmproxy subprocess: {e}.")
    await check_mitmdump(process, timeout=timeout)


async def check_mitmdump(process, port=8080, timeout=10):
    try:
        is_listening = await is_port_listening(port, timeout=timeout)
        if is_listening:
            print("Process listening on 8080")
            await read_output(process)
    except RuntimeError:
        print(f"No listening on port {port} after. MITMProxy is not running.")
        print("Event loop is closed.")


if __name__ == "__main__":
    port = 8080
    asyncio.run(run_mitmdump(port=8080, timeout=10))
