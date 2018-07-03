# flake8: noqa
"""
$ python p2.py < p2.txt

p2.txt format
n w1 w2 w3 ... wn

e.g.
work = [4, 3, 3]
n = 5
-> 5 4 3 3
"""

import sys
from functools import reduce


def get_minimum_fatigability(work, n):
    for _ in range(n):
        max_work = max(work)
        if max_work == 0:
            break

        update = max_work - 1
        max_work_index = work.index(max_work)
        work[max_work_index] = update

    return reduce(lambda x, y: x + y, map(lambda x: x**2, work))


def run(works, ns):
    for work, n in zip(works, ns):
        min_fatig = get_minimum_fatigability(work, n)
        print(min_fatig)


if __name__ == '__main__':
    works = []
    ns = []
    for line in sys.stdin:
        raw = line.replace('\n', '')
        n, *work = raw.split(' ')

        ns.append(int(n))

        work = list(map(lambda x: int(x), work))
        works.append(work)

    assert len(works) == len(ns)
    run(works, ns)
