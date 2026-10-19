import json, os, re, sys, urllib.request

URL = "https://na.alienwarearena.com/"
STATE = "seen.json"
PATTERN = re.compile(r'/ucf/show/(\d+)/boards/[^"\'\s<>?#]*?/Giveaway/[^"\'\s<>?#]+')

def fetch():
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def notify(title, link):
    topic = os.environ["NTFY_TOPIC"]
    req = urllib.request.Request(
        "https://ntfy.sh/" + topic,
        data=("Nuevo giveaway: " + title).encode("utf-8"),
        headers={"Title": "Alienware Arena", "Priority": "urgent", "Click": link})
    urllib.request.urlopen(req, timeout=30)

html = fetch()
found = {}
for m in PATTERN.finditer(html):
    found[m.group(1)] = m.group(0)

if not found:
    print("No se encontraron giveaways: la web ha cambiado o bloquea la peticion")
    sys.exit(1)

first = not os.path.exists(STATE)
seen = set() if first else set(json.load(open(STATE)))

if not first:
    for gid, path in found.items():
        if gid not in seen:
            title = path.rsplit("/", 1)[-1].replace("-", " ")
            notify(title, "https://na.alienwarearena.com" + path)

json.dump(sorted(seen | set(found)), open(STATE, "w"))
