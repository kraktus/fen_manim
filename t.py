#!/usr/local/bin/python3
#coding: utf-8
# Licence: GNU AGPLv3

"""FEN animation"""

from __future__ import annotations

import chess
import chess.svg
import logging
import logging.handlers
import manimpango

from pathlib import Path
from itertools import islice
from typing import Optional, List, Union, Tuple
from manim import *

#############
# Constants #
#############

LOG_PATH = f"{__file__}.log"


########
# Logs #
########

log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)
format_string = "%(asctime)s | %(levelname)-8s | %(message)s"

# 125000000 bytes = 12.5Mb
handler = logging.handlers.RotatingFileHandler(LOG_PATH, maxBytes=12500000, backupCount=3, encoding="utf8")
handler.setFormatter(logging.Formatter(format_string))
handler.setLevel(logging.DEBUG)
log.addHandler(handler)

handler_2 = logging.StreamHandler(sys.stdout)
handler_2.setFormatter(logging.Formatter(format_string))
handler_2.setLevel(logging.INFO)
if __debug__:
    handler_2.setLevel(logging.DEBUG)
log.addHandler(handler_2)

###########
# Classes #
###########


def text_config(font="Andale Mono",width=6,line_spacing=0.6):
    return {'font': font, 'width': width, 'line_spacing': line_spacing}

def with_delimiter(board) -> str:
    return board.__str__().replace("\n", "/\n")

def one_line(board) -> str:
    return board.__str__().replace("\n", "/").replace(" ", "")

def colored_epd(board):
    return Text(board.epd().split(" ")[0], font="Andale Mono", t2c={str(i): BLUE for i in range(1,9)}) #font_size=27)


def one_line_bluedots(board) -> (List[Text], VGroup):
    """try to put dots in their own Text Node for finer grained animation"""
    one_line = board.__str__().replace("\n", "/").replace(" ", "")
    starting_dot_part = None # Optional[int]
    starting_piece_part = None # Optional[int]
    parts = []
    g = VGroup()
    for (i, char) in enumerate(one_line):
        if char != ".":
                if starting_piece_part is None: # We're at the beginning of the FEN
                    starting_piece_part = i
                if starting_dot_part is not None:
                    # evil zero width space inserted to get dots to the same height as other characters
                    dot_part = Text('\u200B' + one_line[starting_dot_part:i], font="Andale Mono", color=BLUE)
                    g += dot_part
                    parts.append(dot_part)
                    starting_dot_part = None
                    starting_piece_part = i
        if char == ".":
                if starting_dot_part is None: # We're at the beginning of the FEN
                    starting_dot_part = i
                if starting_piece_part is not None:
                    piece_part = Text(one_line[starting_piece_part:i], font="Andale Mono")
                    parts.append(piece_part)
                    g += piece_part
                    starting_piece_part = None
                    starting_dot_part = i
    g.arrange_in_grid(cols=len(parts),row_alignments='d')
    return (parts, g)

def replace_dots(parts: List[Text]) -> VGroup:
    g = VGroup()
    for part in parts:
        if "." in part.text:
            x = Text(str(len(part.text)), font="Andale Mono", color=BLUE)
            x.scale(0.4)
            g += x
        else:
            g += part.copy()
    g.arrange_in_grid(cols=len(parts),row_alignments='d',buff=0.1)
    return g

def anscii_board(board) -> (List[Text], VGroup):
    """given a board, return a VGroup with each board line consisting of a sub VGroup with an empty ending, to allow smoother animation when adding slashes at the end"""
    board_lines = [Text(i, font="Andale Mono") for i in board.__str__().split("\n")]
    g = VGroup(*[VGroup(line, Text("")).arrange(RIGHT) for line in board_lines]).arrange(DOWN)
    return (board_lines, g)

def anscii_board_delimited(board_lines: List[Text]) -> VGroup:
    g = VGroup(*[VGroup(line, Text("/", color=ORANGE)).arrange(RIGHT) for line in board_lines[:-1]])
    g += VGroup(board_lines[-1], Text("")).arrange(RIGHT)
    g.arrange(DOWN)
    return g

def one_line_board(board_lines: List[Text]) -> VGroup:
    g = VGroup(*[VGroup(line, Text("/", color=ORANGE)).arrange(RIGHT) for line in board_lines[:-1]])
    g += VGroup(board_lines[-1], Text("")).arrange(RIGHT)
    g.arrange(RIGHT)
    for line in board_lines:
        line.font_size = 16
    return g

