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


class SquareToCircle(Scene):
    def construct(self):
        board = chess.Board(fen="rnb1k2r/1pq1bppp/p2ppn2/6B1/3NPP2/2N2Q2/PPP3PP/2KR1B1R b kq - 4 9")
        empty = chess.Board(fen=None)
        with open("empty.svg", "w") as f:
            f.write(chess.svg.board(empty))
        with open("board.svg", "w") as f:
            f.write(chess.svg.board(board))
        #board_svg = ImageMobject("fen.png")
        board_svg = SVGMobject("board.svg", width=7)
        board_unicode = board.unicode(empty_square=".", invert_color=True)
        self.add(board_svg)
        #self.wait()
        #self.play(FadeOut(board_svg))
        # for fonts in batched(manimpango.list_fonts(), 4):
        #     g = VGroup()
        #     for font in fonts:
        #         g += VGroup(Text(board_unicode, font=font, width=300), Text(font)).arrange(DOWN)
        #     g.arrange(RIGHT)
        #     self.play(FadeIn(g))
        #     self.wait()
        #     self.remove(g)
        fen_debug = Text(board_unicode, font="Andale Mono", width=810) # Courier New, Optima, Other mono, 
        
        
        #g = VGroup(Text(". p q . b p p p"), Text(". . . . . . B .")).arrange(DOWN)
        self.add(fen_debug)
        print()

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