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

SCALE = 0.4

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
    return Text(board.epd().split(" ")[0], font="Andale Mono", t2c={str(i): BLUE for i in range(1,9)} | {'/': ORANGE}) #font_size=27)

def brace_of(x, caption: str, color, direction=UP, buff=0.25):
    brace = Brace(x, direction=direction, color=color)
    if direction.all() == UP.all():
        brace.stretch(-1,0)
    brace_caption = Text(caption, font="Andale Mono", color=color)
    brace_caption.scale(SCALE + 0.1)
    brace_caption.next_to(brace, direction, buff=buff)
    return brace, brace_caption

# TODO, refactor must be easier way
def one_line_bluedots(board) -> (List[Text], VGroup):
    """try to put dots in their own Text Node for finer grained animation"""
    one_line = board.__str__().replace("\n", "/").replace(" ", "")
    starting_dot_part = None # Optional[int]
    starting_piece_part = None # Optional[int]
    parts = []
    g = VGroup()
    def on_piece(g: VGroup, x: int):
        nonlocal starting_piece_part
        nonlocal starting_dot_part
        if starting_piece_part is None: # We're at the beginning of a piece sequence
            starting_piece_part = x
        if starting_dot_part is not None:
            dot_part = Text(one_line[starting_dot_part:x], font="Andale Mono", color=BLUE)
            g += dot_part
            parts.append(dot_part)
            starting_dot_part = None
            starting_piece_part = x

    def on_dot(g: VGroup, x: int):
        nonlocal starting_piece_part
        nonlocal starting_dot_part
        if starting_dot_part is None: # We're at the beginning of a dot sequence
            starting_dot_part = x
        if starting_piece_part is not None:
            piece_part = Text(one_line[starting_piece_part:x], font="Andale Mono",t2c={'/': ORANGE})
            parts.append(piece_part)
            g += piece_part
            starting_piece_part = None
            starting_dot_part = x

    for (i, char) in enumerate(one_line):
        if char != ".":
            on_piece(g, i)
        else:
            on_dot(g, i)
    # to close the last part
    if one_line[-1] == ".":
        # call on_piece when it's a dot to finish the last piece part
        on_piece(g, len(one_line))
    else:
        on_dot(g, len(one_line))
    g.arrange_in_grid(cols=len(parts),row_alignments='d')
    return (parts, g)

