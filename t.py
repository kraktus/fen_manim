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
from manimlib import *

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

def batched(iterable, chunk_size):
    iterator = iter(iterable)
    while chunk := tuple(islice(iterator, chunk_size)):
        yield chunk

def with_delimiter(board) -> str:
    return board.__str__().replace("\n", "/\n")

def one_line(board) -> str:
    return board.__str__().replace("\n", "/").replace(" ", "")

def colored_epd(board):
    return Text(board.epd().split(" ")[0], font="Andale Mono", t2c={str(i): BLUE for i in range(1,9)}) #font_size=27)

class Fen(Scene):
    def construct(self):
        board = chess.Board(fen="rnb1k2r/1pq1bppp/p2ppn2/6B1/3NPP2/2N2Q2/PPP3PP/2KR1B1R b kq - 4 9")
        empty = chess.Board(fen=None)
        with open("empty.svg", "w") as f:
            f.write(chess.svg.board(empty))
        with open("board.svg", "w") as f:
            f.write(chess.svg.board(board))
        board_svg = SVGMobject("board.svg", width=7)
        self.add(board_svg)
        #self.wait()
        #self.play(FadeOut(board_svg))
        board_unicode = Text(board.unicode(empty_square=".", invert_color=True), font="Andale Mono", width=810) # Courier New, Optima, Other mono
        self.play(FadeOut(board_svg), FadeIn(board_unicode))
        #self.wait()
        board_anscii = Text(board.__str__(), font="Andale Mono", width=810)
        self.play(ReplacementTransform(board_unicode, board_anscii))
        #self.wait()
        board_anscii_delimited = Text(with_delimiter(board), font="Andale Mono", width=870, t2c={'/': ORANGE})
        self.add(board_anscii_delimited)
        self.wait()
        self.play(TransformMatchingShapes(board_anscii, board_anscii_delimited))
        self.wait()
        board_anscii_oneline = Text(one_line(board), font="Andale Mono", t2c={'/': ORANGE})
        self.play(ReplacementTransform(board_anscii_delimited, board_anscii_oneline))
        self.wait()
        board_anscii_oneline_blue_dot = Text(one_line(board), font="Andale Mono", t2c={'.': BLUE}) #font_size=20)
        self.play(ReplacementTransform(board_anscii_oneline, board_anscii_oneline_blue_dot))
        board_colored_epd = colored_epd(board)
        self.wait()
        self.play(TransformMatchingShapes(board_anscii_oneline_blue_dot, board_colored_epd, run_time=3))

class Test(Scene):
    def construct(self):
        #Text.set_default(font="Andale Mono")
        line0 = Text('♖ ♘ ♗ . ♔ . . ♖', font="Andale Mono")
        line1 = Text('. ♙ ♕ . ♗ ♙ ♙ ♙', font="Andale Mono")
        line2 = Text('♙ . . ♙ ♙ ♘ . .', font="Andale Mono")
        g = VGroup(VGroup(line0, Text("")).arrange(RIGHT), VGroup(line1, Text("")).arrange(RIGHT), line2).arrange(DOWN)
        self.add(g)
        self.wait()
        g2 = VGroup(VGroup(line0, Text("/")).arrange(RIGHT), VGroup(line1, Text("/")).arrange(RIGHT), line2).arrange(DOWN)
        self.play(ReplacementTransform(g, g2))

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