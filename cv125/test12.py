import cv2
import numpy as np
import math
import requests
import threading
import bluetooth
import time
preState = ''
def nothing(x):
    pass

cap = cv2.VideoCapture('http://192.168.43.1:8080/video')
if cap.isOpened()== False:
    print("Error opening video stream or file")
i = 0
minLineLength = 100 # 아무것도 아님
maxLineGap = 10 # 아무것도 아님
cols, rows = 0,0 # 가로세로
trap_bottom_width = 0.85 # 아무것도 아님
trap_top_width = 0.07 # 아무것도 아님
trap_height = 0.4 # 아무것도 아님
state = 'Go -500' # 상태
cv2.namedWindow('asdf')
cv2.createTrackbar('x','asdf',0,1000,nothing)
cv2.createTrackbar('y','asdf',0,1000,nothing)
flag = 0
Uflag = 0
UPointflag = 0
Lflag = 0
LPointflag = 0
dhlsFlag = 0
dhFlag = 0
angleState = 0
anglePre = 0
preTime = 0
LXflag = 0
RXflag = 0
while(cap.isOpened()):
    ret, img = cap.read()
    if ret == True:
        flag = 0
        img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_LINEAR)
        cols, rows = img.shape[:2]
        x = cv2.getTrackbarPos('x','asdf')
        y = cv2.getTrackbarPos('y','asdf')
        cv2.circle(img,(x,y),2,(0,0,0),1,1)
        print(img[y, x])
        for i in range(int(cols / 2 - 100)):
            for j in range(int(rows / 2 - 100), int(rows / 2 + 100)):
                if img[i,j,0] < 80 and img[i,j,1] < 70 and img[i,j,2] > 70:
                    cv2.putText(img,'Yellow',(j,i),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
                if img[i,j,0] < 70 and img[i,j,1] > 80 and img[i,j,2] < 40:
                    cv2.putText(img, 'Green', (j, i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
        #출력 부분
        cv2.imshow('img2',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print('안됨')
        break
cap.release()
cv2.destroyAllWindows()