import pytest
from ncoreparser.util import Size

class TestSize:
    
    @pytest.mark.parametrize("size1, size2", [("1024 MB", "1 GB"),
                                              ("10 MB", "10 MB"),
                                              ("2048 KB", "2 MB")])
    def test_equal(self, size1, size2):
        s1 = Size(size1)
        s2 = Size(size2)
        assert s1 == s2
    
    @pytest.mark.parametrize("size1, size2", [("1023 MB", "1 GB"),
                                              ("10 MB", "11 MB"),
                                              ("2049 KB", "2 MB")])
    def test_not_equal(self, size1, size2):
        s1 = Size(size1)
        s2 = Size(size2)
        assert s1 != s2
    
    @pytest.mark.parametrize("size1, size2", [("1025 MB", "1 GB"),
                                              ("11 MB", "10 MB"),
                                              ("2049 KB", "2 MB")])
    def test_greater_than(self, size1, size2):
        s1 = Size(size1)
        s2 = Size(size2)
        assert s1 > s2

    @pytest.mark.parametrize("size1, size2", [("1025 MB", "1 GB"),
                                              ("10 MB", "10 MB"),
                                              ("2049 KB", "2 MB"),
                                              ("2048 KB", "2 MB")])
    def test_greater_equal(self, size1, size2):
        s1 = Size(size1)
        s2 = Size(size2)
        assert s1 >= s2
    
    @pytest.mark.parametrize("size1, size2, expected", [("1024 MB", "1 GB", "2.00 GB"),
                                                        ("10 MB", "11 MB", "21.00 MB"),
                                                        ("2048 KB", "2 MB", "4.00 MB")])
    def test_add(self, size1, size2, expected):
        s = Size(size1) + Size(size2)
        assert str(s) == expected
        s = Size(size1)
        s += Size(size2)
        assert str(s) == expected

