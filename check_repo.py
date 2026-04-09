import urllib.request
url = "https://raw.githubusercontent.com/jxxghp/MoviePilot/main/app/api/endpoints/plugin.py"
try:
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')
    with open('/workspace/plugin_api.py', 'w') as f:
        f.write(content)
    print("Success")
except Exception as e:
    print(f"Failed: {e}")
