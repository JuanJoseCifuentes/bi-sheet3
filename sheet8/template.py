import numpy as np
import pandas as pd
import itertools

# reads in a transaction data file and returns a list of lists.
# Each element in the output list is a transaction. This is a list of items contained in this transaction
def read_database(file):
    db = []
    with open(file) as f:
        lineList = f.readlines()
        for line in lineList:
            line = line.strip()
            li = line.split(" ")
            row = []
            for v in li:
                row.append(v)
            db.append(row)
    return db


# Computes the difference list between list li1 and li2
def diff(li1, li2):
    return [x for x in li1 if not x in li2]


# Computes the set of all subsets (lists) of li
def powerset(li):
    ps = itertools.chain.from_iterable(itertools.combinations(li, r) for r in range(0, len(li) + 1))
    pl = []
    for e in reversed(list(ps)):
        pl.append(list(e))
    return pl
