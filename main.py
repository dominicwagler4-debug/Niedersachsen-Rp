import discord
from discord import app_commands
import requests
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. Kleiner Webserver für Render (damit der Port-Scan nicht fehlschlägt) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")
    def log_message(self, format, *args):
        pass # Unterdrückt Spam in den Logs

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Webserver im Hintergrund starten
threading.Thread(target=run_web_server, daemon=True).start()

# --- 2. Bot-Setup initialisieren ---
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Deine Roblox Daten & Server ID
ROBLOX_API_KEY = "Z+aS/hlW8kmSJ6buCWtF9buf+xaQw22fGzWKPYavJ+ZBkHQwZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkluTnBaeTB5TURJeExUQTNMVEV6VkRFNE9qVXhPalE1V2lJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaGRXUWlPaUpTYjJKc2IzaEpiblJsY201aGJDSXNJbWx6Y3lJNklrTnNiM1ZrUVhWMGFHVnVkR2xqWVhScGIyNVRaWEoyYVdObElpd2lZbUZ6WlVGd2FVdGxlU0k2SWxvcllWTXZhR3hYT0d0dFUwbzJZblZEVjNSR09XSjFaaXQ0WVZGM01qSm1SM3BYUzFCWllYWktLMXBDYTBoUmR5SXNJbTkzYm1WeVNXUWlPaUkzTWpRNU16WTFNelExSWl3aVpYaHdJam94TnpnMk9ETXlOemswTENKcFlYUWlPakUzT0RZNE1qa3hPVFFzSW01aVppSTZNVGM0TmpneU9URTVOSDAuWEN3NmtvcWxrLVpZZ2g0YUQ1WEZZcmc0X2EtbzdxTWdqN005aWRqQ2xITlJHdTZrdllwM29DWXlfUWUxNkNBeGEzSm05SWtJREhTcDNHWnJ0YnRzaDRXeFZzSkZ4R0t6UnpPN1Y3WEpIdGxEbzV6NnRXdUptVFBZY3cxaU9EdElGMm8zLWJ2YURzVkNPLTZDZHY1T0FrOFloQno4MVVEaHo2MW1sZWU3Y1ZuSVA5eVFCczl2T3U5MFE5VXd2cVdlSk5DNGxxbENKemtkeWYwc3JIOWpFeXY2WmI4UDJLeENnRmxCbndlUm1yenpsTTBzS1Nkd28zSHlSQjI1NXB5ZFZVaFAzNHZCT2tiTGg1bXBncGdkWjhHUmk1ZmVhcTVKYzAzRUVVdjBIeEJNSVFya1FxTWVrVDg3RWVYNmFWWERlcXVZXzRwMW5JX1hpOGNCRms2X2Fn"
UNIVERSE_ID = "9772844823"
SECRET_KEY = "Gamemode"

GUILD_ID = discord.Object(id=153120464911649999) 

@client.event
async def on_ready():
    tree.copy_global_to(guild=GUILD_ID)
    await tree.sync(guild=GUILD_ID)
    print(f"Eingeloggt als {client.user} und Befehle für den Server synchronisiert!")

# --- 3. Der Ban-Befehl ---
@tree.command(name="ban", description="Banne einen Spieler im Spiel")
async def ban(interaction: discord.Interaction, user_id: str, grund: str):
    await interaction.response.defer()
    
    url = f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/BanRequest"
    
    payload = {
        "message": f'{{"userId": "{user_id}", "reason": "{grund}", "key": "{SECRET_KEY}"}}'
    }
    
    headers = {
        "x-api-key": ROBLOX_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            await interaction.followup.send(f"✅ Spieler {user_id} wurde erfolgreich gebannt. Grund: {grund}")
        else:
            await interaction.followup.send(f"❌ Fehler bei Roblox: {response.text}")
    except Exception as e:
        await interaction.followup.send(f"❌ Ein technischer Fehler ist aufgetreten: {e}")

# --- 4. Token laden und Bot starten ---
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    print("❌ FEHLER: DISCORD_TOKEN wurde nicht gefunden!")
else:
    client.run(TOKEN)
