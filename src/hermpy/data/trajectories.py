import datetime as dt
from functools import cache

import astropy.units as u
import numpy as np
import spiceypy as spice

from hermpy.utils import Constants, DateLike, DateSequence


def get_aberration_angle(
    datetimes: DateLike | DateSequence,
) -> u.Quantity:

    # Force list format even for single input
    if isinstance(datetimes, DateLike):
        dates = datetimes if isinstance(datetimes, dt.date) else datetimes.date()
    else:
        dates = [d if isinstance(d, dt.date) else d.date() for d in datetimes]

    aberration_angles = u.Quantity([_get_aberration_angle_single(d) for d in dates])

    aberration_angles = np.squeeze(aberration_angles)

    assert isinstance(aberration_angles, u.Quantity)

    return aberration_angles


@cache
def _get_aberration_angle_single(date: dt.date) -> u.Quantity:
    # Compute aberration for a single date

    mercury_distance = get_heliocentric_distance(date)
    a = Constants.MERCURY_SEMI_MAJOR_AXIS
    M = Constants.SOLAR_MASS
    G = Constants.G

    orbital_velocity = np.sqrt(G * M * ((2 / mercury_distance) - (1 / a)))

    return np.arctan(orbital_velocity / Constants.SOLAR_WIND_SPEED_AVG)


def get_heliocentric_distance(
    datetimes: DateLike | DateSequence,
) -> u.Quantity:

    if isinstance(datetimes, (dt.date, dt.datetime)):
        datetimes_list: list[DateLike] = [datetimes]
    else:
        datetimes_list = list(datetimes)

    ets = spice.datetime2et(datetimes_list)
    positions, _ = spice.spkpos("MERCURY", ets, "J2000", "NONE", "SUN")

    distances = np.linalg.norm(positions, axis=1) * u.km

    return distances
