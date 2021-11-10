from sympy.geometry import *
import itertools
def is_valid(p) :
    if p.is_convex() : # 凸多角形の場合
        return True
    if len(p.vertices) != len(set(p.vertices)) : 
        return False
    for (s1,s2) in itertools.combinations(p.sides,2):
        cp = s1.intersection(s2)
        if len(cp) == 0 :
            continue
        if cp[0] in s1.points and cp[0] in s2.points :
            continue
        else :
            return False
    return True

