"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Aamos Storkey at the University of Edinburgh.
"""
import traceback
import sys
import os
utilpath = sys.path[0] + "/../util/"
sys.path.append(utilpath)

from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL
import gtp_connection
import numpy as np
import re

class GtpConnectionGo1(gtp_connection.GtpConnection):

    def __init__(self, go_engine, board, outfile = 'gtp_log', debug_mode = False):
        """
        GTP connection of Go1

        Parameters
        ----------
        go_engine : GoPlayer
            a program that is capable of playing go by reading GTP commands
        komi : float
            komi used for the current game
        board: GoBoard
            SIZExSIZE array representing the current board state
        """
        gtp_connection.GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)
        self.commands["hello"] = self.hello_cmd
        self.commands["score"] = self.score_cmd


    def hello_cmd(self, args):
        """ Dummy Hello Command """
        self.respond("Hello! " + self.go_engine.name)

    def score_cmd(self,args):
        # Add the white/black stones on the board to white/black score first

        whiteScore = np.sum(self.board.board == WHITE)
        self.respond("init White" +str(whiteScore))
        blackScore = np.sum(self.board.board == BLACK)
        self.respond("init Black" +str(blackScore))



        #Add the score of white/black by counting the empty owned by black/white stone

        empties = list(*np.where(self.board.board == EMPTY))
        for empty in empties:
            # using _is_eyeish(empty) to figure out the empties are white or black points
            result = self.board._is_eyeish(empty)
            if result == BLACK:
                blackScore += 1
            elif result == WHITE:
                whiteScore += 1
        self.respond("eyeish added White" +str(whiteScore))
        self.respond("eyeish added Black" +str(blackScore))
        #Add komi to white score and passes to white/black score
        whiteScore += self.komi
        whiteScore -= self.board.passes_white
        blackScore -= self.board.passes_black

        self.respond("komi/pass added White" +str(whiteScore))
        self.respond("komi/pass added Black" +str(blackScore))

        if blackScore > whiteScore:
            WinnerScore = blackScore - whiteScore
            self.respond("B\+" + str(WinnerScore))

        elif blackScore < whiteScore:
            WinnerScore = whiteScore - blackScore
            self.respond("W\+" + str(WinnerScore))
        else:
            self.respond("drawn")

