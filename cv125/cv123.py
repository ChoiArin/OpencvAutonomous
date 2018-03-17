import cv2
import numpy as np
import math
import requests
import threading
import bluetooth
import time
preState = ''
cap = cv2.VideoCapture('http://192.168.43.1:8080/video')
if cap.isOpened()== False:
    print("Error opening video stream or file")
serverMACAddress = 'CC:78:AB:26:50:CE'
port = 3
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s.connect((serverMACAddress, port))
i = 0
minLineLength = 100 # 아무것도 아님
maxLineGap = 10 # 아무것도 아님
cols, rows = 0,0 # 가로세로
trap_bottom_width = 0.85 # 아무것도 아님
trap_top_width = 0.07 # 아무것도 아님
trap_height = 0.4 # 아무것도 아님
state = 'Go -500' # 상태
s.send(state)
time.sleep(0.1)
s.send('angle 0')
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
interflag = 1
greenflag = 0
angleAdd = 0
angleAddd = 0
leftflag = 0
interTime = 99999
leftTime = 9999
while(cap.isOpened()):
    ret, img = cap.read()
    if ret == True:
        print(state)
        print(angleState)
        img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_LINEAR)
        cols, rows = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray,100,150,apertureSize=3)
        #방지턱 검출
        if img[int(cols / 2), int(rows / 2), 0] < 70 and img[int(cols / 2), int(rows / 2), 1] > 80 and img[int(cols / 2), int(rows / 2), 2] < 40:
            greenflag = 1
        #방해물 검출
        if img[10, int(rows / 2), 0] > 20 and img[10, int(rows / 2), 1] < 20 and img[10, int(rows / 2), 2] < 30:
            interTime = 0
            s.send('angle 70')
            angleState += 70
            interTime = time.time()
        '''if interflag == 1 and time.time()-interTime > 1:
            s.send('angle '+str(angleState * -1))
            interTime = 99999'''
        #표지판 검출
        cimg = cv2.GaussianBlur(gray, (3, 3), 0)
        circles = cv2.HoughCircles(cimg, cv2.HOUGH_GRADIENT, 1, 30,
                                   param1=50, param2=70, minRadius=20, maxRadius=0)
        if type(circles) != type(None):
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                # draw the outer circle
                if i[1] + int(i[2] / 3) > cols or i[0] - int(i[2] / 3) < 0:
                    continue
                elif abs(int(img[i[1], i[0], 0]) - int(img[i[1] + int(i[2] / 3), i[0] - int(i[2] / 3), 0])) > 17 and Uflag == 0 and leftflag == 0:
                    cv2.putText(img, 'U', (i[0], i[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
                    print('U턴')
                    state = 'Uturn'
                    Uflag = 1
                    interflag = 1
                elif Uflag == 0 and Lflag == 0 and leftflag == 0:
                    cv2.putText(img, 'LEFT', (i[0], i[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
                    print('좌회전')
                    state = 'Lturn'
                    Lflag = 1
                    interflag = 1
                    leftTime = time.time()
                    s.send('angle 80')
                cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
                # draw the center of the circle
                cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
        #길 검출
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
        if type(lines) != type(None):
            max1 = 123456789
            max1_list = []
            max2 = 123456789
            max2_list = []
            max_y = 0
            max_y_list = []
            for i in range(len(lines)):
                for rho, theta in lines[i]:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    x1 = int(x0 + 1000 * (-b))
                    y1 = int(y0 + 1000 * (a))
                    x2 = int(x0 - 1000 * (-b))
                    y2 = int(y0 - 1000 * (a))
                    angle = math.atan2(abs(y1-y2),abs(x1-x2)) * 180 / np.pi
                    if angle > 15:
                        if y1 <= y2:
                            if rows/2 - x1 < max1: #and x1 < rows/2 - 100:
                                max1 = rows/2 - x1
                                max1_list = x1,y1,x2,y2
                        else:
                          if x2 - rows/2 < max2: #and x2 > rows/2  + 100:
                             max2 = x2 - rows/2
                             max2_list = x1,y1,x2,y2
                    if angle < 5 and angle > -5:
                        if y1 > max_y:
                            max_y = y1
                            max_y_list = x1,y1,x2,y2

        #cv2.resizeWindow('img2', 800, 900)
            if max1!=123456789:
                cv2.line(img, (max1_list[0], max1_list[1]), (max1_list[2], max1_list[3]), (255, 0, 255), 2)
            if max2!=123456789:
                cv2.line(img, (max2_list[0], max2_list[1]), (max2_list[2], max2_list[3]), (255, 0, 255), 2)
            if interflag != 1:
                if max1 == 123456789 and max2 != 123456789:
                    if time.time() - LXflag > 0.1 :
                        print('오른쪽 없음')
                        x1, y1, x2, y2 = max2_list
                        dx = x1 - x2
                        dy = y1 - y2
                        red = math.atan2(dy, dx)
                        degree = (red * 180) / np.pi
                        angle = -1 * (int(degree) + 90) + 180 + angleAddd
                        if angle - anglePre < 0:
                            angle -= 3
                        else:
                            angle += 3
                        print(angle)
                        s.send('angle ' + str(angle - anglePre))
                        angleState += angle - anglePre
                        anglePre = angle
                    LXflag = time.time()
                elif max1 != 123456789 and max2 == 123456789:
                    if time.time() - RXflag > 0.1:
                        print('왼쪽 없음')
                        x1, y1, x2, y2 = max1_list
                        dx = x1 - x2
                        dy = y1 - y2
                        red = math.atan2(dy, dx)
                        degree = (red * 180) / np.pi
                        angle = -1 * (int(degree) + 90) + angleAdd
                        if angle - anglePre < 0:
                            angle -= 3
                        else:
                            angle += 3
                        print(angle)
                        s.send('angle ' + str(angle - anglePre))
                        angleState += angle - anglePre
                        anglePre = angle
                    RXflag = time.time()
            if max1!=123456789 and max2!=123456789:
                if Lflag == 1:
                    Lflag = 0
                    interflag = 0
                    state = 'Gp -500'
                    print('정상화')
                    s.send('angle 7')
                if Uflag == 1 and UPointflag == 1:
                    Uflag = 0
                    UPointflag = 0
                    interflag = 0
                    state = 'Gp -500'
                    print('정상화')
                    s.send('angle -80 and Stop')
                    time.sleep(0.5)
                a1,b1,a2,b2 = 0,0,0,0
                same_a = 0
                same_b = 0
                x1, y1, x2, y2 = max1_list
                if x1==x2:
                    continue
                else:
                    a1 = (y2 - y1) / (x2 - x1)
                    b1 = y1 - a1 * x1
                x1, y1, x2, y2 = max2_list
                if x1 == x2:
                    continue
                else:
                    a2 = (y2 - y1) / (x2 - x1)
                    b2 = y1 - a2 * x1
                intersectX = -(b1 - b2) / (a1 - a2)
                intersectY = a1 * intersectX + b1
                cv2.circle(img, (int(intersectX), int(intersectY)), 10, (0,0,0), -1)
                dx = int(intersectX) - int( rows / 2)
                dy = int(intersectY) - cols
                red = math.atan2(dy,dx)
                degree = (red*180)/np.pi
                angle = -1*(int(degree)+90)
                if interflag != 1:
                    if angle != angleState and angle > -100 and angle < 100:
                        if time.time() - preTime > 0.1:
                            if angle == 0:
                                s.send('angle '+str(angleState * -1))
                                angleState = 0
                                anglePre = 0
                                preTime = time.time()
                            else:
                                if angle - anglePre < 0:
                                    angle -= 3
                                else:
                                    angle += 3
                                s.send('angle '+str(int(angle - anglePre)))
                                angleState += angle - anglePre
                                anglePre = angle
                                preTime = time.time()
            if max_y!=0 and max_y < cols:
                #cv2.circle(img,(int(rows/2),max_y),2,(255,255,255),-1)
                #print(int(img[max_y-10,int(rows/2),0]), int(img[max_y-10,int(rows/2),1]) , int(img[max_y-10,int(rows/2),2]))
                #if int(img[max_y,int(rows/2),0]) < 10 and int(img[max_y,int(rows/2),1]) < 10 and int(img[max_y,int(rows/2),2]) < 10:
                x1,y1,x2,y2 = max_y_list
                if Uflag == 1 and UPointflag == 0:
                    s.send('angle 70')
                    UPointflag = 1
                #차단기 인식
                elif max_y > cols/2 - 100 and greenflag == 1:
                    fflag = 0
                    for i in range(int(cols / 2 - 100)):
                        for j in range(int(rows / 2 - 100), int(rows / 2 + 100)):
                            if img[i, j, 0] < 80 and img[i, j, 1] > 100 and img[i, j, 2] > 100:
                                cv2.putText(img, 'Yellow', (j, i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
                                fflag = 1
                                break
                        if fflag == 1:
                            break
                    if fflag == 0:
                        greenflag = 0
                    else:
                        s.send('Stop')
                #신호등 인식
                elif max_y > cols/2 and UPointflag != 1 and LPointflag != 1:
                    for i in range(int(cols/2),0,-1):
                        flag = 0
                        for j in range(int(rows/2)):
                            if int(img[i, j, 0]) < 50 and int(img[i, j, 1]) > 200 and int(img[i, j, 2]) < 150:
                                cv2.putText(img, 'green', (j, i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
                                flag = 1
                                print('green')
                                s.send('Go -500')
                                interflag = 1
                                break
                            if int(img[i, j, 0]) == 250 and int(img[i, j, 1]) > 200 and int(img[i, j, 2]) > 200:
                                cv2.putText(img, 'amber', (j, i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
                                flag = 1
                                print('amber')
                                s.send('Stop')
                                break
                            if int(img[i, j, 0]) > 250 and int(img[i, j, 1]) > 250 and int(img[i, j, 2]) > 250:
                                cv2.putText(img, 'red', (j, i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
                                flag = 1
                                print('red')
                                s.send('Stop')
                                break
                        if flag == 1:
                            break
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        #출력 부분
        cv2.imshow('img2',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            time.sleep(0.2)
            s.send('Stop')
            break
    else:
        print('안됨')
        break
cap.release()
cv2.destroyAllWindows()