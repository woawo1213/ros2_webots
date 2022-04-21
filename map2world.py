#!/usr/bin/python3
# -*- coding: utf8 -*-#
#
import numpy as np
import cv2

val=[]

def convert(fname):
    # read img & find box 
    img_src = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
    box_src = np.where(img_src == 0)
    box_src = np.array(box_src)
    box_src = np.vstack([box_src, np.zeros(box_src.shape[1])])
    box_src = np.vstack([box_src, np.ones(box_src.shape[1])])
    rows, colums = box_src.shape
    val.append(colums)
    
    # get translation x,y
    sx = -img_src.shape[0]/2
    sy = -img_src.shape[1]/2
    # make H
    H = [[1, 0, 0, sx],
         [0,-1, 0, sy],
         [0, 0,-1, 0],
         [0, 0, 0, 1]]
    H = np.array(H, dtype=float)
    
    scale = 0.005
    map_src = scale * H @ box_src
    map_src = np.delete(map_src, 3, 0)
    val.append(map_src)
    make_world()
    # print(map_src)

def make_world():
    f = open('webots.wbt','w')
    f.write('#VRML_SIM R2022a utf8\n')
    f.write('WorldInfo { \n}\n')
    f.write('Viewpoint { \n  orientation -0.4253 0.6130 0.6657 1.6120 \n  position -1.333 -2.6609 6.3386\n} \n')
    f.write('TexturedBackground {\n} \n')
    f.write('TexturedBackgroundLight {\n} \n')
    f.write('RectangleArena{\n  translation 0 0 0\n  floorSize 1.5 1.5\n} \n')
    for i in range(val[0]):
        f.write('SolidBox {\n  translation ')
        x, y, z = val[1][:,i]
        f.write("%f " %x)
        f.write("%f " %y)
        f.write("%f " %z)
        f.write('\n  name "box')
        f.write("%d" %i)
        f.write('"\n  size 0.005 0.005 0.1\n  appearance PBRAppearance {\n    baseColor 0 0 0\n  }\n  castShadows FALSE\n}\n')
    f.close()

def main():
    convert('map.png')

if __name__=='__main__':
    main()