def replace_dots(parts: List[Text]) -> VGroup:
    g = VGroup()
    for part in parts:
        if "." in part.text:
            x = Text(str(len(part.text)), font="Andale Mono", color=BLUE)
            x.scale(SCALE)
            g += x
        else:
            g += part.copy()
    g.arrange_in_grid(cols=len(parts),row_alignments='d',buff=0.05)
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
        fen = "rnb1k2r/1pq1bppp/p2ppn2/6B1/3NPP2/2N2Q2/PPP3PP/2KR1B1R b kq - 4 9"
        board = chess.Board(fen=fen)
        empty = chess.Board(fen=None)
        with open("empty.svg", "w") as f:
            f.write(chess.svg.board(empty))
        with open("board.svg", "w") as f:
            f.write(chess.svg.board(board))
        board_svg = SVGMobject("board.svg", width=7)
        self.add(board_svg)
        #self.wait()
        board_unicode = Text(board.unicode(empty_square=".", invert_color=True), **text_config()) # Courier New, Optima, Other mono
        self.play(FadeOut(board_svg), FadeIn(board_unicode))
        #self.wait()
        board_anscii = Text(board.__str__(), font="Andale Mono", width=810)
        #board_lines, board_anscii = anscii_board(board)
        board_anscii_one_part = Text(board.__str__(),  **text_config())
        self.play(ReplacementTransform(board_unicode, board_anscii_one_part))
        #self.remove(board_anscii_one_part)
        #self.add(board_anscii)
        #self.wait()
        board_anscii_delimited = Text(with_delimiter(board), t2c={'/': ORANGE}, **text_config(width=6.52))
        #board_anscii_delimited =  anscii_board_delimited(board_lines)
        #self.add(board_anscii_delimited)
        #self.wait()
        self.play(TransformMatchingShapes(board_anscii_one_part, board_anscii_delimited))
        #self.wait()
        self.play(board_anscii_delimited.animate.scale(SCALE))
        board_anscii_oneline = Text(one_line(board), font="Andale Mono", t2c={'/': ORANGE})
        board_anscii_oneline.scale(SCALE)
        self.play(ReplacementTransform(board_anscii_delimited, board_anscii_oneline))
        #self.wait()
        #board_anscii_oneline_blue_dot = Text(one_line(board), font="Andale Mono", t2c={'.': BLUE})
        parts, board_anscii_oneline_blue_dot = one_line_bluedots(board)
        board_anscii_oneline_blue_dot.scale(SCALE)
        self.play(TransformMatchingShapes(board_anscii_oneline, board_anscii_oneline_blue_dot))
        self.add(board_anscii_oneline_blue_dot)
        board_colored_epd_final = colored_epd(board)
        board_colored_epd_final.scale(SCALE)
        board_colored_epd = replace_dots(parts)
        self.play(ReplacementTransform(board_anscii_oneline_blue_dot, board_colored_epd, run_time=2))
        self.play(TransformMatchingShapes(board_colored_epd, board_colored_epd_final))
        self.play(board_colored_epd_final.animate.set_color(WHITE).shift(2 * LEFT))
        turn = Text(fen.split(" ")[1], font="Andale Mono")
        turn.next_to(board_colored_epd_final, RIGHT)
        turn.scale(SCALE)
        castling = Text(fen.split(" ")[2], font="Andale Mono")
        castling.next_to(turn, RIGHT)
        castling.scale(SCALE)
        ep = Text(fen.split(" ")[3])
        ep.next_to(castling, RIGHT)
        ep.scale(SCALE)
        counters = Text(" ".join(fen.split(" ")[4:]), font="Andale Mono")
        counters.next_to(ep, RIGHT,buff=0)
        counters.scale(SCALE)
        self.play(
            AnimationGroup(
                FadeIn(turn, shift=DOWN), 
                FadeIn(castling, shift=DOWN), 
                FadeIn(ep, shift=DOWN), 
                FadeIn(counters, shift=DOWN),
                lag_ratio=0.4
                )
            )
        self.play(
            AnimationGroup(
                self.add_brace(board_colored_epd_final, "Board", direction=UP,color=GREEN),
                self.add_brace(turn, "Turn", direction=DOWN,color=ORANGE),
                self.add_brace(castling, "Castling", direction=UP,color=BLUE),
                self.add_brace(ep, "En-passant", direction=DOWN,color=PINK,buff=0),
                self.add_brace(counters, "Counters", direction=UP,color=LIGHT_GREY,buff=0.7),
                lag_ratio=0.9,
                )
        )
        self.wait()

    def add_brace(self, of, caption, direction, color, buff=0.25):
        brace, caption = brace_of(of, caption, direction=direction,color=color,buff=buff)
        return AnimationGroup(of.animate.set_color(color),Write(caption,run_time=1),Write(brace, run_time=1), lag_ratio=0.4)

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

class ShiftAndColor(Scene):
    def construct(self):
        #Text.set_default(font="Andale Mono")
        Text.set_default(font="Andale Mono") 
        line0 = Text('Foo')
        self.add(line0)
        self.wait()
        self.play(AnimationGroup(
                line0.animate.set_color(YELLOW),
                line0.animate.shift(2 * LEFT),
                ))

class BraceCreateLeft(Scene):
    def construct(self):
        Text.set_default(font="Andale Mono") 
        line0 = Text('Foo')
        brace = Brace(line0, direction=UP)
        caption = Text("Bar")
        caption.next_to(brace, UP)
        self.add(line0)
        self.wait()
        self.play(AnimationGroup(Write(caption,run_time=1),Write(brace, run_time=1, reverse=True), lag_ratio=0.4))

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