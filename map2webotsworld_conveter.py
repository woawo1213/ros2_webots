#!/usr/bin/python3
# -*- coding: utf8 -*-#
import sys
import cv2
import numpy as np


class Converter:
    def __init__(self):
        self.obj_lists = []
        self.img_width = 0
        self.img_height = 0
        self.scale = 0.05
        self.wall_height = 1.5
        self.map_name = sys.argv[1]
        self.world_name = sys.argv[2]
        self.main()

    def convert_map2webotsworld(self, fname):
        img_src = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
        self.img_height, self.img_width = np.array(img_src.shape)
        black_px = np.where(img_src == 0)  # 0:black, 205: unknown, 255: free
        black_px = np.array(black_px)
        point_set = sorted(set(zip(*black_px)))  # (y,x)

        contour_src = cv2.imread(fname)
        gray = cv2.cvtColor(contour_src, cv2.COLOR_RGB2GRAY)
        contours, hierarchy = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)#find all contours
        contours = contours[:-1] # except img border line

        contour_lists = [] #individual contour lists
        for j in range(len(contours)):
            tmp = []
            for i in range(len(contours[j])):
                con = np.array(contours[j][i][0])
                con = con.tolist()
                tmp.append(tuple(con))
            contour_lists.append(tmp)


        # make transfrom
        sx = -self.img_width / 2
        sy = -self.img_height / 2
        
        dx = [self.scale/2., self.scale/2., -self.scale/2., -self.scale/2.]
        dy = [self.scale/2., -self.scale/2., -self.scale/2., self.scale/2.]

        H = [[1, 0, 0, sx],
             [0, 1, 0, sy],
             [0, 0, 1, 0],
             [0, 0, 0, 1]]
        H = np.array(H, dtype=float)

        # black pixel transform
        blackpx_lists = []
        y_pos, x_pos = zip(*point_set)
        x_pos = list(x_pos)
        y_pos = list(y_pos)
        blackpx_lists.append(x_pos)
        blackpx_lists.append(y_pos)
        blackpx_lists = np.array(blackpx_lists)

        blackpx_lists = np.vstack([blackpx_lists, np.zeros(blackpx_lists.shape[1])])
        blackpx_lists = np.vstack([blackpx_lists, np.ones(blackpx_lists.shape[1])])

        blackpx_trans = self.scale * H @ blackpx_lists
        blackpx_trans = np.delete(blackpx_trans, -1, 0)
        blackpx_trans = np.delete(blackpx_trans, -1, 0)

        #make 4 point lists each black px
        blackpx_trans = np.round(blackpx_trans.astype(np.float64), 4)
        blackpx_trans = set(zip(*blackpx_trans))
        blackpx_trans = list(blackpx_trans)

        bx_4points = []
        bx_4points_set = set()

        for i in blackpx_trans:
            for j in range(4):
                nx = i[0]+dx[j]
                ny = i[1]+dy[j]
                bx_4points.append((nx, ny))

        bx_4points = np.array(bx_4points)
        bx_4points = np.round(bx_4points.astype(np.float64), 4)

        for i in bx_4points:
            x, y = i[0], i[1]
            bx_4points_set.add((x, y))
        bx_4points_set = list(bx_4points_set)

        #contours transform
        cont_4points_list = []
        for contours in contour_lists:
            x_pos, y_pos = zip(*contours)
            contour = []
            x_pos = list(x_pos)
            y_pos = list(y_pos)
            contour.append(x_pos)
            contour.append(y_pos)
            contour = np.array(contour)

            contour = np.vstack([contour, np.zeros(contour.shape[1])])
            contour = np.vstack([contour, np.ones(contour.shape[1])])

            cont_trans = self.scale * H @ contour
            cont_trans = np.delete(cont_trans, -1, 0)
            cont_trans = np.delete(cont_trans, -1, 0)

            cont_trans = np.round(cont_trans.astype(np.float64), 4)

            cont_trans = zip(*cont_trans)
            cont_trans = list(cont_trans)

            cont_4points = []
            for i in cont_trans:
                for j in range(4):
                    nx = i[0]+dx[j]
                    ny = i[1]+dy[j]
                    cont_4points.append((nx, ny))

            cont_4points = np.array(cont_4points)
            cont_4points = np.round(cont_4points.astype(np.float64), 4)

            tmp = []
            for i in cont_4points:
                x, y = i[0], i[1]
                tmp.append((x, y))
            cont_4points_list.append(tmp)

        # 최종 저장 self.obj_lists=[]
        # black pixel의 4 point들의 리스트 셋 bx_4points_set
        # contour 4 point 의 순서 고려한 cont_4points_list
        for o4l in cont_4points_list:
            tmp_obj = []
            for i in range(len(o4l)):
                if o4l[i] in bx_4points_set:
                    if o4l[i] not in tmp_obj:
                        tmp_obj.append(o4l[i])
            self.obj_lists.append(tmp_obj)

        self.write_webotsworld()

    def write_webotsworld(self):
        f = open(self.world_name, 'w')
        f.write('#VRML_SIM R2022a utf8\nWorldInfo{\n}\nViewpoint{\norientation -0.6353 0.0058 0.7721 3.1272\nposition 0.6316 0.1011 2.4908\n}\nTexturedBackground{\n}\nTexturedBackgroundLight{\n}\n')
        world_width, world_height = self.img_width * self.scale, self.img_height * self.scale
        world_size = str(world_width) + " " + str(world_height)
        f.write('Floor{\ntranslation 0 0 0\nsize %s\nappearance Parquetry{type "light strip"}\n}' % world_size)
        
        obj_count = 0
        #make each object
        for obj in self.obj_lists:

            f.write('\nSolid {\nchildren [\nShape {\nappearance PBRAppearance {\nbaseColor 1 1 1\nbaseColorMap ImageTexture {\nurl [\n"https://wallha.com/wallpaper/grey-gray-filter-578430"\n]\n}\n}\ngeometry DEF IFS IndexedFaceSet {\ncoord Coordinate{\npoint[\n ')
            # lower side coordiante points
            for i in range(len(obj)):
                x, y = obj[i][0], obj[i][1]
                lside = str(x) + " " + str(y) + " 0 "
                f.write('%s' % lside)
            
            # upper side coordiante points
            for i in range(len(obj)):
                x, y = obj[i][0], obj[i][1]
                uside = str(x) + " " + str(y) + " 1.0 "
                f.write('%s' % uside)
            f.write(']\n} coordIndex [\n')

            #make lower side plane
            for fnode in range(len(obj)):
                f.write("%d, " % fnode)
            f.write("-1 ")

            #make upper side plane
            for cnode in range(len(obj)):
                cnode += len(obj)
                f.write("%d, " % cnode)
            f.write("-1 ")

            # make wall plane
            for wall in range(len(obj)-1):
                plane = str(wall)+", "+str(wall+1)+", "+str(wall+1+len(obj))+", "+str(wall+len(obj))+", -1 "
                f.write("%s" % plane)

            final = str(len(obj)-1)+", "+str(0)+", " + str(0+len(obj))+", "+str(1+len(obj)*2)+", -1 "
            f.write("%s" % final)
            f.write('\n]\n}\n ')
            f.write('castShadows FALSE\n}\n]\nname "solid%d"\n}' %obj_count)
            obj_count += 1

        f.close()

    def main(self):
        self.convert_map2webotsworld(self.map_name)


if __name__ == '__main__':
    Converter()
