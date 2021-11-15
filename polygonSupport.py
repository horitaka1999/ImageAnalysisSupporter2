from sympy.geometry import *
from math import sqrt
import cv2
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
def rotate(vec,polygonData,reverse): # 回転して表示する,反転がありならTrue

    min_x = float('inf')
    min_y = float('inf')
    max_x = -float('inf')
    max_y = -float('inf')
    x,y = vec
    rev = []
    sin = y / sqrt(x**2 + y ** 2)
    cos = x / sqrt(x**2 + y ** 2)
    rotArray = np.array([[cos,sin],[-sin,cos]])
    reverseArray = np.array([[-1,0],[0,-1]])
    if reverse:
        rotArray = np.dot(reverseArray,rotArray)
    for i in range(len(polygonData)):
        tmp = np.array(polygonData[i])
        rev.append(list(map(int,list(np.dot(rotArray,tmp.T)))))
    return rev

def fillPolygon(polygonData2):#polygonDataはnp array
    X = polygonData2[:,0]
    Y = polygonData2[:,1]
    minx = np.amin(X)
    miny = np.amin(Y)
    maxx = np.amax(X)
    maxy = np.amax(Y)
    img = np.zeros([(maxy-miny)*2,(maxx-minx)*2],dtype=np.int32)
    points = []
    for i in range(len(polygonData2)):

        fix_y = miny 
        fix_x = minx
        points.append(list((polygonData2[i][0] -fix_x, polygonData2[i][1]-fix_y)))
    cv2.fillConvexPoly(img,np.array([points],dtype = np.int32), 255)
    return np.flipud(img)

def weight(y):
    return sqrt(y)

def calcCost(img):
    score = 0
    for y in range(len(img)):
        for x in range(len(img[0])):
            if img[y][x] == 255:
                score += weight(y)
    return score
                


