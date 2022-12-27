import math
from fractions import Fraction as F
import networkx as nx
from itertools import count, takewhile

def frac_to_ver(p, q=None, base=2):
    if type(p) == F and q is None:
        p, q = p.numerator, p.denominator
    occurs = dict()
    pos = 0
    current = []
    while p not in occurs:
        occurs[p] = pos
        z = (base*p)//q
        p = base*p - z*q
        if z == base:
            return current, [base-1]
        if p == 0:
            if z != 0:
                current.append(z)
            return (current, [])
        current.append(z)
        pos += 1

    return (current[:occurs[p]], current[occurs[p]:])


def horner(l, base=2):
    x = F(0)
    for c in l:
        x = x * base + c
    
    return x


def ver_to_frac(ver, base=2):
    t, r = ver

    nt = len(t)
    nr = len(r)
    x = 0 if nr == 0 else horner(r) / (base**nr - 1) / (base**nt)
    y = horner(t) / base**nt

    return x + y


def difficulty(p, q=None, base=2):
    t, r = frac_to_ver(p, q, base)
    return len(t) + len(r)


class Node:
    def __init__(self, v, left=None, right=None, info=None):
        self.v = v  # The node value (float/int/str)
        self.left = left    # Left child
        self.right = right  # Right child
        self.info = info
    
    def __repr__(self):
        if self.right is None and self.left is None:
            return f"Leaf({self.info})"
        else:
            return f"Node({self.v}, {self.left}, {self.right})"


def get_splitter_tree(ratios):
    B = [Node(f, info=i) for i, f in enumerate(ratios)]

    while len(B) >= 2:
        k = len(B)
        i, j, c = min([
            (i, j, difficulty(B[i].v / (B[i].v + B[j].v)))
              for i in range(k)
              for j in range(i+1, k)
            ], key=lambda x: x[2])

        left = B[i]
        right = B[j]

        assert i < j
        B = B[:i] + B[i+1:j] + B[j+1:] + [Node(left.v+right.v, left, right, c)]
    return next(iter(B))

def continued(r):
    i = math.floor(r)
    f = r - i
    
    if f == 0:
        return [i]
    
    return [i] + continued(1/f)

def float_to_frac(r):
    
    a = iter(reversed(list(takewhile(lambda x: x < 10000, continued(F(r))))))
    
    x = F(next(a))
    for y in a:
        x = y + 1/x
    
    return x
