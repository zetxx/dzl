import subprocess, os
import json
from appdirs import AppDirs
import customtkinter
import shutil
import requests
import base64
import shlex

my_env = os.environ.copy()

dirs = AppDirs("dzl", "zetxx", "0.0.1", False)
dayzId = 221100
steamExec = shutil.which("steam")
dayzEnv = my_env = os.environ.copy()
userDir = os.path.expanduser("~")

def init():
    if not os.path.exists(dirs.user_data_dir):
        os.makedirs(dirs.user_data_dir)
        config = open(os.path.join(dirs.user_data_dir, 'config.json'),'w')
        config.write(json.dumps({"steamHome": False}))
        config.close()
        server = open(os.path.join(dirs.user_data_dir, 'servers.json'),'w')
        server.write("[]")
        server.close()

def setConfig(path):
    config = open(os.path.join(dirs.user_data_dir, 'config.json'),'w')
    config.write(json.dumps({"steamHome": path}))
    config.close()

def writeFileVar(dict):
    config = open(os.path.join(userDir, '.mangoHud.query.server'),'w')
    ws = ""
    for x in dict:
        ws += f"export {x}=\"{dict[x]}\"\n"

    config.write(ws)
    config.close()

def getConfig():
    s = open(os.path.join(dirs.user_data_dir, 'config.json'),'r')
    sr = json.loads(s.read())
    s.close()
    steamHome = sr["steamHome"]
    return {
        "steamHome": steamHome,
        "gameDir": f"{steamHome}/common/DayZ",
        "workshopDir": f"{steamHome}/workshop/content/{dayzId}"
    }

def serverAppend(single):
    s = servers()
    s.append(single)
    server = open(os.path.join(dirs.user_data_dir, 'servers.json'),'w')
    server.write(json.dumps(s))
    server.close()

def servers():
    s = open(os.path.join(dirs.user_data_dir, 'servers.json'),'r')
    sr = s.read()
    s.close()
    return json.loads(sr)

def runza(host, port, qport, mods):
    arg = f"{steamExec} -applaunch {dayzId} -connect {host}:{port}{mods}"
    dayzEnv["STEAM_ROOT"] = getConfig()["steamHome"]
    dayzEnv["DAYZ_QUERY_HOST"] = host
    dayzEnv["DAYZ_QUERY_PORT"] = str(qport)
    # print(arg, dayzEnv)
    writeFileVar({"DAYZ_QUERY_HOST": host, "DAYZ_QUERY_PORT": str(qport)})
    subprocess.Popen(shlex.split(arg), env=dayzEnv)

def runz(host, port, qport, mods=False):
    m = ""
    if mods:
        m = m + f" -mod={mods}"
    return lambda: runza(host, port, qport, mods=m)

def browserButton():
    filename = customtkinter.filedialog.askdirectory()
    setConfig(filename)

def redrawServerList(root):
    for child in root.winfo_children():
        child.destroy()
    servers()
    s = servers()
    for idx, child in enumerate(s):
        server = queryServer(host=child["host"], port=child["port"]["query"])
        customtkinter.CTkLabel(master=root, text=child["name"]).grid(row=idx, column=0, padx=10)
        customtkinter.CTkButton(master=root, text="Run", command=runz(child["host"], child["port"]["game"], child["port"]["query"], mods=server["-mod"])).grid(row=idx, column=1)

def appendServer(root):
    fields = [["name"], ["host"], ["port", "game"], ["port", "query"]]
    valid = True
    server = {}
    for child in root.winfo_children():
        if valid and hasattr(child, "get") and len(fields) > 0:
            val = child.get()
            if len(val) < 1:
                valid = False
            f = fields[0]
            fields.pop(0)
            if len(f) > 1:
                if not server.__contains__(f[0]):
                    server[f[0]] = {}
                server[f[0]][f[1]] = val
            else:
                server[f[0]] = val
    if valid:
        serverAppend(server)

def queryServer(host, port):
    response = requests.get(f"https://dayzsalauncher.com/api/v1/query/{host}/{port}")
    result = json.loads(response.text)["result"]
    result["-mod"] = False
    if len(result["mods"]) > 0:
        mods = ""
        for record in result["mods"]:
            mod = mod2base64(record["steamWorkshopId"])
            mods += f"@{mod};"
        result["-mod"] = mods[0:len(mods)-1].replace("/", "-")

    return result

def dec2base64(num):
    charDict = []
    while num > 0:
        byte = num & 0xff
        num >>= 8
        charDict.append(byte)

    char_bytes = bytes(charDict)
    b64_bytes = base64.b64encode(char_bytes)
    return b64_bytes.decode("utf-8")

def mod2base64(num):
    b64 = dec2base64(num)
    ttl = tl = len(b64)
    stop = tl
    while tl > -1 and stop == ttl:
        if b64[tl-1:tl] != "=":
            stop = tl
        tl = tl -1
    return b64[0:stop]