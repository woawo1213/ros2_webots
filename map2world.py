#!/usr/bin/python3
# -*- coding: utf8 -*-#
# author: jmshin(woawo1213@gmail.com) 22.04.20

from matplotlib.pyplot import axis, box
import numpy as np
import cv2

class WorldDeveloper:
    def __init__(self):
        self.map_obst=[]
        self.img_width = 0
        self.img_height = 0
        self.scale = 0.005
        self.N = 3
        self.map_name='map.png'
        self.main()

    def bucket(self, n, m, pset):
        for p in pset:
            temp_set = set()
            count = 0
            for i in range(n):
                for j in range(m):
                    if (i == 0 and j == 0):
                        continue
                    if (p[0] + i, p[1] + j) in pset:
                        count += 1
                        temp_set.add((p[0] + i, p[1] + j))
            if count == n * m - 1:
                for i in temp_set:
                    pset.remove(i)
        return pset

    def add_bucket(self, pset):
        for i in range(self.N, 0, -1):
            for j in range(self.N, 0, -1):
                if(i == 1 and j == 1):
                    continue
                pset = self.bucket(i, j, pset)
        return pset

    def map_to_world(self,fname):
        img_src = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
        self.img_width, self.img_height = np.array(img_src.shape)
        box_src = np.where(img_src == 0) # 0:black, 205: unknown, 255: free
        box_src=np.array(box_src)

        # compress the osbstacle
        point_set = sorted(set(zip(*box_src)))
        point_set = self.add_bucket(point_set) 

        x_pos,y_pos = zip(*point_set)
        compact_obst=[]
        x_pos=list(x_pos)
        y_pos=list(y_pos)
        compact_obst.append(x_pos)
        compact_obst.append(y_pos)
        compact_obst=np.array(compact_obst)
        box_src = np.array(compact_obst)
        rows, colums = box_src.shape

        self.map_obst.append(colums)
        box_src = np.vstack([box_src, np.zeros(box_src.shape[1])])
        box_src = np.vstack([box_src, np.ones(box_src.shape[1])])
        
        # get translation x,y
        sx = -img_src.shape[0]/2
        sy = -img_src.shape[1]/2
        
        # make H
        H = [[1, 0, 0, sx],
            [0, 1, 0, sy],
            [0, 0, -1, 0],
            [0, 0, 0, 1]]
        H = np.array(H, dtype=float)
        
        map_src = self.scale * H @ box_src
        map_src = np.delete(map_src, 3, 0)
        self.map_obst.append(map_src)
        self.make_world()
        return point_set

    def make_world(self):
        f = open('webots.wbt','w')
        f.write('#VRML_SIM R2022a utf8\n')
        f.write('WorldInfo { \n}\n')
        f.write('Viewpoint { \n  orientation -0.4253 0.6130 0.6657 1.6120 \n  position -1.333 -2.6609 6.3386\n} \n')
        f.write('TexturedBackground {\n} \n')
        f.write('TexturedBackgroundLight {\n} \n')
        f.write('RectangleArena{\n  translation 0 0 0\n  floorSize ')
        w, h = self.img_width * self.scale, self.img_height * self.scale
        f.write("%f " %w)
        f.write("%f " %h)
        f.write('\n} \n')
        for i in range(self.map_obst[0]):
            f.write('SolidBox {\n  translation ')
            x, y, z = self.map_obst[1][:,i]
            f.write("%f " %x)
            f.write("%f " %y)
            f.write("%f " %z)
            f.write('\n  name "box')
            f.write("%d" %i)
            f.write('"\n  size 0.01 0.01 0.1\n  appearance PBRAppearance {\n    baseColor 0 0 0\n  }\n  castShadows FALSE\n}\n')
        f.close()

    def main(self):
        self.map_to_world(self.map_name)


if __name__=='__main__':
    w = WorldDeveloper()