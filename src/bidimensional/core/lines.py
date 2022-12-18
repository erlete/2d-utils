from __future__ import annotations

from .coordinates import Coordinate
from typing import Generator


class Line:
    """A class to represent a line in 2D space.

    This class provides a way to represent a line in 2D space. It must be
    composed by two Coordinate objects.

    Args:
        a (Coordinate): The first coordinate.
        b (Coordinate): The second coordinate.

    Attributes:
        a (Coordinate): The first coordinate.
        b (Coordinate): The second coordinate.
        slope (float): The slope of the line.
    """

    def __init__(self, a: Coordinate, b: Coordinate) -> None:
        self._properties = {}

        self.a = a
        self.b = b

    @property
    def a(self) -> Coordinate:
        return self._a

    @a.setter
    def a(self, value) -> None:
        if not isinstance(value, Coordinate):
            raise TypeError("value must be a Coordinate object.")

        self._a = value
        self._properties.clear()

    @property
    def b(self) -> Coordinate:
        return self._b

    @b.setter
    def b(self, value) -> None:
        if not isinstance(value, Coordinate):
            raise TypeError("value must be a Coordinate object.")

        self._b = value
        self._properties.clear()

    @property
    def slope(self) -> float:
        if self._properties.get("slope") is None:
            self._properties["slope"] = (
                (self.b.y - self.a.y)
                / (self.b.x - self.a.x)
            )

        return self._properties["slope"]

    def intersect(self, line: Line) -> Coordinate | None:
        """Determines the intersection between two lines.

        Args:
            line (Line): the line to determine the intersection with.

        Raises:
            TypeError: if line is not a Line object.

        Returns:
            Coordinate | None: the intersection between the two lines (if it
                exists, otherwise None).
        """

        if not isinstance(line, Line):
            raise TypeError(f"Expected Line, got {type(line)}")

        if self.slope == line.slope:
            return None

        x = (line.b.y - self.b.y + self.slope * self.b.x - line.slope * line.b.x) / (self.slope - line.slope)
        y = self.slope * (x - self.b.x) + self.b.y

        return Coordinate(x, y)

    def __mul__(self, line: Line) -> Coordinate | None:
        return self.intersect(line)

    def __eq__(self, value) -> bool:
        if not isinstance(value, Line):
            raise TypeError("value must be a Line object.")

        return self.a == value.a and self.b == value.b

    def __ne__(self, value) -> bool:
        if not isinstance(value, Line):
            raise TypeError("value must be a Line object.")

        return self.a != value.a or self.b != value.b

    def __hash__(self) -> int:
        return hash((self.a, self.b))

    def __getitem__(self, index) -> Coordinate:
        if index == 0:
            return self.a
        elif index == 1:
            return self.b
        else:
            raise IndexError("index must be 0 or 1")

    def __setitem__(self, index, value) -> None:
        if index == 0:
            self.a = value
        elif index == 1:
            self.b = value
        else:
            raise IndexError("index must be 0 or 1")

    def __iter__(self) -> Generator[Coordinate, None, None]:
        yield self.a
        yield self.b

    def __reversed__(self) -> Generator[Coordinate, None, None]:
        yield self.b
        yield self.a

    def __getattr__(self, name) -> Coordinate:
        if name == 'a':
            return self.a
        elif name == 'b':
            return self.b
        else:
            raise AttributeError(f"{name} is not an attribute")

    def __delattr__(self, name) -> None:
        if name == 'a':
            del self.a
        elif name == 'b':
            del self.b
        else:
            raise AttributeError(f"{name} is not an attribute")

    def __str__(self) -> str:
        return f"Line({self.a}, {self.b})"

    def __repr__(self) -> str:
        return f"Line({self.a}, {self.b})"

    def __len__(self) -> int:
        return 2