import matplotlib.pyplot as plt
import numpy as np
import matplotlib

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
# Avoid Type 3 font http://phyletica.org/matplotlib-fonts/

def format_figure(ax):
    # set tick inwards
    ax.tick_params(direction='in')
    # hide the top and right spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


# from https://qiita.com/hoto17296/items/31e9ea85c6409cb86194
def fill_flag_area(pd, ax, flags, alpha=0.3):
    """ フラグが立っている領域を塗りつぶす
    params:
        ax: Matplotlib の Axes オブジェクト
        flags: index が DatetimeIndex で dtype が bool な pandas.Series オブジェクト
    return:
        Matplotlib の Axes オブジェクト
    """
    diff = pd.Series([0] + list(flags.astype(int)) + [0]).diff().dropna()
    for start, end in zip(flags.index[diff.iloc[:-1] == 1], flags.index[diff.iloc[1:] == -1]):
        ax.axvspan(start, end, alpha=alpha)
    return ax

# from https://stackoverflow.com/questions/13685386/matplotlib-equal-unit-length-with-equal-aspect-ratio-z-axis-is-not-equal-to
def set_axes_equal(ax):
    '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    '''

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5*max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])
