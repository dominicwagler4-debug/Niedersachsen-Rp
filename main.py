import discord
from discord import app_commands
import requests

# 1. Bot-Setup initialisieren
intents = discord.Intents.default()
client = discord.Client(intents=intents)
bot = app_commands.CommandTree(client)

# Discord-Token (falls du einen Event-Listener für den Start brauchst)
TOKEN = "DEIN_DISCORD_BOT_TOKEN"

# 2. Deine Roblox Daten
ROBLOX_API_KEY = "Z+aS/hlW8kmSJ6buCWtF9buf+xaQw22fGzWKPYavJ+ZBkHQwZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkluTnBaeTB5TURJeExUQTNMVEV6VkRFNE9qVXhPalE1V2lJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaGRXUWlPaUpTYjJKc2IzaEpiblJsY201aGJDSXNJbWx6Y3lJNklrTnNiM1ZrUVhWMGFHVnVkR2xqWVhScGIyNVRaWEoyYVdObElpd2lZbUZ6WlVGd2FVdGxlU0k2SWxvcllWTXZhR3hYT0d0dFUwbzJZblZEVjNSR09XSjFaaXQ0WVZGM01qSm1SM3BYUzFCWllYWktLMXBDYTBoUmR5SXNJbTkzYm1WeVNXUWlPaUkzTWpRNU16WTFNelExSWl3aVpYaHdJam94TnpnMk9ETXlOemswTENKcFlYUWlPakUzT0RZNE1qa3hPVFFzSW01aVppSTZNVGM0TmpneU9URTVOSDAuWEN3NmtvcWxrLVpZZ2g0YUQ1WEZZcmc0X2EtbzdxTWdqN005aWRqQ2xITlJHdTZrdllwM29DWXlfUWUxNkNBeGEzSm05SWtJREhTcDNHWnJ0YnRzaDRXeFZzSkZ4R0t6UnpPN1Y3WEpIdGxEbzV6NnRXdUptVFBZY3cxaU9EdElGMm8zLWJ2YURzVkNPLTZDZHY1T0FrOFloQno4MVVEaHo2MW1sZWU3Y1ZuSVA5eVFCczl2T3U5MFE5VXd2cVdlSk5DNGxxbENKemtkeWYwc3JIOWpFeXY2WmI4UDJLeENnRmxCbndlUm1yenpsTTBzS1Nkd28zSHlSQjI1NXB5ZFZVaFAzNHZCT2tiTGg1bXBncGdkWjhHUmk1ZmVhcTVKYzAzRUVVdjBIeEJNSVFya1FxTWVrVDg3RWVYNmFWWERlcXVZXzRwMW5JX1hpOGNCRms2X2Fn"
UNIVERSE_ID = "9772844823"
SECRET_KEY = "Gamemode"

@client.event
async def on_ready():
    await bot.sync()
    print(f"Eingeloggt als {client.user} und Befehle synchronisiert!")

# 3. Der Ban-Befehl
@bot.command(name="ban", description="Banne einen Spieler im Spiel")
async def ban(interaction: discord.Interaction, user_id: str, grund: str):
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
            await interaction.response.send_message(f"✅ Spieler {user_id} wurde erfolgreich gebannt. Grund: {grund}")
        else:
            await interaction.response.send_message(f"❌ Fehler: {response.text}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Ein technischer Fehler ist aufgetreten: {e}")

# Bot starten (falls du den Token hast, ansonsten lass den Start-Teil so wie er bei dir funktionierte)
# client.run(TOKEN)
