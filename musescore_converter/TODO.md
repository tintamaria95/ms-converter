- create mitmproxy task manager to start and stop mitmproxy + windows proxy - OK
- create mitmproxy script for sheet download - OK (proxy.py)
- create logic to get aws url to get complete sheet - OK (save_score.py)

- merge proxy.py and save_score to complete sheet download and pdf creation
- write again mitmproxy installation in .ps1 file (ps_scripts dir)
- change frontend to show available music sheets to download + "beautify"
- add arg in task_manager __init__ function: websocket, add method to send websocket when LISTENING is read from MITMProxy -> send it to frontend to change mitmproxy connection status