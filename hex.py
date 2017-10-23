from collections import namedtuple
import math
from enum import Enum
from itertools import combinations


class Direction(Enum):
    East = (1, 0)
    NorthEast = (1, -1)
    NorthWest = (0, -1)
    West = (-1, 0)
    SouthWest = (-1, 1)
    SouthEast = (0, 1)


class Hex(namedtuple("Hex", ["q", "r"])):
    def __add__(self, other):
        return Hex(self.q + other.q, self.r + other.r)

    def __sub__(self, other):
        return Hex(self.q - other.q, self.r - other.r)

    def __abs__(self):
        return (abs(self.q) + abs(self.r) + abs(self.s)) // 2

    @property
    def s(self):
        return -self.q - self.r

    def neighbors(self):
        for d in Direction:
            yield self.neighbor(d)

    def scale(self, scale):
        return Hex(self.q * scale, self.r * scale)

    def rotate_counterclockwise(self):
        return Hex(-self.s, -self.q)

    def rotate_clockwise(self):
        return Hex(-self.r, -self.s)

    def neighbor(self, direction: Direction):
        return self + Hex(*direction.value)

    def round(self):
        q = int(round(self.q))
        r = int(round(self.r))
        s = int(round(self.s))
        q_diff = abs(q - self.q)
        r_diff = abs(r - self.r)
        s_diff = abs(s - self.s)
        if q_diff > r_diff and q_diff > s_diff:
            q = -r - s
        else:
            if r_diff < s_diff:
                s = -q - r
            r = -q - s
        return Hex(q, r)

    def path(self, other):
        n = Hex.distance(self, other)
        a_nudge = Hex(self.q + 0.000001, self.r + 0.000001)
        b_nudge = Hex(other.q + 0.000001, other.r + 0.000001)
        results = []
        step = 1.0 / max(n, 1)
        for i in range(0, n + 1):
            results.append(Hex.lerp(a_nudge, b_nudge, step * i).round())
        return results

    @staticmethod
    def distance(a: 'Hex', b: 'Hex'):
        return abs(a - b)

    @staticmethod
    def lerp(a, b, t: float):
        return Hex(a.q * (1 - t) + b.q * t, a.r * (1 - t) + b.r * t)

    @staticmethod
    def spiral():
        h = Hex(0, 0)
        radius = 0
        yield h
        while True:
            radius += 1
            h = h.neighbor(direction=Direction.SouthWest)
            for d in Direction:
                for i in range(radius):
                    yield h
                    h = h.neighbor(direction=d)

# hex_diagonals = [Hex(2, -1), Hex(1, -2), Hex(-1, -1), Hex(-2, 1), Hex(-1, 2),
#                  Hex(1, 1)]


# def hex_diagonal_neighbor(hex, direction):
#     return hex + hex_diagonals[direction]


class Edge(namedtuple('Edge', ['h1', 'h2'])):
    def __eq__(self, other):
        return set(self) == set(other)

    def __hash__(self):
        return hash(self.h1) * hash(self.h2)

    def neighbors(self):
        h3, h4 = set(self.h1.neighbors()).intersection(self.h2.neighbors())
        return [Edge(self.h1, h3),
                Edge(self.h1, h4),
                Edge(self.h2, h3),
                Edge(self.h2, h4)]


class Vertex(namedtuple('Vertex', ['h1', 'h2', 'h3'])):
    def __eq__(self, other):
        return set(self) == set(other)

    def __hash__(self):
        return hash(self.h1) * hash(self.h2) * hash(self.h3)

    def neighbors(self):
        h4 = set(self.h1.neighbors()).intersection(self.h2.neighbors()) - {self.h3}
        h5 = set(self.h1.neighbors()).intersection(self.h3.neighbors()) - {self.h2}
        h6 = set(self.h2.neighbors()).intersection(self.h3.neighbors()) - {self.h1}
        return [Vertex(self.h1, self.h2, h4),
                Vertex(self.h1, self.h3, h5),
                Vertex(self.h2, self.h3, h6)]

    def edges(self):
        return map(Edge, combinations(self, 2))


OffsetCoord = namedtuple("OffsetCoord", ["col", "row"])

EVEN = 1
ODD = -1


def qoffset_from_cube(offset, h):
    col = h.q
    row = h.r + (h.q + offset * (h.q & 1)) // 2
    return OffsetCoord(col, row)


def qoffset_to_cube(offset, h):
    q = h.col
    r = h.row - (h.col + offset * (h.col & 1)) // 2
    return Hex(q, r)


def roffset_from_cube(offset, h):
    col = h.q + (h.r + offset * (h.r & 1)) // 2
    row = h.r
    return OffsetCoord(col, row)


def roffset_to_cube(offset, h):
    q = h.col - (h.row + offset * (h.row & 1)) // 2
    r = h.row
    return Hex(q, r)


Orientation = namedtuple("Orientation", ["f0", "f1", "f2", "f3", "b0", "b1", "b2", "b3",
                                                     "start_angle"])

Layout = namedtuple("Layout", ["orientation", "size", "origin"])

layout_pointy = Orientation(math.sqrt(3.0), math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0,
                            math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0, 0.5)
layout_flat = Orientation(3.0 / 2.0, 0.0, math.sqrt(3.0) / 2.0, math.sqrt(3.0), 2.0 / 3.0, 0.0,
                          -1.0 / 3.0, math.sqrt(3.0) / 3.0, 0.0)


class Point(namedtuple("Point", ["x", "y"])):
    pass


