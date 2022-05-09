import cv2
import numpy as np
import random
src = cv2.imread("map_.png")

gray = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)

contours, hierarchy = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

contours=contours[:-1]
print(len(contours))

contour_list=[]
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
    contour_list.append(tmp)
    print("contour list\n",tmp)
    print("center\n",center)

print(contour_list[0])
print(contour_list[1])

obj=[]
# obj.append(center)
# print(center)
obj.append(tmp)
# print(obj)
for i in contours:
    color=(random.randint(0,256),random.randint(0,256),random.randint(0,256))
    img=cv2.drawContours(src, [i], -1, color,0)
    # print("length contours:",len(i))
    cnt+=1

# print(cnt)

cv2.imshow("src", img)
cv2.waitKey(0)
cv2.destroyAllWindows()