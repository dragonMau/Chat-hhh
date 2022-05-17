import asyncio
from os import system
import os
from sys import argv
from threading import Thread
from tkinter import END, Button, Entry, Frame, Text, Tk

import socketio
from aiohttp import web

class User:
    name: str
    def __init__(self, sid, name = ""):
        if name == "":
            self.name = str(sid)
        else:
            self.name = name
    

class storage:
    users = {}  #  sid : userdata
    messages = {} #  id : data

root = Tk()
text = Text(root, state = "disabled", width=0, height=0)
def write(chars):
    text.configure(state="normal")
    text.insert(END, chars)
    text.configure(state="disabled")
    text.see(END)

frame = Frame(root, height=30, width=0)
field = Entry(frame, width=0)
def parseCommand(*e):
    data = field.get()
    field.delete(0, END)
    if data == "help":
        write("""
help list:
    list - list all active members
    stop - stop the server
    join - start new client""")
    elif data == "stop":
        exit()
    elif data == "list":
        write(f"\n{len(storage.users)} members active:")
        for sid, member in storage.users.items():
            write(f"\n   {member.name} - {sid}")
    elif data == "join":
        system("explorer \"http://localhost:8080\"")
        

field.bind("<Return>", parseCommand)
button_send = Button(frame, text="Submit", command=parseCommand)


sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

@sio.on('register')
async def register(sid, data):
    result = "error"
    usr = data["usr"]
    h_usr = usr.encode("utf-8").hex()
    pwd = data["pwd"]
    if not os.path.exists(f"./users/{h_usr}"):
        with open(f"./users/{h_usr}", "w") as f:
            f.write(f"{pwd}\n")
            f.write(f"{usr}\n")
        result = "ok"
    else:
        result = "overlap"
    await sio.emit("register answer", result)

@sio.on('login')
async def login(sid, data):
    if sid in storage.users.keys():
        if storage.users[sid].name != sid:
            return
    result = "error"
    usr = data["usr"]
    h_usr = usr.encode("utf-8").hex()
    pwd = data["pwd"]
    data = ""
    if os.path.exists(f"./users/{h_usr}"):
        with open(f"./users/{h_usr}", "r") as f:
            user_data = f.read().split("\n")
            if pwd == user_data[0]:
                storage.users[sid] = User(sid, usr)
                write("\n"+ storage.users[sid].name +" joined")
                result = "ok"
                with open("./chat.html", "r") as f:
                    data = f.read()
            else:
                result = "wrong pwd"
    else:
        result = "wrong usr"
    await sio.emit("login answer", {"code":result, "new":data})

@sio.on('connect')
async def connect(sid, environ):
    storage.users[sid] = User(sid)

@sio.on('message')
async def print_message(sid, message):
    write("\n" + storage.users[sid].name + ": " + str(message))

@sio.on('disconnect')
async def disconnect(sid):
    write("\n"+ storage.users[sid].name +" left")
    del storage.users[sid]

app.router.add_get('/', index)

def server(*e):
    global sio, app
    web.run_app(app)

lp2 = Thread(target=server)
lp2.daemon = True

def init_gui(*e):
    text.pack(anchor="nw", fill="both", expand="true")
    frame.pack(anchor="sw", fill="x")
    button_send.pack(side="right")
    field.pack(fill="x", expand="true", side="right")
    root.geometry("500x300")
    root.title("http://localhost:8080")
    root.bind("<Destroy>", exit)
    field.focus()
    root.mainloop()
    
lp1 = Thread(target=init_gui)
lp1.daemon = True


if __name__ == '__main__':
    lp2.start()
    lp1.run()
