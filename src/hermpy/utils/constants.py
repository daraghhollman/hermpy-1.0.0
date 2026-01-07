import astropy.units as u


class Constants:
    MERCURY_RADIUS = 2_439_700 * u.m

    DIPOLE_OFFSET = 479 * u.km
    DIPOLE_OFFSET_RADII = DIPOLE_OFFSET / MERCURY_RADIUS

    MERCURY_SEMI_MAJOR_AXIS = 57_909_050 * u.km
    SOLAR_MASS = 1.9891e30 * u.kg

    SOLAR_WIND_SPEED_AVG = 400_000 * u.m / u.s

    G = 6.6743e-11 * u.N * u.m**2 / u.kg**2
