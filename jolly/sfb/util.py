"""Some utility functions."""
import random
r = random.Random()

def choice(seq):
    if len(seq) == 10:
        return seq[int(r.random() * 6) + int(r.random() * 6)]
    else:
        return seq[int(r.random() * len(seq))]
