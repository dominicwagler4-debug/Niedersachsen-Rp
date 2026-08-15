import os
import time
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from aiohttp import web

# Intents einrichten
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class MyBot(commands.Bot):

  def __init__(self):
    super().__init__(command_prefix="!", intents=intents)

  async def setup_hook(self):
    self.add_view(TicketView())
    self.add_view(TicketCloseView())
    await self.tree.sync()
    print(f"Eingeloggt als {self.user} und Slash Commands synchronisiert.")


bot = MyBot()

# Speicher für aktive Shifts und gebannte Roblox-IDs
active_shifts = {}
banned_roblox_ids = set()


# Hilfsfunktion zur Umwandlung von Roblox-Namen in IDs
async def get_roblox_id(username: str):
  url = "https://users.roblox.com/v1/usernames/users"
  payload = {"usernames": [username], "excludeBannedUsers": False}
  async with aiohttp.ClientSession() as session:
    async with session.post(url, json=payload) as resp:
      if resp.status == 200:
        data = await resp.json()
        if data.get("data"):
          return data["data"][0]["id"]
  return None


# -------------------------------------------------------------------------
# 1. TICKET SYSTEM
# -------------------------------------------------------------------------


class TicketView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="🎫 Ticket erstellen",
      style=discord.ButtonStyle.green,
      custom_id="create_ticket",
  )
  async def create_ticket(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    guild = interaction.guild
    existing_channel = discord.utils.get(
        guild.text_channels, name=f"ticket-{interaction.user.name.lower()}"
    )
    if existing_channel:
      await interaction.response.send_message(
          f"Du hast bereits ein offenes Ticket: {existing_channel.mention}",
          ephemeral=True,
      )
      return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(
            read_messages=True, send_messages=True
        ),
        guild.me: discord.PermissionOverwrite(
            read_messages=True, send_messages=True
        ),
    }

    ticket_channel = await guild.create_text_channel(
        f"ticket-{interaction.user.name}", overwrites=overwrites
    )
    await interaction.response.send_message(
        f"Dein Ticket wurde erstellt: {ticket_channel.mention}", ephemeral=True
    )

    close_view = TicketCloseView()
    await ticket_channel.send(
        f"Hallo {interaction.user.mention}! Ein Teammitglied wird sich gleich"
        " kümmern.\nKlicke auf den Button, um das Ticket zu schließen.",
        view=close_view,
    )


class TicketCloseView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="🔒 Ticket schließen",
      style=discord.ButtonStyle.red,
      custom_id="close_ticket",
  )
  async def close_ticket(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_message("Ticket wird in 5 Sekunden gelöscht...")
    await discord.utils.sleep_until(
        discord.utils.utcnow() + discord.timedelta(seconds=5)
    )
    await interaction.channel.delete()


@bot.tree.command(
    name="ticketpanel",
    description="Erstellt das Ticket-Panel (Nur für Admins)",
)
@app_commands.checks.has_permissions(administrator=True)
async def ticketpanel(interaction: discord.Interaction):
  view = TicketView()
  embed = discord.Embed(
      title="Support Tickets",
      description="Klicke auf den Button unten, um ein Ticket zu erstellen.",
      color=discord.Color.blue(),
  )
  await interaction.channel.send(embed=embed, view=view)
  await interaction.response.send_message(
      "Ticket-Panel erfolgreich erstellt!", ephemeral=True
  )


# -------------------------------------------------------------------------
# 2. SHIFT SYSTEM
# -------------------------------------------------------------------------

shift = app_commands.Group(name="shift", description="Verwalte deine Shifts")


@shift.command(name="start", description="Startet deine Shift")
async def shift_start(interaction: discord.Interaction):
  user_id = interaction.user.id
  if user_id in active_shifts:
    await interaction.response.send_message(
        "Du hast bereits eine laufende Shift!", ephemeral=True
    )
    return

  active_shifts[user_id] = time.time()
  embed = discord.Embed(
      title="⏱️ Shift Gestartet",
      description=f"{interaction.user.mention} hat die Shift begonnen.",
      color=discord.Color.green(),
  )
  await interaction.response.send_message(embed=embed)


@shift.command(name="end", description="Beendet deine Shift")
async def shift_end(interaction: discord.Interaction):
  user_id = interaction.user.id
  if user_id not in active_shifts:
    await interaction.response.send_message(
        "Du hast keine aktive Shift!", ephemeral=True
    )
    return

  start_time = active_shifts.pop(user_id)
  elapsed_seconds = int(time.time() - start_time)
  hours = elapsed_seconds // 3600
  minutes = (elapsed_seconds % 3600) // 60
  seconds = elapsed_seconds % 60

  embed = discord.Embed(
      title="⏱️ Shift Beendet",
      description=(
          f"{interaction.user.mention} hat die Shift"
          f" beendet.\n**Gesamtzeit:** {hours}h {minutes}m {seconds}s"
      ),
      color=discord.Color.red(),
  )
  await interaction.response.send_message(embed=embed)


bot.tree.add_command(shift)

# -------------------------------------------------------------------------
# 3. UPRANK & DOWNRANK SYSTEM
# -------------------------------------------------------------------------


@bot.tree.command(
    name="uprank", description="Befördere einen Benutzer auf eine neue Rolle"
)
@app_commands.checks.has_permissions(manage_roles=True)
async def uprank(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role,
):
  await member.add_roles(role)
  embed = discord.Embed(
      title="📈 Uprank",
      description=(
          f"{member.mention} wurde erfolgreich auf **{role.name}** befördert!"
      ),
      color=discord.Color.gold(),
  )
  await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="downrank", description="Stufe einen Benutzer von einer Rolle herab"
)
@app_commands.checks.has_permissions(manage_roles=True)
async def downrank(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role,
):
  await member.remove_roles(role)
  embed = discord.Embed(
      title="📉 Downrank",
      description=(
          f"Die Rolle **{role.name}** wurde von {member.mention} entfernt."
      ),
      color=discord.Color.dark_red(),
  )
  await interaction.response.send_message(embed=embed)


