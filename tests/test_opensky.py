from explane.main import find_planes_in_area


def test_call_opensky_api():
    upperboundlat = 52.443184364808296
    lowerboundlat = 52.20764192842824

    upperboundlong = 4.914450293691345
    lowerboundlong = 4.529052796072473

    result = find_planes_in_area(lowerboundlat, upperboundlat, lowerboundlong, upperboundlong)

    print(result)
