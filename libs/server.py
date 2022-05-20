from os import path

import socketio
from aiohttp import web

from lib import Storage, User
from window import Gui


class Server:
    sio: socketio.AsyncServer
    app: web.Application
    gui: Gui
    storage: Storage
    
    async def index(self, request):
        with open('./public/index.html') as f:
            return web.Response(text=f.read(), content_type='text/html')
    
    def init_handler(self):
        @self.sio.on('connect')
        async def connect(sid, *_):
            self.storage.users[sid] = User(sid)
        
        @self.sio.on('register')
        async def register(sid, data, *_):
            result = "error"
            usr = data["usr"]
            h_usr = usr.encode("utf-8").hex()
            pwd = data["pwd"]
            if not path.exists(f"./local/users/{h_usr}"):
                with open(f"./local/users/{h_usr}", "w") as f:
                    f.write(f"{pwd}\n")
                    f.write(f"{usr}\n")
                result = "ok"
            else:
                result = "overlap"
            await self.sio.emit("register answer", result, to=sid)
            
        @self.sio.on('login')
        async def login(sid, data, *_):
            if sid in self.storage.users.keys():
                if self.storage.users[sid].name != sid:
                    return
            result = "error"
            usr = data["usr"]
            h_usr = usr.encode("utf-8").hex()
            pwd = data["pwd"]
            data = ""
            if usr in [u.name for u in self.storage.users.values()]:
                td = [k for k, v in self.storage.users.items() if v.name == usr][0]
                await self.sio.emit("stop", to=td)
                await self.sio.disconnect(td)
            if path.exists(f"./local/users/{h_usr}"):
                with open(f"./local/users/{h_usr}", "r") as f:
                    user_data = f.read().split("\n")
                    if pwd == user_data[0]:
                        self.storage.users[sid] = User(sid, usr)
                        self.gui.write("\n"+ self.storage.users[sid].name +" joined")
                        result = "ok"
                        with open("./public/chat.html", "r") as f:
                            data = f.read()
                    else:
                        result = "wrong pwd"
            else:
                result = "wrong usr"
            await self.sio.emit("login answer", {"code":result, "new":data}, to=sid)
            
        @self.sio.on('message')
        async def print_message(sid, message, *_):
            self.gui.write("\n" + self.storage.users[sid].name + ": " + str(message))
            
        @self.sio.on('disconnect')
        async def disconnect(sid, *_):
            self.gui.write("\n"+ self.storage.users[sid].name +" left")
            del self.storage.users[sid]
            
    def __init__(self, gui, storage) -> None:
        self.storage = storage
        self.gui = gui
        self.sio = socketio.AsyncServer()
        self.app = web.Application()
        self.sio.attach(self.app)
        
        self.init_handler()
        
        self.app.router.add_static('/static', './public')
        self.app.router.add_get('/', self.index)
