#!/usr/bin/python3
# -*- coding: utf8 -*-#

import numpy as np
import cv2
class WorldDeveloper:
    def __init__(self):
        self.map_obst=[]
        self.world_obst={}
        self.resize_dict={}
        self.img_width = 0
        self.img_height = 0
        self.scale = 0.005
        self.N = 2
        self.map_name='map_.png'
        self.world_name='webots.wbt'
        self.main()

    def bucket(self, n, m, pset):
        for p in pset:
            temp_set = set()
            count = 0
            for i in range(n):
                for j in range(m):
                    if (i==0 and j==0):
                        continue
                    if (p[0] + i, p[1] + j) in pset:
                        count += 1
                        temp_set.add((p[0] + i, p[1] + j))
            if count == n * m - 1:
                size_w = 0.01 * n
                size_h = 0.01 * m
                for i in temp_set:
                    pset.remove(i)
                x = p[0]
                y = p[1]
                self.world_obst[(x,y)] = (size_w,size_h)
        return pset

    def add_bucket(self, pset):
        bucket_list=[]
        for i in range(self.N, 0, -1):
            for j in range(self.N, 0, -1):
                bucket_list.append((i,j))
        bucket_list = sorted(bucket_list, key = lambda x : x[0] * x[1], reverse = True)
        for i in bucket_list:
            if(i[0] == 1 and i[1] == 1):
                continue
            pset = self.bucket(i[0], i[1], pset)
        return pset

    def map_to_world(self,fname):
        img_src = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
        self.img_width, self.img_height = np.array(img_src.shape)
        black_px = np.where(img_src == 0) # 0:black, 205: unknown, 255: free
        black_px=np.array(black_px)


        # compress the osbstacle
        point_set = sorted(set(zip(*black_px)))
        point_set = self.add_bucket(point_set) 

        # for dict
        ox_pos,oy_pos=zip(*list(self.world_obst.keys()))
        val=list(self.world_obst.values())
        bucket_obst=[]
        ox_pos=list(ox_pos)
        oy_pos=list(oy_pos)
        bucket_obst.append(ox_pos)
        bucket_obst.append(oy_pos)
        bucket_obst = np.array(bucket_obst)
        resize_bucket = np.array(bucket_obst)
        resize_bucket = np.vstack([resize_bucket, np.zeros(resize_bucket.shape[1])])
        resize_bucket = np.vstack([resize_bucket, np.ones(resize_bucket.shape[1])])

        # for all
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

        resize_src = self.scale * H @ resize_bucket
        resize_src=np.delete(resize_src,3,0)
        resize_keys=[]
        for i in range(len(ox_pos)):
            resize_keys.append((np.around(resize_src[0][i],4),np.around(resize_src[1][i],4)))
        
        self.resize_dict=dict(zip(resize_keys,val))
        self.map_obst.append(map_src)
        self.make_world()

    def make_world(self):
        f = open(self.world_name,'w')
        f.write('#VRML_SIM R2022a utf8\n')
        f.write('WorldInfo { \n}\n')
        f.write('Viewpoint { \n  orientation -0.4253 0.6130 0.6657 1.6120 \n  position -1.333 -2.6609 6.3386\n} \n')
        f.write('TexturedBackground {\n} \n')
        f.write('TexturedBackgroundLight {\n} \n')
        f.write('Floor{\n  translation 0 0 0\n  size ')
        w, h = self.img_width * self.scale, self.img_height * self.scale
        f.write("%f " %w)
        f.write("%f " %h)
        f.write('\n} \n')
        for i in range(self.map_obst[0]):
            f.write('SolidBox {\n  translation ')
            x, y, z = self.map_obst[1][:,i]
            if((x,y) in self.resize_dict.keys()):
                box_w = self.resize_dict.get((x,y))[0]
                box_h = self.resize_dict.get((x,y))[1]
            else:
                box_w = 0.01
                box_h = 0.01
            f.write("%f " %x)
            f.write("%f " %y)
            f.write("%f " %z)
            f.write('\n  name "box')
            f.write("%d" %i)
            f.write('"\n  size ')
            f.write("%f " %box_w)
            f.write("%f " %box_h)
            f.write('0.03\n  appearance PBRAppearance {\n    baseColor 0 0 0\n  }\n  castShadows FALSE\n}\n')
        f.close()

    def main(self):
        self.map_to_world(self.map_name)


if __name__=='__main__':
    w = WorldDeveloper()