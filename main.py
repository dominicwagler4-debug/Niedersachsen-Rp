import discord
from discord import app_commands
import requests

# HIER DEINE DATEN EINTRAGEN
ROBLOX_API_KEY = "DEIN_API_KEY_HIER_EINFUEGEN"
UNIVERSE_ID = "9772844823"
SECRET_KEY = "DEIN_GEHEIMES_PASSWORT_HIER" # Das gleiche, das im Roblox-Skript steht!

# ... (Dein restlicher Bot-Code) ...

@bot.tree.command(name="ban", description="Banne einen Spieler im Spiel")
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
