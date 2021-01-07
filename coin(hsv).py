# -*- coding: utf-8 -*-

# ラズパイカメラを用いた硬貨の識別（HSVの値による識別）

import picamera
import picamera.array
import cv2
import numpy as np
import math

version = cv2.__version__.split(".")
CVversion = int(version[0])

with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        camera.resolution = (320, 240)
        camera.framerate = 15

        while True:
            # stream.arrayにBGRの順で映像データを格納
            camera.capture(stream, 'bgr', use_video_port=True)
            # 映像データをグレースケール画像grayに変換
            gray = cv2.cvtColor(stream.array, cv2.COLOR_BGR2GRAY)
            # ガウシアンぼかしを適用して、認識精度を上げる
            blur = cv2.GaussianBlur(gray, (9,9), 0)
            
            # ハフ変換を適用し、映像内の円を探す
            if CVversion == 2:
                circles = cv2.HoughCircles(blur, cv2.cv.CV_HOUGH_GRADIENT,
                      dp=1, minDist=50, param1=120, param2=40,
                      minRadius=10, maxRadius=100)
            else:
                circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT,
                      dp=1, minDist=50, param1=120, param2=40,
                      minRadius=10, maxRadius=100)

            if circles is not None:
                 circles = np.uint16(np.around(circles))

                 for c in circles[0,:]:
                     r=c[2]
                     # hsvの値を取得する範囲を指定
                     xmax=c[0]+1
                     xmin=c[0]-1
                     ymax=c[1]-5
                     ymin=c[1]-7
                    # 見つかった円の上に赤い円を元の映像(system.array)上に描画
                    # c[0]:x座標, c[1]:y座標, c[2]:半径(errorになるため値を設定)
                     center = stream.array[ymin:ymax,xmin:xmax]
                     # 指定した範囲を長方形で可視化
                     cv2.rectangle(stream.array,(xmin,ymin),(xmax,ymax),(0,0,255),2)

                    # HSV色空間に変換、それぞれの値を取得
                     HSV_img = cv2.cvtColor(center,cv2.COLOR_BGR2HSV)
                     h, s, v = cv2.split(HSV_img)
                     # 指定した範囲でのh,s,v値それぞれの平均値を取得（小数点以下切り捨て）
                     new_h = math.floor(np.mean(h))
                     new_s = math.floor(np.mean(s))
                     new_v = math.floor(np.mean(v))
                     # 配列に変換
                     hsv = np.array([new_h, new_s, new_v])
                     
                     # "1yen"の条件を指定
                     if 60 < new_h < 120 and 30 < new_s < 50 and 170<new_v<=255:
                         cv2.circle(stream.array, (c[0],c[1]), r, (0,0,255) , 2)
                         # 取得した"1yen"画像の上部に"1yen"と表示
                         cv2.putText(stream.array ,"1yen", (c[0]-r,c[1]-r-8), cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.8,color=(0, 0, 255),thickness=1,lineType=cv2.LINE_AA,)
                         print("1yen")
                         print(np.array(hsv))

                    # "100yen"の条件を指定
                     elif 1<new_h<150 and 1<new_s<29 and 120<new_v<170:
                         cv2.circle(stream.array, (c[0],c[1]), r, (255,0,0), 2)
                         # 取得した"100yen"画像の上部に"100yen"と表示
                         cv2.putText(stream.array ,"100yen", (c[0]-r,c[1]-r-8), cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.8,color=(255, 0, 0),thickness=1,lineType=cv2.LINE_AA,)
                         print("100yen")
                         print(np.array(hsv))

                    # "5yen"の条件を指定     
                     elif 1<new_h<50 and 50<new_s<255 and 10<new_v<100 :
                        cv2.circle(stream.array, (c[0],c[1]), r, (0,255,0), 2)
                        # 取得した"5yen"画像の上部に"5yen"と表示
                        cv2.putText(stream.array ,"5yen", (c[0]-r,c[1]-r-8), cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.8,color=(0, 255, 0),thickness=1,lineType=cv2.LINE_AA,)
                        print("5yen")
                        print(np.array(hsv))
                     
            # system.arrayをウインドウに表示
            cv2.imshow('frame', stream.array)

            # "q"を入力でアプリケーション終了
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # streamをリセット
            stream.seek(0)
            stream.truncate()

        cv2.destroyAllWindows()
