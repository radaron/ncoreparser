import pytest
from ncoreparser.util import Size


class TestSize:
    @pytest.mark.parametrize("size1, size2", [("1024 MiB", "1 GiB"),
                                              ("10 MiB", "10 MiB"),
                                              ("2048 KiB", "2 MiB")])
    def test_equal(self, size1, size2):
        s1 = Size(size1)
        s2 = Size(size2)
        assert s1 == s2

    @pytest.mark.parametrize("size1, size2", [("1023 MiB", "1 GiB"),
                                              ("10 MiB", "11 MiB"),
                                              ("2049 KiB", "2 MiB")])
    def test_not_equal(self, size1, size2):
        s1 = Size(size1)
        s2 = Size(size2)
        assert s1 != s2

    @pytest.mark.parametrize("size1, size2", [("1025 MiB", "1 GiB"),
                                              ("11 MiB", "10 MiB"),
                                              ("2049 KiB", "2 MiB")])
    def test_greater_than(self, size1, size2):
        s1 = Size(size1)
        s2 = Size(size2)
        assert s1 > s2

    @pytest.mark.parametrize("size1, size2", [("1025 MiB", "1 GiB"),
                                              ("10 MiB", "10 MiB"),
                                              ("2049 KiB", "2 MiB"),
                                              ("2048 KiB", "2 MiB")])
    def test_greater_equal(self, size1, size2):
        s1 = Size(size1)
        s2 = Size(size2)
        assert s1 >= s2

    @pytest.mark.parametrize("size1, size2, expected", [("1024 MiB", "1 GiB", "2.00 GiB"),
                                                        ("10 MiB", "11 MiB", "21.00 MiB"),
                                                        ("2048 KiB", "2 MiB", "4.00 MiB")])
    def test_add(self, size1, size2, expected):
        s = Size(size1) + Size(size2)
        assert str(s) == expected
        s = Size(size1)
        s += Size(size2)
        assert str(s) == expected
