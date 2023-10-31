import subprocess, os
import json
from appdirs import AppDirs
import customtkinter
import shutil
import requests
import base64
import shlex

my_env = os.environ.copy()

dirs = AppDirs("dzl", "zetxx", "0.0.2", False)
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

def setConfig(steamHome):
    config = open(os.path.join(dirs.user_data_dir, 'config.json'),'w')
    config.write(json.dumps({"steamHome": steamHome}))
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
        "gameDir": f"{steamHome}/steamapps/common/DayZ",
        "workshopDir": f"{steamHome}/steamapps/workshop/content/{dayzId}"
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

def runza(config, mods):
    arg = f'{steamExec} -applaunch {dayzId} -connect {config["host"]}:{config["port"]["game"]}'
    if "igName" in config:
        arg += f' -name {config["igName"]}'
    arg += mods
    dayzEnv["STEAM_ROOT"] = getConfig()["steamHome"]
    dayzEnv["DAYZ_QUERY_HOST"] = config["host"]
    dayzEnv["DAYZ_QUERY_PORT"] = str(config["port"]["game"])
    writeFileVar({"DAYZ_QUERY_HOST": config["host"], "DAYZ_QUERY_PORT": str(config["port"]["query"])})
    subprocess.Popen(shlex.split(arg), env=dayzEnv)

def runz(config, mods=False):
    m = ""
    if mods:
        m = m + f" -mod={mods}"
    # print(f'{config["port"]}/{mods}')
    return lambda: runza(config, mods=m)

def serverInfoRedraw(label, child):
    server = queryServer(host=child["host"], port=child["port"]["query"])
    label.configure(text=serverInfoText(child, server))
    label.update()

def reloadEv(label, child):
    return lambda: serverInfoRedraw(label, child)

def serverInfoText(child, server):
    if server == False:
        return f'{child["name"]}:(N/A)'
    p = "FP"
    if not server["firstPersonOnly"]:
        p = "FP/TP"

    return f'{child["name"]}:(T:{server["time"]};P:{server["players"]}/{server["maxPlayers"]};{p})'

def serverInfo(root, server, child, idx):
    infoLabel = customtkinter.CTkLabel(master=root, text=serverInfoText(child, server))
    infoLabel.grid(row=idx, column=0, padx=10)
    return infoLabel

def redrawServerList(root):
    for child in root.winfo_children():
        child.destroy()
    servers()
    s = servers()
    for idx, child in enumerate(s):
        server = queryServer(host=child["host"], port=child["port"]["query"])
        if server and "mods" in server and len(server["mods"]) > 0:
            linkMods(server)
        infoLabel = serverInfo(root, server, child, idx)
        customtkinter.CTkButton(master=root, text="Reload", command=reloadEv(infoLabel, child), fg_color="#ffd900", text_color="#474433").grid(row=idx, column=1)
        customtkinter.CTkLabel(master=root, text=' ').grid(row=idx, column=2)
        if server != False:
            customtkinter.CTkButton(master=root, text="Run", command=runz(child, mods=server["-mod"]), fg_color="#fc6f6f", text_color="#473333").grid(row=idx, column=3)
        customtkinter.CTkButton(master=root, text="Run", command=runz(child, mods=False), fg_color="#fc6f6f", text_color="#473333").grid(row=idx, column=3)

def linkMods(server):
    print('/////////////////////////////////////')
    print(f'Loading mods for mod: {server["name"]}')
    print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
    cnf = getConfig()
    for element in server["mods"]:
        dst = os.path.join(cnf["gameDir"], f'@{element["base64"]}')
        src = os.path.join(cnf["workshopDir"], str(element['steamWorkshopId']))
        if not os.path.exists(dst):
            if not os.path.exists(src):
                print(f'Missing mod: {element["name"]} [{element["steamWorkshopId"]}] ({server["name"]})')
            else:
                os.symlink(src, dst)

def appendServer(root):
    fields = [["name"], ['igName'], ["host"], ["port", "game"], ["port", "query"]]
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
    resp = json.loads(response.text)
    if "error" in resp:
        return False
    result = resp["result"]
    result["-mod"] = False
    if len(result["mods"]) > 0:
        mods = ""
        for idx, record in enumerate(result["mods"]):
            mod = mod2base64(record["steamWorkshopId"])
            mod = mod[0:len(mod)-1].replace("/", "-")
            result["mods"][idx]["base64"] = mod
            mods += f"@{mod};"
            # print(f"{record}>{mod}")
        result["-mod"] = mods

    return result

def dec2base64(num):
    oldNum = num
    charDict = []
    while num > 0:
        byte = num & 0xff
        num >>= 8
        charDict.append(byte)

    return base64.b64encode(bytes(charDict)).decode("utf-8")

def mod2base64(num):
    b64 = dec2base64(num)
    ttl = tl = len(b64)
    stop = tl
    while tl > -1 and stop == ttl:
        if b64[tl-1:tl] != "=":
            stop = tl
        tl = tl -1
    return b64[0:stop]

def steamRootAdd(el):
    filename = customtkinter.filedialog.askdirectory()
    setConfig(steamHome=filename)
    el.configure(text=filename)
    el.update()