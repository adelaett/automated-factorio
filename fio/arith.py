from dataclasses import dataclass
import math
from fractions import Fraction as F
from itertools import takewhile
from turtle import right

def frac_to_ver(p: int|F, q: int|None=None, base: int=2) -> tuple[list[int], list[int]]:
    if type(p) == F and q is None:
        p, q = p.numerator, p.denominator
    elif type(p) == int and type(q) == int:
        pass
    else:
        raise TypeError("Wrong type")

    occurs: dict[int, int] = dict()
    pos = 0
    current: list[int] = []
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


def horner(l: list[int], base:int=2) -> F:
    x = F(0)
    for c in l:
        x = x * base + c
    
    return x


def ver_to_frac(ver: tuple[list[int], list[int]], base: int=2):
    t, r = ver

    nt = len(t)
    nr = len(r)
    x = 0 if nr == 0 else horner(r) / (base**nr - 1) / (base**nt)
    y: F = horner(t) / base**nt

    return x + y


def difficulty(p: int|F, q:int|None=None, base: int=2):
    t, r = frac_to_ver(p, q, base)
    return len(t) + len(r)

def continued(r: F) -> list[int]:
    i = math.floor(r)
    f = r - i
    
    if f == 0:
        return [i]
    
    return [i] + continued(1/f)

def float_to_frac(r: float)-> F:

  integral = int(math.floor(r))

  r = r - integral

  a = iter(reversed(list(takewhile(lambda x: x < 1000, continued(F.from_float(r))))))
  
  fractionnal = F(next(a), 1)
  for y in a:
    fractionnal = y + 1/fractionnal
  
  return integral + fractionnal

@dataclass
class Node:
    v: int
    right: Node | None
    left: Node | None
    info: str | None
    
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