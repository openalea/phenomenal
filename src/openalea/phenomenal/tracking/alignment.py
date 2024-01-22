""" Multiple sequence alignment """

import numpy as np
from copy import deepcopy


def needleman_wunsch(X, Y, gap, gap_extremity_factor=1.):
    """
    Performs pairwise alignment of profiles X and Y with Needleman-Wunsch algorithm.
    A profile is defined as an array of one or more sequences of the same length.
    Each sequence includes one or several vectors of the same length, and might contain gaps (vectors filled with NaN)
    Source code : https://gist.github.com/slowkow/06c6dba9180d013dfd82bec217d22eb5
    The source code was modified to correct a few errors, and adapted to fit all requirements (extremity gap,
    customized scoring function, etc.)

    Parameters
    ----------
    X : array of shape (profile length, sequence length, vector length)
        profile 1
    Y : array of shape (profile length, sequence length, vector length)
        profile 2
    gap : float
        gap penalty parameter
    gap_extremity_factor : float
        optional factor to increase/decrease gap penalty on sequence extremities

    Returns
    -------
    (list, list)
    """

    if X.size == 0 and Y.size == 0:
        rx, ry = [], []
        return rx, ry

    gap_extremity = gap * gap_extremity_factor

    nx = X.shape[1]
    ny = Y.shape[1]

    # Optimal score at each possible pair of characters.
    F = np.zeros((nx + 1, ny + 1))
    F[:, 0] = np.linspace(start=0, stop=-nx*gap_extremity, num=nx+1)
    F[0, :] = np.linspace(start=0, stop=-ny*gap_extremity, num=ny+1)

    # Pointers to trace through an optimal alignment.
    P = np.zeros((nx + 1, ny + 1))
    P[:, 0] = 3
    P[0, :] = 4

    # Temporary scores.
    t = np.zeros(3)
    for i in range(nx):
        for j in range(ny):

            # TODO : gap argument should be useless ?
            t[0] = F[i, j] - alignment_score(X[:, i, :], Y[:, j, :], gap_extremity)

            if j + 1 == ny:
                t[1] = F[i, j + 1] - gap_extremity
            else:
                t[1] = F[i, j + 1] - gap

            if i + 1 == nx:
                t[2] = F[i + 1, j] - gap_extremity
            else:
                t[2] = F[i + 1, j] - gap

            tmax = np.max(t)
            F[i + 1, j + 1] = tmax
            if t[0] == tmax:
                P[i + 1, j + 1] += 2
            if t[1] == tmax:
                P[i + 1, j + 1] += 3
            if t[2] == tmax:
                P[i + 1, j + 1] += 4

    # Trace through an optimal alignment.
    i, j = nx, ny

    rx, ry = [], []
    condition = True
    while condition:
        if P[i, j] in [2, 5, 6, 9]:
            rx.append(i - 1)
            ry.append(j - 1)
            i -= 1
            j -= 1
        elif P[i, j] in [3, 5, 7, 9]:
            rx.append(i - 1)
            ry.append(-1)  # gap
            i -= 1
        elif P[i, j] in [4, 6, 7, 9]:
            rx.append(-1)  # gap
            ry.append(j - 1)
            j -= 1

        condition = i > 0 or j > 0

    rx = rx[::-1]
    ry = ry[::-1]

    return rx, ry


def scoring_function(vec1, vec2):
    """
    Compute a dissimilarity score between two vectors of same length, which is equal to their euclidian distance.

    Parameters
    ----------
    vec1 : 1D array
    vec2 : 1D array, of same length than vec1

    Returns
    -------
    float
    """

    return np.linalg.norm(vec1 - vec2)


def alignment_score(x, y, gap_extremity):
    """

    Compute a dissimilarity score between two arrays of vectors x and y.
    x and y can have different lengths, but all vectors in x and y must have the same length.

    Parameters
    ----------
    x : 2D array
        size (number of vectors, vector length)
    y : 2D array
        size (number of vectors, vector length)
    gap_extremity : float

    Returns
    -------
    float

    """

    # list of scores for each pair of vectors xvec and yvec,
    # with xvec and yvec being non-gap elements of x and y respectively.
    score = []
    for xvec in x:
        for yvec in y:
            if not all(np.isnan(xvec)) and not all(np.isnan(yvec)):
                score.append(scoring_function(xvec, yvec))

    if score:
        score = np.mean(score)
    else:
        score = gap_extremity  # TODO : hack

    return score


