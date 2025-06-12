# i have no idea what i'm doing
import discord, json
from discord.ext import commands
from discord.ext.commands import Context
import aiosqlite

VERSION: str = "0.1"

with open("config.json") as f:
  token = json.loads(f.read())["token"]

client = commands.Bot(command_prefix="f!", intents=discord.Intents.all())

@client.event
async def on_ready():
  async with aiosqlite.connect("database.db") as db:
    cursor = await db.cursor()
    await cursor.execute("""CREATE TABLE IF NOT EXISTS cuh (
            id INTEGER PRIMARY KEY,
            money INTEGER
        )""")
    await db.commit()
    await cursor.close()
    await db.close()
    
  print("florbot {} is ready".format(VERSION))

@client.event
async def on_message(msg: discord.Message):
  if msg.author.bot: return
  async with aiosqlite.connect("database.db") as db:
    cursor = await db.cursor()
    await cursor.execute(f"SELECT * FROM cuh WHERE id = {msg.author.id}")
    cuh = await cursor.fetchone()
    if cuh is None:
      await cursor.execute("INSERT INTO cuh(id, money) VALUES (?, ?)", (msg.author.id, 100))
    if "florp" in msg.content:
      await cursor.execute("UPDATE cuh SET money=? WHERE id=?", (cuh[1]+1, msg.author.id))
      await msg.reply("+1 florp")
    await db.commit()
    await cursor.close()
    await db.close()
  await client.process_commands(msg)


@client.command(aliases=["bal"])
async def balance(ctx: Context, member: discord.Member=commands.param(default=None, description="member to see balance")):
  if member is None: member = ctx.author
  async with aiosqlite.connect("database.db") as db:
    cursor = await db.cursor()
    await cursor.execute(f"SELECT * FROM cuh WHERE id = {member.id}")
    cuh = await cursor.fetchone()
    if cuh is None:
      await cursor.execute("INSERT INTO cuh(id, money) VALUES (?, ?)", (member.id, 100))
      await db.commit()
      await cursor.execute(f"SELECT * FROM cuh WHERE id = {member.id}")
      cuh = await cursor.fetchone()
    await cursor.close()
    await db.close()
  e = discord.Embed(colour=discord.Colour.random(), title="{}'s balance".format(member.name))
  e.set_thumbnail(url="attachment://florp.png")
  e.add_field(name=":coin: money", value=cuh[1])
  await ctx.reply(files=[discord.File("florp.png")], embed=e)

client.run(token)