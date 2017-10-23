from hexgrid import Hex, Direction, Layout, layout_flat, Point, pixel_to_hex, layout_pointy, \
    hex_to_pixel, OffsetCoord, qoffset_to_cube, EVEN, qoffset_from_cube, ODD, roffset_to_cube, \
    roffset_from_cube


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
