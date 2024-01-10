import numpy as np


def polyline_length(pl):
    return np.sum([np.linalg.norm(np.array(pl[k]) - np.array(pl[k + 1])) for k in range(len(pl) - 1)])


def polyline_quantile_coordinate(pl, q):
    pl = np.array(pl)
    d = np.diff(pl, axis=0)
    segdists = np.sqrt((d ** 2).sum(axis=1))
    s = np.cumsum(segdists) / np.sum(segdists)
    s = np.concatenate((np.array([0]), s))

    try:
        i_q = next(i for i, val in enumerate(s) if val >= q)
    except StopIteration:
        i_q = len(s) - 1

    a, b = pl[i_q - 1], pl[i_q]
    q_pl = a + (b - a) * ((q - s[i_q - 1]) / (s[i_q] - s[i_q - 1]))

    return q_pl


def polyline_until_z(pl, z):
    """ return the polyline section starting from height z """
    # TODO : it's approximate
    if np.max(np.array(pl)[:, 2]) <= z:
        i = 0
    else:
        i = next((i for i, pos in enumerate(pl) if pos[2] > z))
    return pl[i:]


def polyline_simplification(pl, n):

    if len(pl) < n:
        return np.array(pl)
    else:
        return np.array([polyline_quantile_coordinate(pl, q) for q in np.linspace(0, 1, n)])
