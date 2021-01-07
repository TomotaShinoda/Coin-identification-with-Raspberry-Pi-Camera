# -*- coding: utf-8 -*-

# ラズパイカメラを用いた硬貨の識別（硬貨の半径情報による識別）

import picamera
import picamera.array
import cv2
import numpy as np

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
                      minRadius=5, maxRadius=100)
            else:
                circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT,
                      dp=1, minDist=50, param1=120, param2=40,
                      minRadius=5, maxRadius=100)

            if circles is not None:
                 circles = np.uint16(np.around(circles))

                 for c in circles[0,:]:
                     r=c[2]
                    # 見つかった円の上に赤い円を元の映像(system.array)上に描画
                    # c[0]:x座標, c[1]:y座標, c[2]:半径(errorになるため値を設定)
                     if r < 44 :
                        cv2.circle(stream.array, (c[0],c[1]), r, (0,0,255), 2)
                        cv2.putText(stream.array ,"1yen", (c[0]-r,c[1]-r-8), cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.8,color=(0, 0, 255),thickness=1,lineType=cv2.LINE_AA,)
                     else:
                        cv2.circle(stream.array, (c[0],c[1]), r, (255,0,0), 2)
                        cv2.putText(stream.array ,"100yen", (c[0]-r,c[1]-r-8), cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.8,color=(255, 0, 0),thickness=1,lineType=cv2.LINE_AA,)
                    
                     print(r)
                     
            # system.arrayをウインドウに表示
            cv2.imshow('frame', stream.array)

            # "q"を入力でアプリケーション終了
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # streamをリセット
            stream.seek(0)
            stream.truncate()

        cv2.destroyAllWindows()
