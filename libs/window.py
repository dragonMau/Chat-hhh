from os import path, system
from socket import socket
from time import time_ns
from tkinter import END, Button, Entry, Frame, Text, Tk

from lib import Storage
import asyncio


class Gui():
    root: Tk
    text: Text
    frame: Frame
    field: Entry
    button_send: Button
    storage: Storage
    sio: None

    def write(self, chars):
        self.text.configure(state="normal")
        self.text.insert(END, chars)
        self.text.configure(state="disabled")
        self.text.see(END)

    def parseCommand(self, *e):
        data, *args = self.field.get().split()
        self.field.delete(0, END)
        if data == "help":
            self.write("""
help list:
    list - list all active members
    stop - stop the server
    join - start new client
    send - send message""")
        elif data == "stop":
            exit()
        elif data == "list":
            self.write(f"\n{len(self.storage.users)} members active:")
            for usr in self.storage.users:
                self.write(f"\n   {usr.name.to_str()} - {usr.sid}")
        elif data == "join":
            system("explorer \"http://localhost:8080\"")
            
    def __init__(self, storage) -> None:
        self.storage = storage
        self.root = Tk()
        self.text = Text(self.root, state = "disabled", width=0, height=0)
        self.frame = Frame(self.root, height=30, width=0)
        self.field = Entry(self.frame, width=0)
        self.button_send = Button(self.frame, text="Submit", command=self.parseCommand)
        
        self.field.bind("<Return>", self.parseCommand)
        self.text.pack(anchor="nw", fill="both", expand="true")
        self.frame.pack(anchor="sw", fill="x")
        self.button_send.pack(side="right")
        self.field.pack(fill="x", expand="true", side="right")
        self.root.geometry("500x300")
        self.root.title("http://localhost:8080")
        self.root.bind("<Destroy>", lambda _: exit())
        self.field.focus()
