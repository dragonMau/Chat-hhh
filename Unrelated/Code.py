
from discord_webhook import DiscordWebhook
import requests
from time import time
import discord

start_time = time()
def log(*text, sep=" ", end="\n"):
    sec = (time()-start_time)%3600
    print(
    f"({int(sec//60):02d}:{int(sec%60):02d}) "\
    +sep.join(text)+end, sep="", end="")

class Sender:
    def send_art(self, art="https://picsum.photos/200/300", file=False):
        log("creating webhook...")
        webhook = DiscordWebhook(
        url=self.urls,
        username=self.data["username"],
        avatar_url=self.data["avatar_url"])
        
        log("webhook created, creating art...")
        if not file:
            log("    downloading from url...")
            art = requests.get(art).content
        if file:
            log("    opening from file...")
            art = art.fp
            
        log("art created, adding file...")
            
        webhook.add_file(file = art,
        filename=f"{asctime()}.png")
        
        log("file added, executing webhook...")
        response = webhook.execute()
        log(f"webhook executed, {response}")

    def __init__(self):
        self.urls = [
            "https://discord.com/api/webhooks/1029616014670966794/5tyXvWKZS-BD94TGiy1eiAEUvnfuoosHdevtBZ4d9WEMRWlnMuqYRY-f7kTy8d_QSC2F"
        ]
        self.data = {
            "username" : "pikachu",
            "avatar_url" : "https://cdn.discordapp.com/avatars/623939240354512937/6f1a8414a4f5efb4a99d8dbf8d6a3986.png?size=1024",
        }
        self.bank = 1027690326909005996
        self.token = "token"
           
 
 
sender = Sender()     

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
        log("started, getting bank channel...")
        ch = client.get_channel(1027690326909005996)
        log("got bank channel.")
        times = int(input("how many arts to send?: "))
        log(f"sending {times} arts...")
        for i in range(times):
            log("making history")
            history = ch.history(oldest_first=True)
            log("made history, asking first message...")
            first = await history.next()
            log("got first message, downloading art...")
            first_art = await first.attachments[-1].to_file()
            
            log("loaded art, sending art...")
            sender.send_art(first_art, file=True)
            
            log("art sent, deleting from bank channel...")
            await first.delete()
            log(f"deleted. done {i} arts")
        
        log("finished!", "\n"*2, "-"*15)
        exit()

if __name__=="__main__":
    log("starting...")
    client.run(sender.token)
