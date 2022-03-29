import os
import discord
import chess
import chess.svg
from discord.ext import commands, tasks
from cairosvg import svg2png
from stockfish import Stockfish

class Game:
    def __init__(self, game_info=None):
        self.game_type = game_info
        self.engine = Stockfish(depth=20, parameters={"Skill Level": 20})
        self.board = chess.Board() 
        self.votes = dict()
        self.moves = dict()

    def engine_move(self):
        # make engine move
        self.engine.set_fen_position(self.board.fen())
        self.board.push(self.board.parse_uci(self.engine.get_best_move()))

    def user_move(self):
        # make most voted user move
        try:
            self.board.push(max(self.moves, key=self.moves.get))
        except:
            return False
        self.votes.clear()
        self.moves.clear()
        return True

    def submit_vote_move(self, user, san_move):
        try:
            move = self.board.parse_san(san_move)
        except:
            return False
        if move in self.board.legal_moves:
            self.votes[user] = move
            self.moves = self.get_move_votes()
            return True
        else:
            return False
    
    def get_move_votes(self):
        moves = dict()
        for i in self.votes.values():
            moves[i] = moves.get(i, 0) + 1
        return moves

    def generate_discord_board_image(self):
        svg2png(bytestring=chess.svg.board(self.board),write_to='output.png')
        with open('output.png', 'rb') as f:
            return discord.File(f)


with open("./token", "r") as f:
    TOKEN = f.read()

GUILD = "Lambda's bot testing shithole"

game = Game()
bot = commands.Bot(command_prefix='$')

@bot.command(name='list')
async def _create(ctx):
    moves = game.get_move_votes()
    msg = ""
    for move in moves:
        msg = msg+game.board.san(move)+": "+str(moves[move])+"\n"
    await ctx.channel.send(msg)
        

@bot.command(name='vote')
async def _vote(ctx, move):
    if(game.submit_vote_move(ctx.author, move)):
        await ctx.message.add_reaction('\N{Thumbs Up Sign}')
    else:
        await ctx.message.add_reaction('\N{Thumbs Down Sign}')

@tasks.loop(minutes=.25)
async def submit():
    channel = discord.utils.get(discord.utils.find(lambda g: g.name == GUILD, bot.guilds).channels, name="general")
    if(game.user_move()):
        game.engine_move()
        await channel.send(file=game.generate_discord_board_image())
    
    
@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    print(
        f'{bot.user} has connected to:\n'
        f'{guild.name}(id: {guild.id})'
        )
    submit.start()

bot.run(TOKEN)
