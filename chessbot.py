import os
import discord
import chess
import chess.svg
from discord.ext import commands, tasks
from cairosvg import svg2png
from stockfish import Stockfish

from game import Game

with open("./token", "r") as f:
    TOKEN = f.read()

GUILD = "Lambda's bot testing shithole"

game = None
bot = commands.Bot(command_prefix='$')

channel = None

@bot.command(name='list')
async def _list(ctx):
    moves = game.get_move_votes()
    msg = ""
    for move in moves:
        msg = msg+game.board.san(move)+": "+str(moves[move])+"\n"
    await ctx.channel.send(msg)
        
@bot.command(name='create')
async def _create(ctx, interval, engine_playsfor, difficulty, game_type):
    try:
        submit.start()
        submit.change_interval(seconds=int(interval))
        global game
        if engine_playsfor == "white": 
            game = Game(interval, chess.WHITE, difficulty, game_type)
        else:
            game = Game(interval, chess.BLACK, difficulty, game_type)
        if game_type == "engine" and engine_playsfor == "white":
            game.engine_move()
    except:
        return
    await channel.send(file=game.generate_discord_board_image())

@bot.command(name='stop')
async def _stop(ctx):
    try:
        submit.stop()
    except:
        return
    
@tasks.loop(seconds=30)
async def submit():
    if(game.user_move()):
        game.engine_move()
        await channel.send(file=game.generate_discord_board_image())

@bot.command(name='vote')
async def _vote(ctx, move):
    if(game.submit_vote_move(ctx.author, move)):
        await ctx.message.add_reaction('\N{Thumbs Up Sign}')
    else:
        await ctx.message.add_reaction('\N{Thumbs Down Sign}')    
    
@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    print(
        f'{bot.user} has connected to:\n'
        f'{guild.name}(id: {guild.id})'
        )
    global channel
    channel = discord.utils.get(discord.utils.find(lambda g: g.name == GUILD, bot.guilds).channels, name="general")

bot.run(TOKEN)
