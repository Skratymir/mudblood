from mudblood import main

def test_add_map():
    """Test if add_map adds a map to the map list"""
    server = main.Server()
    server.add_map("test_map", "./map")
    print(server.maps)
    assert len(server.maps) != 0

def test_update():
    """Check if there are any errors in update"""
    main.Server().update()
    assert True

def test_force_update():
    """Check if there are any errors in force_update"""
    main.Server().force_update()
    assert True
