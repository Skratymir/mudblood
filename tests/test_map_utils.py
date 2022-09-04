from mudblood import map_utils

def test_parse_position():
    assert map_utils._parse_position([0, 0]) == "0-0"
    assert map_utils._parse_position([5, 2]) == "5-2"
