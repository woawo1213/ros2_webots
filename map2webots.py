#!/usr/bin/python3
# -*- coding: utf8 -*-#
import time
import numpy as np
import cv2


class MapConverter:
    def __init__(self):
        self.map_obst=[]
        self.obj_list=[]
        self.img_width = 0
        self.img_height = 0
        self.scale = 0.005
        self.map_name='map.png'
        self.world_name='webots.wbt'
        self.main()


    def map_to_world(self,fname):
        img_src = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
        self.img_width, self.img_height = np.array(img_src.shape)
        black_px = np.where(img_src == 0) # 0:black, 205: unknown, 255: free
        black_px=np.array(black_px) 
        point_set = sorted(set(zip(*black_px)))#(y,x)
        print("point_set\n",point_set)

        contour_src=cv2.imread(fname)
        gray=cv2.cvtColor(contour_src,cv2.COLOR_RGB2GRAY)
        contours, hierarchy = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contours=contours[:-1]


        contours_lists=[]
        for j in range(len(contours)):
            tmp=[]
            cnt=0
            center=(0,0)
            for i in range(len(contours[j])):
                
                a=np.array(contours[j][i][0])
                a=a.tolist()
                tmp.append(tuple(a))
                # cnt=contours[j]
                # M=cv2.moments(cnt)
                # cx = int(M['m10']/M['m00'])
                # cy = int(M['m01']/M['m00'])
                # center=(cx,cy)
            contours_lists.append(tmp)
            # print("contour list\n",tmp)
            # print("center\n",center)
        print("contour list\n",contours_lists)



        y_pos,x_pos = zip(*point_set)
        # x_pos,y_pos = zip(*con_list)
        # x_pos,y_pos = zip(*concent)
        compact_obst=[]
        x_pos=list(x_pos)
        y_pos=list(y_pos)
        compact_obst.append(x_pos)
        compact_obst.append(y_pos)
        compact_obst=np.array(compact_obst)
        # print(compact_obst)
        

        rows, colums = compact_obst.shape
        self.map_obst.append(colums)
        compact_obst = np.vstack([compact_obst, np.zeros(compact_obst.shape[1])])
        compact_obst = np.vstack([compact_obst, np.ones(compact_obst.shape[1])])
        
        # get translation x,y
        sx = -self.img_width / 2
        sy = -self.img_height / 2
        
        # make H
        H = [[1, 0, 0, sx],
            [0, 1, 0, sy],
            [0, 0, -1, 0],
            [0, 0, 0, 1]]
        H = np.array(H, dtype=float)
        
        map_src = self.scale * H @ compact_obst
        map_src = np.delete(map_src, -1, 0)
        map_src_ = np.delete(map_src, -1, 0)
        
        self.map_obst.append(map_src)

        #make 4 angle point
        dx=[-0.0025, -0.0025, 0.0025, 0.0025]
        dy=[0.0025, -0.0025, -0.0025, 0.0025]
        map_src_ = np.round(map_src_.astype(np.float64),4)
        map_src_=set(zip(*map_src_))
        map_src_=list(map_src_)
        print("map_src_\n",map_src_)# transfom 한 좌표들

        bx_4angle_list=[]
        bx_4angle_set=set()
        for i in map_src_:
            for j in range(4):            
                nx=i[0]+dx[j]
                ny=i[1]+dy[j]
                bx_4angle_list.append((nx,ny))

        bx_4angle_list=np.array(bx_4angle_list)
        bx_4angle_list=np.round(bx_4angle_list.astype(np.float64),4)
        # print(bx_4angle_list)

        for i in bx_4angle_list:
            x,y=i[0],i[1]
            bx_4angle_set.add((x,y))
        bx_4angle_set=list(bx_4angle_set)
        print("bx_4angle_set\n",bx_4angle_set)# transform 한 검은 픽셀의 4코너 좌표의 전체 리스트
        print("########################")


        #contour 좌표 변환
        obj_4angle_list=[]
        for contour in contours_lists:
            print("contour\n",contour)
            x_pos,y_pos = zip(*contour)
            # x_pos,y_pos = zip(*con_list)
            # x_pos,y_pos = zip(*concent)
            contour_obst=[]
            x_pos=list(x_pos)
            y_pos=list(y_pos)
            contour_obst.append(x_pos)
            contour_obst.append(y_pos)
            contour_obst=np.array(contour_obst)
            # print(contour_obst)
            

            # rows, colums = contour_obst.shape
            # self.map_obst.append(colums)
            contour_obst = np.vstack([contour_obst, np.zeros(contour_obst.shape[1])])
            contour_obst = np.vstack([contour_obst, np.ones(contour_obst.shape[1])])
            
            # get translation x,y
            sx = -self.img_width / 2
            sy = -self.img_height / 2
            
            # make H
            H = [[1, 0, 0, sx],
                [0, 1, 0, sy],
                [0, 0, -1, 0],
                [0, 0, 0, 1]]
            H = np.array(H, dtype=float)
            
            cont_src = self.scale * H @ contour_obst
            cont_src = np.delete(cont_src, -1, 0)
            cont_src_ = np.delete(cont_src, -1, 0)
            
            # self.map_obst.append(cont_src)

            #make 4 angle point
            dx=[-0.0025, 0.0025, 0.0025, -0.0025]
            dy=[0.0025, 0.0025, -0.0025, -0.0025]
            cont_src_ = np.round(cont_src_.astype(np.float64),4)

            cont_src_=zip(*cont_src_)
            cont_src_=list(cont_src_)
            print("cont_src_\n",cont_src_)# transfom 한 좌표들

            cont_4angle_list=[]
            # cont_4angle_set=set()
            for i in cont_src_:
                for j in range(4):            
                    nx=i[0]+dx[j]
                    ny=i[1]+dy[j]
                    cont_4angle_list.append((nx,ny))

            cont_4angle_list=np.array(cont_4angle_list)
            cont_4angle_list=np.round(cont_4angle_list.astype(np.float64),4)
            print("cont_4angle_list\n",len(cont_4angle_list))


            
            tmp=[]
            for i in cont_4angle_list:
                x,y=i[0],i[1]
                tmp.append((x,y))
            # cont_4angle_set=list(cont_4angle_set)
            obj_4angle_list.append(tmp)

        print("obj_4angle_list\n",len(obj_4angle_list))


        # 최종 저장 self.obj_list=[]
        # 까만 점의 4꼭지들의 리스트 셋 bx_4angle_set
        # contour obj 4angle list 순서 고려 obj_4angle_list
        for o4l in obj_4angle_list:
            tmp_obj=[]
            for i in range(len(o4l)):
                if o4l[i] in bx_4angle_set:
                    if o4l[i] not in tmp_obj:
                        tmp_obj.append(o4l[i])
            self.obj_list.append(tmp_obj)

        # for i in range(len(self.obj_list)):
        #     print(len(self.obj_list[i]))
        # print((self.obj_list[1]))

        # print(self.obj_list)
















        self.make_world()

    def make_world(self):
        f = open(self.world_name,'w')
        f.write('#VRML_SIM R2022a utf8\nWorldInfo { \n}\nViewpoint { \n  orientation -0.6353 0.0058 0.7721 3.1272 \n  position 0.6316 0.1011 2.4908\n} \nTexturedBackground {\n} \nTexturedBackgroundLight {\n} \n')
        w, h = self.img_width * self.scale, self.img_height * self.scale
        img_size = str(w) + " " + str(h)
        f.write('Floor{\n  translation 0 0 0\n  size %s\n} \n' %img_size)
        f.write('Solid {\n  children [\n    Shape {\n      appearance PBRAppearance {\n        baseColor 0 0 0\n      }\n      geometry DEF IFS IndexedFaceSet {\n          coord Coordinate{\n     }\n       coordIndex [\n      ]\n  }\n  castShadows FALSE\n  }\n]  \n}')
        for i in range(self.map_obst[0]):
            x, y, z = self.map_obst[1][:,i]
            box_w = self.scale * 1
            box_h = self.scale * 1
            position = str(x) + " " + str(y) + " " + str(z)
            box_size = str(box_w) + " " + str(box_h)
            f.write('SolidBox {\n  translation ')
            f.write("%f " %x)
            f.write("%f " %y)
            f.write("%f " %z)
            f.write('\n  name "box%d' %i)
            f.write('"\n  size %s' %box_size)            
            f.write(' 0.03\n  appearance PBRAppearance {\n    baseColor 0 0 0\n  }\n  castShadows FALSE\n}\n')
        f.close()

    def main(self):
        self.map_to_world(self.map_name)

if __name__=='__main__':
    w = MapConverter()