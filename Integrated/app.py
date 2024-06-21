import HandTrackingModule as htm
import cv2
import numpy as np
import os
from flask import Flask, Response
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Initialize variables and settings
folder = "Header"
video = cv2.VideoCapture(0)
list = os.listdir("header")
overlayList = []
video.set(3, 1280)
video.set(4, 720)
drawColor = (255, 0, 255)
shape = "freestyle"
eraserThickness = 50

for i in list:
    image = cv2.imread(f'{folder}/{i}')
    overlayList.append(image)
header = overlayList[11]
xp, yp = 0, 0
detector = htm.handDetector(detectionCon=0.85, maxHands=1)
imgcanvas = np.zeros((720, 1280, 3), np.uint8)

def generate_frames():
    global xp, yp, imgcanvas, header, drawColor, shape, eraserThickness
    while True:
        success, img = video.read()
        if not success:
            break
        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList, pos = detector.findPosition(img)
        
        if len(lmList) > 20:
            x1, y1 = lmList[8][1:]  # index fingertip
            xm, ym = lmList[12][1:]  # middle fingertip
            up = detector.fingersUp()
            xt, yt = lmList[4][1:]  # thumb tip
            dist = int(((yt - y1) ** 2 + (xt - x1) ** 2) ** 0.5)

            if up[1] and up[2]:
                print("selection mode")
                # for color selction
                if y1 < 120:
                        if 250 < x1 < 450:
                            header = overlayList[11]
                            drawColor = (255, 0, 255)
                        elif 550 < x1 < 750:
                            header = overlayList[2]
                            drawColor = (255,0,0)
                        elif 800 < x1 < 950:
                            header = overlayList[7]
                            drawColor = (0, 255, 0)
                        elif 1050 < x1 < 1200:
                            header = overlayList[4]
                            drawColor = (0, 0, 0)
                # for shapes selection
                if y1 > 120 and y1 < 210:
                        if x1 < 250:
                            header = overlayList[13]
                        elif 250 <x1 <450 and drawColor == (255,0,255):
                            header = overlayList[11]
                            shape = 'freestyle'
                        elif 550 < x1 < 750 and drawColor == (255,0,255):
                            header = overlayList[9]
                            shape = 'circle'
                        elif 800 < x1 < 950 and drawColor == (255,0,255):
                            header = overlayList[12]
                            shape = 'rectangle'
                        elif 1050 < x1 < 1200 and drawColor == (255,0,255):
                            header = overlayList[10]
                            shape ='ellipse'
                        elif 250 <x1 <450 and drawColor == (255,0,0):
                            header = overlayList[2]
                            shape = 'freestyle'
                        elif 550 < x1 < 750 and drawColor == (255,0,0):
                            header = overlayList[0]
                            shape = 'circle'
                        elif 800 < x1 < 950 and drawColor == (255,0,0):
                            header = overlayList[3]
                            shape = 'rectangle'
                        elif 1050 < x1 < 1200 and drawColor == (255,0,0):
                            header = overlayList[1]
                            shape ='ellipse'
                        if 250 <x1 <450 and drawColor == (0,255,0):
                            header = overlayList[7]
                            shape = 'freestyle'
                        elif 550 < x1 < 750 and drawColor == (0,255,0):
                            header = overlayList[5]
                            shape = 'circle'
                        elif 800 < x1 < 950 and drawColor == (0,255,0):
                            header = overlayList[8]
                            shape = 'rectangle'
                        elif 1050 < x1 < 1200 and drawColor == (0,255,0):
                            header = overlayList[6]
                            shape ='ellipse'

            cv2.circle(img, (x1, y1), 25, drawColor, cv2.FILLED)
            if up[1] and up[2]==False:
                print("Drawing mode")   
                if xp==0 and yp==0:
                    xp,yp=x1,y1
                if drawColor==(0,0,0): #for eraser
                    if up[1] and up[4]:
                        eraserThickness=dist
                    # cv2.line(imgcanvas,(xp,yp),(x1,y1),drawColor,eraserThickness)
                    cv2.circle(img,(x1,y1),int(eraserThickness/2),drawColor,cv2.FILLED)
                    cv2.circle(imgcanvas,(x1,y1),int(eraserThickness/2),drawColor,cv2.FILLED)
                else:
                    if shape=="freestyle":
                        if dist<50: #only if you join thumb and index, you can write
                            cv2.line(imgcanvas,(xp,yp),(x1,y1),drawColor,10)
                    if shape=="circle":
                        # print(dist)
                        cv2.circle(img,(x1,y1),dist,drawColor)
                        if up[4]==1:  #if little finger is up draw circle
                            cv2.circle(imgcanvas,(x1,y1),dist,drawColor)
                    if shape=="rectangle":
                        cv2.rectangle(img,(xt,yt),(x1,y1),drawColor)
                        if up[4]:
                            cv2.rectangle(imgcanvas,(xt,yt),(x1,y1),drawColor)
                    if shape=="ellipse":
                        a=xt-xm
                        b=yt-y1
                        if a <0:
                            a=-1*a
                        if b<0:
                            b=-1*b
                        cv2.ellipse(img,(x1,y1),(a,b),0,0,360,drawColor)
                        if up[4]:
                            cv2.ellipse(imgcanvas,(x1,y1),(a,b),0,0,360,drawColor)
            xp, yp = x1, y1

        img[0:210, 0:1280] = header
        img_gray = cv2.cvtColor(imgcanvas, cv2.COLOR_BGR2GRAY)
        _, imginv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        imginv = cv2.cvtColor(imginv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imginv)
        img = cv2.bitwise_or(img, imgcanvas)

        ret, buffer = cv2.imencode('.jpg', img)
        img = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)