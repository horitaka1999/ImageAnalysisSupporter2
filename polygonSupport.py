from sympy.geometry import *
from math import sqrt
import numpy as np
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
def rotate(vec,polygonData):
    x,y = vec
    rev = []
    sin = y / sqrt(x**2 + y ** 2)
    cos = x / sqrt(x**2 + y ** 2)
    rotArray = np.array([[cos,sin],[-sin,cos]])
    for i in range(len(polygonData)):
        tmp = np.array(polygonData[i])
        rev.append(list(np.dot(rotArray,tmp.T)))
    return rev



