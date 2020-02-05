from pytest import approx

from explane.data_types import Location
from explane.location import get_distance_meters, travel_from_point


def test_ground_distance():
    loc_schiphol = Location(52.325291, 4.7222645, 0)
    loc_plane_at_veluwe = Location(52.2185812, 5.8322737, 0)

    assert approx(76452.70936688947) == get_distance_meters(loc_schiphol, loc_plane_at_veluwe)


def test_distance_to_plane_at_altitude():
    loc_schiphol = Location(52.325291, 4.7222645, 0)
    loc_plane_at_veluwe = Location(52.2185812, 5.8322737, 10_000)

    assert approx(77103.93485119984) == get_distance_meters(loc_schiphol, loc_plane_at_veluwe)


def test_travel_from_point():
    assert approx((52.38883677089265, 4.6180672037253565)) \
        == travel_from_point(Location(52.325291, 4.7222645, 0), 315, 10)