def hex_to_pixel(layout, h):
    m = layout.orientation
    size = layout.size
    origin = layout.origin
    x = (m.f0 * h.q + m.f1 * h.r) * size.x
    y = (m.f2 * h.q + m.f3 * h.r) * size.y
    return Point(x + origin.x, y + origin.y)


def pixel_to_hex(layout, p):
    m = layout.orientation
    size = layout.size
    origin = layout.origin
    pt = Point((p.x - origin.x) / size.x, (p.y - origin.y) / size.y)
    q = m.b0 * pt.x + m.b1 * pt.y
    r = m.b2 * pt.x + m.b3 * pt.y
    return Hex(q, r)


def hex_corner_offset(layout, corner):
    m = layout.orientation
    size = layout.size
    angle = 2.0 * math.pi * (m.start_angle - corner) / 6
    return Point(size.x * math.cos(angle), size.y * math.sin(angle))


def polygon_corners(layout, h):
    corners = []
    center = hex_to_pixel(layout, h)
    for i in range(0, 6):
        offset = hex_corner_offset(layout, i)
        corners.append(Point(center.x + offset.x, center.y + offset.y))
    return corners


########################################
# Tests


def equal_offset_coord(name, a, b):
    assert a.col == b.col and a.row == b.row


def test_hex_arithmetic():
    assert Hex(4, -10) == (Hex(1, -3) + Hex(3, -7))
    assert Hex(-2, 4) == (Hex(1, -3) - Hex(3, -7))


def test_hex_neighbor():
    assert Hex(1, -3) == Hex(1, -2).neighbor(Direction.NorthWest)


# def test_hex_diagonal():
#     equal_hex("hex_diagonal", Hex(-1, -1), hex_diagonal_neighbor(Hex(1, -2), 3))


def test_hex_distance():
    assert 7 == Hex.distance(Hex(3, -7), Hex(0, 0))


def test_hex_rotate_right():
    assert Hex(1, -3).rotate_clockwise() == Hex(3, -2)


def test_hex_rotate_left():
    assert Hex(1, -3).rotate_counterclockwise() == Hex(-2, -1)


def test_hex_round():
    a = Hex(0, 0)
    b = Hex(1, -1)
    c = Hex(0, -1)

    assert Hex(5, -10) == Hex.lerp(Hex(0, 0), Hex(10, -20), 0.5).round()
    assert a.round() == Hex.lerp(a, b, 0.499).round()
    assert b.round() == Hex.lerp(a, b, 0.501).round()
    assert a.round() == Hex(a.q * 0.4 + b.q * 0.3 + c.q * 0.3,
                            a.r * 0.4 + b.r * 0.3 + c.r * 0.3).round()
    assert c.round() == Hex(a.q * 0.3 + b.q * 0.3 + c.q * 0.4,
                            a.r * 0.3 + b.r * 0.3 + c.r * 0.4).round()


def test_hex_linedraw():
    assert [Hex(0, 0), Hex(0, -1), Hex(0, -2), Hex(1, -3), Hex(1, -4), Hex(1, -5)] == \
           Hex(0, 0).path(Hex(1, -5))


def test_layout():
    h = Hex(3, 4)
    flat = Layout(layout_flat, Point(10, 15), Point(35, 71))
    assert h == pixel_to_hex(flat, hex_to_pixel(flat, h)).round()
    pointy = Layout(layout_pointy, Point(10, 15), Point(35, 71))
    assert h == pixel_to_hex(pointy, hex_to_pixel(pointy, h)).round()


def test_conversion_roundtrip():
    a = Hex(3, 4)
    b = OffsetCoord(1, -3)
    assert a == qoffset_to_cube(EVEN, qoffset_from_cube(EVEN, a))
    equal_offset_coord("conversion_roundtrip even-q", b,
                       qoffset_from_cube(EVEN, qoffset_to_cube(EVEN, b)))
    assert a == qoffset_to_cube(ODD, qoffset_from_cube(ODD, a))
    equal_offset_coord("conversion_roundtrip odd-q", b,
                       qoffset_from_cube(ODD, qoffset_to_cube(ODD, b)))
    assert a == roffset_to_cube(EVEN, roffset_from_cube(EVEN, a))
    equal_offset_coord("conversion_roundtrip even-r", b,
                       roffset_from_cube(EVEN, roffset_to_cube(EVEN, b)))
    assert a == roffset_to_cube(ODD, roffset_from_cube(ODD, a))
    equal_offset_coord("conversion_roundtrip odd-r", b,
                       roffset_from_cube(ODD, roffset_to_cube(ODD, b)))


def test_offset_from_cube():
    equal_offset_coord("offset_from_cube even-q", OffsetCoord(1, 3),
                       qoffset_from_cube(EVEN, Hex(1, 2)))
    equal_offset_coord("offset_from_cube odd-q", OffsetCoord(1, 2),
                       qoffset_from_cube(ODD, Hex(1, 2)))


def test_offset_to_cube():
    assert Hex(1, 2) == qoffset_to_cube(EVEN, OffsetCoord(1, 3))
    assert Hex(1, 2) == qoffset_to_cube(ODD, OffsetCoord(1, 2))


if __name__ == '__main__':
    test_hex_arithmetic()
    test_hex_neighbor()
    # test_hex_diagonal()
    test_hex_distance()
    test_hex_rotate_right()
    test_hex_rotate_left()
    test_hex_round()
    test_hex_linedraw()
    test_layout()
    test_conversion_roundtrip()
    test_offset_from_cube()
    test_offset_to_cube()
