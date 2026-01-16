import matplotlib.pyplot as plt
import numpy as np


def plot_magnetospheric_boundaries(
    ax: plt.Axes,
    plane: str = "xy",
    sub_solar_magnetopause: float = 1.45,
    alpha: float = 0.5,
    psi: float = 1.04,
    p: float = 2.75,
    initial_x: float = 0.5,
    add_legend: bool = False,
    zorder: int = 0,
    color="black",
    lw=1,
) -> None:
    """Add average magnetopause and bow shock locations based on
    Winslow et al. (2013).

    Add the plane projection of the average magnetopause and
    bow shock locations based on Winslow et al. (2013).
    These are plotted in units of Mercury radii.


    Parameters
    ----------
    ax : pyplot.Axes
        The pyplot axis to add the boundaries to.

    plane : str {`"xy"`, `"xz"`, `"yz"`}, optional
        What plane to project the boundaries to. yz is not yet
        implimented.

    add_legend : bool {`True`, `False`}, optional
        Should pyplot legend labels be added.


    Returns
    -------
    None
    """

    # Plotting magnetopause
    phi = np.linspace(0, 2 * np.pi, 1000)
    rho = sub_solar_magnetopause * (2 / (1 + np.cos(phi))) ** alpha

    magnetopause_x_coords = rho * np.cos(phi)
    magnetopause_y_coords = rho * np.sin(phi)

    L = psi * p

    rho = L / (1 + psi * np.cos(phi))

    bowshock_x_coords = initial_x + rho * np.cos(phi)
    bowshock_y_coords = rho * np.sin(phi)

    # Bow shock functional form creates non-physical points far sunward of Mercury.
    # These are incorrect and must be removed.
    bowshock_y_coords = bowshock_y_coords[bowshock_x_coords < 2]
    bowshock_x_coords = bowshock_x_coords[bowshock_x_coords < 2]

    match plane:
        case "xy":
            bowshock_label = ""
            magnetopause_label = ""

            if add_legend:
                bowshock_label = "Avg. Bowshock (Winslow et al. 2013)"
                magnetopause_label = "Avg. Magnetopause (Winslow et al. 2013)"

            ax.plot(
                magnetopause_x_coords,
                magnetopause_y_coords,
                ls="--",
                lw=lw,
                color=color,
                label=magnetopause_label,
                zorder=zorder,
            )
            ax.plot(
                bowshock_x_coords,
                bowshock_y_coords,
                ls="-",
                lw=lw,
                color=color,
                label=magnetopause_label,
                zorder=zorder,
            )

        case "xz":
            bowshock_label = ""
            magnetopause_label = ""

            if add_legend:
                bowshock_label = "Avg. Bowshock (Winslow et al. 2013)"
                magnetopause_label = "Avg. Magnetopause (Winslow et al. 2013)"

            ax.plot(
                magnetopause_x_coords,
                magnetopause_y_coords,
                ls="--",
                lw=lw,
                color=color,
                label=magnetopause_label,
                zorder=zorder,
            )
            ax.plot(
                bowshock_x_coords,
                bowshock_y_coords,
                ls="-",
                lw=lw,
                color=color,
                zorder=zorder,
                label=bowshock_label,
            )

        case "yz":
            pass
