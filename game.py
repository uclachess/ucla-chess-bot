import os
import discord
import chess
import chess.svg
from discord.ext import commands, tasks
from cairosvg import svg2png
from stockfish import Stockfish

class Game:
    def __init__(self, interval, engine_playsfor, difficulty, game_type):
        self.game_type = game_type
        self.engine = Stockfish(depth=25, parameters={"Skill Level": difficulty, "Threads": 8})
        self.board = chess.Board() 
        self.votes = dict()
        self.moves = dict()

        self.interval = interval;
        self.engine_playsfor = engine_playsfor;
        
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
        if self.game_type == "engine" and self.engine_playsfor == chess.WHITE:
            svg2png(bytestring=chess.svg.board(self.board, orientation=chess.BLACK),write_to='output.png')
        else:
            svg2png(bytestring=chess.svg.board(self.board),write_to='output.png')
        with open('output.png', 'rb') as f:
            return discord.File(f)
