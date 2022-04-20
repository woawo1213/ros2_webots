#!/usr/bin/python3
# -*- coding: utf8 -*-#
#
from matplotlib.pyplot import box
import numpy as np
import cv2
from squaternion import Quaternion

def convert(fname):
    # read img & find box 
    img_src=cv2.imread(fname,cv2.IMREAD_GRAYSCALE)
    box_src=np.where(img_src==0)
    box_src=np.array(box_src)
    box_src=np.vstack([box_src,np.zeros(box_src.shape[1])])
    box_src=np.vstack([box_src,np.ones(box_src.shape[1])])
    print(box_src)
    
    # get translation x,y
    sx=-img_src.shape[0]/2
    sy=-img_src.shape[1]/2
    # make H
    H=[[1, 0, 0, sx],
       [0,-1, 0, sy],
       [0, 0,-1, 0],
       [0, 0, 0, 1]]
    H=np.array(H,dtype=float)
    print(H)
    
    scale=0.005
    map_src=scale*H@box_src
    map_src=np.delete(map_src,3,0)
    print(map_src)

def make_world():
    f=open('webots.wbt','w')
    f.write('#VRML_SIM R2022a utf8\n')
    f.write('WorldInfo { \n}\n')
    f.write('Viewpoint { \n  orientation -0.4253 0.6130 0.6657 1.6120 \n  position -0.7834 -1.1892 2.9465\n} \n')
    f.write('TexturedBackground {\n} \n')
    f.write('TexturedBackgroundLight {\n} \n')
    f.write('RectangleArena{\n  translation -0.01 0 -0.05\n  floorSize 1.5 1.5\n} \n')
    for i in range(1000):
        f.write('SolidBox {\n  translation 0 0 0\n')
        f.write('  name "box')
        f.write("%d" %i)
        f.write('"\n  size 0.05 0.05 0.1\n  appearance PBRAppearance {\n    baseColor 0 0 0\n  }\n}\n')
    
    f.close()

def main():
    convert('map.png')
    make_world()


if __name__=='__main__':
    main()