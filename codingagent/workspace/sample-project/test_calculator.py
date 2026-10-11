from calculator import calculator


def test_add():
    assert calculator(2, 3, "add") == 5


def test_sub():
    assert calculator(5, 3, "sub") == 2


def test_mul():
    assert calculator(2, 3, "mul") == 6


def test_div():
    assert calculator(6, 3, "div") == 2


def test_mod():
    assert calculator(7, 3, "mod") == 1


def test_invalid_operation():
    try:
        calculator(2, 3, "invalid")
        assert False
    except ValueError:
        assert True
