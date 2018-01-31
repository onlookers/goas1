"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Aamos Storkey at the University of Edinburgh.
"""
import traceback
import sys
import os
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

    def score_cmd(self, args):
        whiteScore = self.komi
        blackScore = 0

        fboard = self.board.copy().board

        # Count all stones for players
        for point in fboard:
            if point == WHITE:
                whiteScore += 1
            elif point == BLACK:
                blackScore += 1

        # Count territories
        for point in range(len(fboard)):
            if fboard[point]== EMPTY:
                pointStack = [point]
                territory = [point]
                fboard[point] = FLOODFILL
                while pointStack:
                    currentPoint = pointStack.pop()
                    neighbors = self.board._neighbors(currentPoint)
                    for n in neighbors :
                        if fboard[n] == EMPTY:
                            fboard[n] = FLOODFILL
                            pointStack.append(n)
                            territory.append(n)

                belongsTo = None
                changed = False
                for t in territory:
                    neighbors = self.board._neighbors(t)
                    for n in neighbors:
                        if fboard[n] in [WHITE, BLACK]:
                            if belongsTo == None:
                                belongsTo = fboard[n]
                            elif belongsTo != fboard[n]:
                                changed = True
                                break
                    if changed:
                        break
                    
                if not changed:
                    if belongsTo == BLACK:
                        blackScore += len(territory)
                    elif belongsTo == WHITE:
                        whiteScore += len(territory)

                
        
        # Output result
        win = abs(whiteScore - blackScore)
        if whiteScore > blackScore:
            self.respond("W+" + str(win))
        elif whiteScore < blackScore:
            self.respond("B+" + str(win))
        else:
            self.respond(str(win))