def insert_gaps(all_sequences, seq_indexes, alignment):
    """
    Add gaps in sequences of 'all_sequences' whose indexes is in 'seq_indexes'. A gap is defined as a NAN array element
    in a given sequence. Gaps positions are given by 'alignment'.

    Parameters
    ----------
    all_sequences : list(2D array)
    seq_indexes : list(int)
    alignment : list(int)
        result from needleman_wunsch()

    Returns
    -------
    """

    all_sequences2 = deepcopy(all_sequences)
    gap_indexes = [i for i, e in enumerate(alignment) if e == -1]

    vec_len = max([len(vec) for seq in all_sequences for vec in seq])

    for si in seq_indexes:
        for gi in gap_indexes:

            if all_sequences2[si].size == 0:
                all_sequences2[si] = np.full((1, vec_len), np.NAN)
            else:
                all_sequences2[si] = np.insert(all_sequences2[si], gi, np.NAN, 0)

    return all_sequences2


def multi_alignment(sequences, gap, gap_extremity_factor=1., start=0, align_range=None):
    """
    Multiple sequence alignment algorithm to align n sequences, using a progressive method. At each step, a sequence (Y)
    is aligned with a matrix (X) corresponding to a profile (i.e. the alignement of k sequences) resulting in the
    alignment of k + 1 sequences. Each pairwise alignment of X vs Y is based on needleman-wunsch algorithm.

    Parameters
    ----------
    sequences : list of 2D arrays
        The list of sequences to align
    gap : float
        penalty parameter to add a gap
    gap_extremity_factor : float
        parameter to modify the gap penalty on sequence extremity positions, relatively to gap value.
        For example, if gap = 5 and gap_extremity_factor = 0.6, Then the penalty for terminal gaps equals 3.
    start : int
        sequences are progressively added to the global alignment from sequences[start] to sequences[0], then from
        sequences[start + 1] to sequences[-1]
    align_range : int
        When adding a new sequence to the global alignment, only the already aligned sequences with a distance inferior
        or equal to this parameter in the sequences order are used for the alignment.

    Returns
    -------
    """

    assert(-1 <= start <= len(sequences) - 1)

    aligned_sequences = deepcopy(sequences)

    # init
    # (k_start -> 0) then (k_start -> n)
    k_start = len(aligned_sequences) - 1 if start == -1 else start
    alignment_order = np.array(list(range(0, k_start + 1)[::-1]) + list(range(k_start + 1, len(aligned_sequences))))
    for k in range(1, len(aligned_sequences)):
        xi = alignment_order[:k]  # ref
        yi = alignment_order[k]

        # select the 2 profiles to align
        xi_in_range = xi if align_range is None else [val for val in xi if abs(val - k) <= align_range]
        X = np.array([aligned_sequences[i] for i in xi_in_range])
        Y = np.array([aligned_sequences[yi]])

        # alignment
        rx, ry = needleman_wunsch(X, Y, gap, gap_extremity_factor=gap_extremity_factor)

        # update all sequences from sq0 to sq yi
        aligned_sequences = insert_gaps(aligned_sequences, xi, rx)  # xi = sequences that all have already been aligned
        aligned_sequences = insert_gaps(aligned_sequences, [yi], ry)

    # convert list of aligned sequences (all having the same length) in a matrix of vector indexes (-1 = gap)
    s = np.array(aligned_sequences).shape
    alignment_matrix = np.full((s[0], s[1]), -1)
    for i, aligned_seq in enumerate(aligned_sequences):
        no_gap = np.array([not all(np.isnan(e)) for e in aligned_seq])
        alignment_matrix[i][no_gap] = np.arange(sum(no_gap))

    return alignment_matrix