# -------------------------------------------------------------------------
# 4. ANKÜNDIGUNGS SYSTEM
# -------------------------------------------------------------------------


@bot.tree.command(
    name="announce", description="Erstelle eine offizielle Ankündigung"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def announce(
    interaction: discord.Interaction,
    text: str,
    channel: discord.TextChannel = None,
):
  target_channel = channel or interaction.channel
  embed = discord.Embed(
      title="📢 Ankündigung", description=text, color=discord.Color.blue()
  )
  embed.set_footer(text=f"Ankündigung von {interaction.user.name}")
  await target_channel.send(embed=embed)
  await interaction.response.send_message(
      f"Ankündigung erfolgreich in {target_channel.mention} gesendet!",
      ephemeral=True,
  )


# -------------------------------------------------------------------------
# 5. ROBLOX BAN & UNBAN PROTOKOLL
# -------------------------------------------------------------------------


@bot.tree.command(
    name="ban", description="Zeigt die Roblox-ID zum Bannen eines Spielers an"
)
@app_commands.checks.has_permissions(ban_members=True)
async def roblox_ban(
    interaction: discord.Interaction,
    roblox_name: str,
    grund: str = "Kein Grund angegeben",
):
  await interaction.response.defer(ephemeral=True)

  roblox_id = await get_roblox_id(roblox_name)
  if not roblox_id:
    await interaction.followup.send(
        f"❌ Der Roblox-Benutzer **{roblox_name}** wurde nicht gefunden!",
        ephemeral=True,
    )
    return

  banned_roblox_ids.add(str(roblox_id))

  embed = discord.Embed(
      title="🔨 Notruf Emden - Ban Protokoll",
      description=(
          f"**Spieler:** {roblox_name}\n**Roblox-ID:** `{roblox_id}`\n**Grund:**"
          f" {grund}\n\n*Trage diese ID im In-Game-Menü ein, um den Spieler zu"
          " bannen.*"
      ),
      color=discord.Color.dark_grey(),
  )
  await interaction.followup.send(embed=embed)


@bot.tree.command(
    name="unban", description="Zeigt die Roblox-ID zum Entbannen eines Spielers an"
)
@app_commands.checks.has_permissions(ban_members=True)
async def roblox_unban(
    interaction: discord.Interaction, roblox_name: str
):
  await interaction.response.defer(ephemeral=True)

  roblox_id = await get_roblox_id(roblox_name)
  if not roblox_id:
    await interaction.followup.send(
        f"❌ Der Roblox-Benutzer **{roblox_name}** wurde nicht gefunden!",
        ephemeral=True,
    )
    return

  banned_roblox_ids.discard(str(roblox_id))

  embed = discord.Embed(
      title="🔓 Notruf Emden - Unban Protokoll",
      description=(
          f"**Spieler:** {roblox_name}\n**Roblox-ID:**"
          f" `{roblox_id}`\n\n*Entbanne diesen Spieler im In-Game-Menü, damit"
          " er wieder joinen kann.*"
      ),
      color=discord.Color.green(),
  )
  await interaction.followup.send(embed=embed)


# --- Mini-Webserver (Hält Render glücklich) ---
async def handle_bans(request):
  return web.json_response(list(banned_roblox_ids))


async def start_web_server():
  app = web.Application()
  app.router.add_get("/bans", handle_bans)
  runner = web.AppRunner(app)
  await runner.setup()
  port = int(os.getenv("PORT", 10000))
  site = web.TCPSite(runner, "0.0.0.0", port)
  await site.start()
  print(f"Webserver läuft auf Port {port}")


async def main():
  token = os.getenv("DISCORD_TOKEN")
  if not token:
    print("Fehler: Kein DISCORD_TOKEN in den Umgebungsvariablen gefunden!")
    return

  await start_web_server()
  await bot.start(token)


if __name__ == "__main__":
  import asyncio

  asyncio.run(main())
