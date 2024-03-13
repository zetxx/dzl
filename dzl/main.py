from os import path
import sys

if __package__:
    parent_dir = path.dirname(__file__)
    root_dir = path.dirname(parent_dir)
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)

import customtkinter
from fns import init, redrawServerList, appendServer, redrawServerList, getConfig, steamRootAdd

def run():
    init()

    customtkinter.set_appearance_mode("system")
    root = customtkinter.CTk()
    root.geometry("1000x1000")
    root.minsize(500, 500)
    root.title("DZL")

    root.grid_rowconfigure((1), weight=1)
    root.grid_columnconfigure((0), weight=1)


    frameServerList = customtkinter.CTkFrame(master=root)
    frameServerList.grid(row=0, column=0, padx=5, pady=(5, 0), sticky='NSEW')
    label2 = customtkinter.CTkLabel(master=frameServerList, text="Server List", font=("Arial", 25))
    label2.pack(padx=5, pady=5)
    frameMainServerList = customtkinter.CTkFrame(master=root)
    frameMainServerList.grid(row=1, column=0, padx=5, pady=(5, 0), sticky='NSEW')
    redrawServerList(frameMainServerList)



    def addBtnEvenet():
        appendServer(frameServerAdd)
        redrawServerList(frameMainServerList)

    frameServerAdd = customtkinter.CTkFrame(master=root, border_width=2)
    frameServerAdd.grid_rowconfigure((0), weight=1)
    frameServerAdd.grid_columnconfigure((8), weight=1)
    frameServerAdd.grid(row=2, column=0, padx=5, pady=(5, 0), sticky='NSEW')

    customtkinter.CTkLabel(master=frameServerAdd, text="Config", font=("Arial", 25)).grid(row=0, column=0, columnspan=14, padx=2, pady=20, sticky='NSEW')

    customtkinter.CTkLabel(master=frameServerAdd, text="Name", font=("Arial", 25)).grid(row=1, column=0, padx=2)
    asname = customtkinter.CTkEntry(master=frameServerAdd, fg_color="gray")
    asname.grid(row=1, column=1, padx=2)

    customtkinter.CTkLabel(master=frameServerAdd, text="In game name", font=("Arial", 25)).grid(row=1, column=2, padx=2)
    ign = customtkinter.CTkEntry(master=frameServerAdd, fg_color="gray")
    ign.grid(row=1, column=3, padx=2)

    customtkinter.CTkLabel(master=frameServerAdd, text="host", font=("Arial", 25)).grid(row=1, column=4, padx=2)
    ashost = customtkinter.CTkEntry(master=frameServerAdd, fg_color="gray")
    ashost.grid(row=1, column=5, padx=2)

    customtkinter.CTkLabel(master=frameServerAdd, text="game port", font=("Arial", 25)).grid(row=1, column=6, padx=2)
    asgp = customtkinter.CTkEntry(master=frameServerAdd, fg_color="gray", height=10)
    asgp.grid(row=1, column=7, padx=2, pady=3)

    customtkinter.CTkLabel(master=frameServerAdd, text="query port", font=("Arial", 25)).grid(row=1, column=8, padx=2)
    asqp = customtkinter.CTkEntry(master=frameServerAdd, fg_color="gray", height=10)
    asqp.grid(row=1, column=9, padx=2)

    customtkinter.CTkButton(master=frameServerAdd, text="Add", command=addBtnEvenet, font=("Arial", 25)).grid(row=1, column=10, padx=20)
    customtkinter.CTkLabel(master=frameServerAdd, text="", font=("Arial", 25)).grid(row=1, column=11, padx=20)
    steamRoot = customtkinter.CTkLabel(master=frameServerAdd, text=getConfig()["steamHome"], font=("Arial", 25))
    steamRoot.grid(row=1, column=12, padx=2)
    customtkinter.CTkButton(master=frameServerAdd, text="Set Steam Root", command=lambda: steamRootAdd(el=steamRoot), font=("Arial", 25)).grid(row=1, column=13, padx=20)

    root.mainloop()

if __name__ == "__main__":
    run()