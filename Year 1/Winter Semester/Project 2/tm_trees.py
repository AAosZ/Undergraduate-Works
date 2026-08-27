from __future__ import annotations

import math
import os
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None

        # You will change this in Task 5
        self._expanded = False

        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))

        if not subtrees:
            self.data_size = data_size

        else:
            self.data_size = 0
            for tree in subtrees:
                self.data_size += tree.data_size

        for tree in subtrees:
            if not tree.is_empty():
                tree._parent_tree = self

    def is_empty(self) -> bool:
        return self._name is None

    def get_parent(self) -> Optional[TMTree]:
        return self._parent_tree

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        x, y, width, height = rect
        self.rect = rect
        if self.data_size == 0:
            self.rect = (0, 0, 0, 0)

        elif width > height:
            curr = x
            for i in range(len(self._subtrees)):
                if i != len(self._subtrees) - 1 and i < len(self._subtrees):
                    percent = self._subtrees[i].data_size / self.data_size
                    new_width = math.floor(percent * width)
                else:
                    new_width = width + x - curr
                self._subtrees[i].update_rectangles((
                    curr, y, new_width, height))
                curr += new_width

        else:
            curr = y
            for i in range(len(self._subtrees)):
                if i != len(self._subtrees) - 1 and i < len(self._subtrees):
                    percent = self._subtrees[i].data_size / self.data_size
                    new_height = math.floor(percent * height)
                else:
                    new_height = height + y - curr
                self._subtrees[i].update_rectangles((
                    x, curr, width, new_height))
                curr += new_height

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        if self.data_size == 0 or self.is_empty():
            return []

        elif self._expanded:
            if self.is_empty():
                return []

            elif self._subtrees == []:
                if self.data_size != 0:
                    return [(self.rect, self._colour)]

                else:
                    return []

            else:
                rect_list = []
                for subtree in self._subtrees:
                    rect_list.extend(subtree.get_rectangles())

                return rect_list

        else:
            return [(self.rect, self._colour)]

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        x, y = pos
        left, up = self.rect[0], self.rect[1]
        right, down = left + self.rect[2], up + self.rect[3]

        if not (left <= x <= right and up <= y <= down):
            return None

        elif not self._expanded:
            return self

        elif self._subtrees:
            for tree in self._subtrees:
                if tree.get_tree_at_position(pos):
                    return tree.get_tree_at_position(pos)
        return self

    def update_data_sizes(self) -> int:
        if self.is_empty():
            self.data_size = 0

        elif self._subtrees == []:
            pass

        else:
            total = 0
            for tree in self._subtrees:
                total += tree.update_data_sizes()
            self.data_size = total

        return self.data_size

    def move(self, destination: TMTree) -> None:
        if self._subtrees == [] and destination._subtrees:
            destination._subtrees.append(self)
            self._parent_tree.data_size -= self.data_size
            self._parent_tree._subtrees.remove(self)
            destination.update_data_sizes()

    def change_size(self, factor: float) -> None:
        if not self._subtrees == []:
            pass

        else:
            if factor > 0:
                self.data_size += math.ceil(self.data_size * factor)

            else:
                add = math.floor(self.data_size * factor)
                if self.data_size == 0:
                    pass

                elif self.data_size + add < 1:
                    self.data_size = 1

                else:
                    self.data_size += add

    def delete_self(self) -> bool:
        if self._parent_tree is None:
            return False

        parent_subtrees = self._parent_tree._subtrees
        if self in parent_subtrees and self._parent_tree._expanded:
            parent_subtrees.remove(self)
            self._parent_tree.data_size -= self.data_size
            return True

        else:
            return False

    def expand(self) -> None:
        if self._expanded or self._subtrees == []:
            pass

        elif self._subtrees:
            self._expanded = True

        if self._parent_tree:
            self._parent_tree.expand()

    def expand_all(self) -> None:
        if not self._subtrees:
            pass

        else:
            self.expand()
            for tree in self._subtrees:
                tree.expand_all()

    def collapse(self) -> None:
        self._expanded = False
        if self._parent_tree is not None:
            self._parent_tree._expanded = False
            for subtree in self._parent_tree._subtrees:
                subtree._collapse_all()

    def collapse_all(self) -> None:
        tree = self
        while tree._parent_tree is not None:
            tree = tree._parent_tree
        tree._collapse_all()

    def _collapse_all(self) -> None:
        self._expanded = False
        for subtree in self._subtrees:
            if subtree._subtrees == []:
                subtree._expanded = False

            else:
                subtree._collapse_all()

    # Methods for the string representation
    def get_path_string(self) -> str:
        if self._parent_tree is None:
            return self._name
        else:
            return self._parent_tree.get_path_string() + \
                self.get_separator() + self._name

    def get_separator(self) -> str:
        raise NotImplementedError

    def get_suffix(self) -> str:
        raise NotImplementedError


class FileSystemTree(TMTree):
    def __init__(self, path: str) -> None:
        # the file init
        if not os.path.isdir(path):
            TMTree.__init__(self, name=os.path.basename(path), subtrees=[],
                            data_size=os.path.getsize(path))

        # the folder init
        else:
            folders = [os.path.join(path, folder) for folder in
                       os.listdir(path)]
            path_dir = [FileSystemTree(subfolders) for subfolders in folders]

            TMTree.__init__(self, name=os.path.basename(path),
                            subtrees=path_dir, data_size=os.path.getsize(path))

    def get_separator(self) -> str:
        return os.sep

    def get_suffix(self) -> str:

        def convert_size(data_size: float, suffix: str = 'B') -> str:
            suffixes = {'B': 'kB', 'kB': 'MB', 'MB': 'GB', 'GB': 'TB'}
            if data_size < 1024 or suffix == 'TB':
                return f'{data_size:.2f}{suffix}'
            return convert_size(data_size / 1024, suffixes[suffix])

        components = []
        if len(self._subtrees) == 0:
            components.append('file')
        else:
            components.append('folder')
            components.append(f'{len(self._subtrees)} items')
        components.append(convert_size(self.data_size))
        return f' ({", ".join(components)})'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
