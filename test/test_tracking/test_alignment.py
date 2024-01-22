import numpy as np

from openalea.phenomenal.tracking.alignment import needleman_wunsch, multi_alignment


def test_needleman_wunsch_alignment():

    seq1 = np.random.random((1, 30, 3))
    seq2 = np.random.random((1, 50, 3))

    rw1 = np.array(needleman_wunsch(seq1, seq2, gap=1e-5))
    rw2 = np.array(needleman_wunsch(seq1, seq2, gap=0.2))
    rw3 = np.array(needleman_wunsch(seq1, seq2, gap=1e5))

    # a lower gap penalty should generate more gaps in the sequences, meaning longer sequences.
    assert len(rw1[0]) > len(rw2[0]) > len(rw3[0])


def test_multi_alignment():

    sequences = [np.random.random((np.random.randint(1, 10), 3)) for _ in range(30)]

    _ = multi_alignment(sequences, gap=0.2)

    _ = multi_alignment(sequences, gap=0.2, align_range=5)

    _ = multi_alignment(sequences, gap=0.2, start=15)