class Fen(Scene):
    def construct(self):
        board = chess.Board(fen="rnb1k2r/1pq1bppp/p2ppn2/6B1/3NPP2/2N2Q2/PPP3PP/2KR1B1R b kq - 4 9")
        empty = chess.Board(fen=None)
        with open("empty.svg", "w") as f:
            f.write(chess.svg.board(empty))
        with open("board.svg", "w") as f:
            f.write(chess.svg.board(board))
        board_svg = SVGMobject("board.svg", width=7)
        #self.add(board_svg)
        #self.wait()
        board_unicode = Text(board.unicode(empty_square=".", invert_color=True), **text_config()) # Courier New, Optima, Other mono
        #self.play(FadeOut(board_svg), FadeIn(board_unicode))
        #self.wait()
        #board_anscii = Text(board.__str__(), font="Andale Mono", width=810)
        board_lines, board_anscii = anscii_board(board)
        board_anscii_one_part = Text(board.__str__(),  **text_config())
        #self.play(ReplacementTransform(board_unicode, board_anscii_one_part))
        #self.remove(board_anscii_one_part)
        #self.add(board_anscii)
        #self.wait()
        board_anscii_delimited = Text(with_delimiter(board), t2c={'/': ORANGE}, **text_config(width=6.52))
        #board_anscii_delimited =  anscii_board_delimited(board_lines)
        #self.add(board_anscii_delimited)
        #self.wait()
        #self.play(TransformMatchingShapes(board_anscii_one_part, board_anscii_delimited))
        #self.wait()
        # self.play(board_anscii_delimited.animate.arrange(RIGHT))
        #self.play(board_anscii_delimited.animate.scale(0.4))
        board_anscii_oneline = Text(one_line(board), font="Andale Mono", t2c={'/': ORANGE})
        board_anscii_oneline.scale(0.4)
        #self.play(ReplacementTransform(board_anscii_delimited, board_anscii_oneline))
        #self.wait()
        board_anscii_oneline_blue_dot = Text(one_line(board), font="Andale Mono", t2c={'.': BLUE})
        #parts, board_anscii_oneline_blue_dot = one_line_bluedots(board)
        board_anscii_oneline_blue_dot.scale(0.4)
        #elf.play(TransformMatchingShapes(board_anscii_oneline, board_anscii_oneline_blue_dot))
        self.add(board_anscii_oneline_blue_dot)
        board_colored_epd = colored_epd(board)
        board_colored_epd.scale(0.4)
        #board_colored_epd = replace_dots(parts)
        self.wait()
        self.play(ReplacementTransform(board_anscii_oneline_blue_dot, board_colored_epd, run_time=5))

class Test(Scene):
    def construct(self):
        #Text.set_default(font="Andale Mono")
        line0 = Text('♖ ♘ ♗ . ♔ . . ♖', font="Andale Mono")
        line1 = Text('. ♙ ♕ . ♗ ♙ ♙ ♙', font="Andale Mono")
        line2 = VGroup(Text('♙', font="Andale Mono"), Text(' . . ', font="Andale Mono"), Text('♙ ♙ ♘ . .', font="Andale Mono")).arrange(RIGHT)
        g = VGroup(VGroup(line0, Text("")).arrange(RIGHT), VGroup(line1, Text("")).arrange(RIGHT), line2).arrange(DOWN)
        self.add(g)
        self.wait()
        g2 = VGroup(VGroup(line0, Text("/")).arrange(RIGHT), VGroup(line1, Text("/")).arrange(RIGHT), line2).arrange(DOWN)
        self.play(ReplacementTransform(g, g2))

class Dots(Scene):
    def construct(self):
        #Text.set_default(font="Andale Mono")
        Text.set_default(font="Andale Mono") 
        line0 = Text('....B./')
        line1 = VGroup(Text('....'), Text('B'), Text('.'), Text('/')).arrange_in_grid(cols=4,row_alignments='d')
        line2 = VGroup(Text('4', color=BLUE), Text('B'), Text('1', color=BLUE), Text('/')).arrange_in_grid(cols=4,row_alignments='d')
        self.add(line0)
        self.wait()
        self.play(TransformMatchingShapes(line0, line1, run_time=0.1)) # ideally imperceptible
        self.wait()
        self.play(ReplacementTransform(line1, line2))

class DotsTex(Scene):
    def construct(self):
        #Text.set_default(font="Andale Mono")
        Text.set_default(font="Andale Mono") 
        line0 = Tex('....B./')
        #line1 = VGroup(Text('....'), Text('B'), Text('.'), Text('/')).arrange_in_grid(cols=4,row_alignments='d')
        line2 = Tex('4B1/')
        self.add(line0)
        self.wait()
        self.play(TransformMatchingTex(line0, line2))

# def main() -> None:
#     parser = argparse.ArgumentParser()
#     parser.add_argument("XXX", help="")
#     args = parser.parse_args()

########
# Main #
########

# if __name__ == "__main__":
#     print('#'*80)
#     main()