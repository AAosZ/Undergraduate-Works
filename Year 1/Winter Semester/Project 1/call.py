
import datetime
import os
from typing import Optional
import pygame


# Sprite files to display the start and end of a call
START_CALL_SPRITE = 'data/call-start-2.png'
END_CALL_SPRITE = 'data/call-end-2.png'

class Drawable:
    sprite: Optional[pygame.Surface]
    linelimits: Optional[tuple[float, float]]
    loc: Optional[tuple[float, float]]

    def __init__(self, sprite_file: Optional[str] = None,
                 location: Optional[tuple[float, float]] = None,
                 linelimits: Optional[tuple[tuple[float, float],
                                            tuple[float, float]]] = None) \
            -> None:
        self.linelimits = None
        self.sprite = None
        self.loc = None

        if sprite_file is not None and location is not None:
            self.sprite = pygame.transform.smoothscale(
                pygame.image.load(os.path.join(os.path.dirname(__file__),
                                               sprite_file)), (13, 13))
            self.loc = location
        else:
            self.linelimits = linelimits

    def get_position(self) -> tuple[float, float]:
        return self.loc

    def get_linelimits(self) -> Optional[tuple[float, float]]:
        return self.linelimits


class Call:
    src_number: str
    dst_number: str
    time: datetime.datetime
    duration: int
    src_loc: tuple[float, float]
    dst_loc: tuple[float, float]
    drawables: list[Drawable]
    connection: Drawable

    def __init__(self, src_nr: str, dst_nr: str,
                 calltime: datetime.datetime, duration: int,
                 src_loc: tuple[float, float], dst_loc: tuple[float, float]) \
            -> None:
        self.src_number = src_nr
        self.dst_number = dst_nr
        self.time = calltime
        self.duration = duration
        self.src_loc = src_loc
        self.dst_loc = dst_loc
        self.drawables = [Drawable(sprite_file=START_CALL_SPRITE,
                                   location=src_loc),
                          Drawable(sprite_file=END_CALL_SPRITE,
                                   location=dst_loc)]

        self.connection = Drawable(linelimits=(src_loc, dst_loc))

    def get_bill_date(self) -> tuple[int, int]:
        return self.time.month, self.time.year

    def get_drawables(self) -> list[Drawable]:
        return self.drawables

    def get_connection(self) -> Drawable:
        return self.connection
    
    def __str__(self) -> str:
        return "srcnum" + self.src_number + "srcdst" + self.dst_number + "time"\
            + str(self.time) + "dur" + str(self.duration) + "srcloc"\
            + str(self.src_loc) + "dstloc" + str(self.dst_loc)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'os', 'pygame'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
