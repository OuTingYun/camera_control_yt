
# 最後面的inshow註解掉就不會有影像 但是要關掉的話要**直接把整個gesture shut down**
# 因為是跳出來的cv2.imshow吃鍵盤輸入，如果註解了就沒地方案ESC。可以再考慮看看要不要留著，或是沒差，讓他一直跑直到我們直接暫停它。

import cv2
import mediapipe as mp
import math
import time

import threading
from chrome import Chrome


class Gesture:

    def __init__(self, personal, url):
        self.chrome = Chrome(personal, url)

        self.model()

        thread = threading.Thread(target=self.detect)
        thread.start()

    # 計算角度
    def calAngle(self, v1, v2):
        v1x, v1y = v1[0], v1[1]
        v2x, v2y = v2[0], v2[1]
        try:
            angle = math.degrees(math.acos(
                (v1x*v2x + v1y*v2y) /  # x dot y
                (((v1x**2 + v1y**2)**0.5) * ((v2x**2 + v2y**2)**0.5))  # |x| * |y|
            ))
        except:
            print('except')
            angle = 65535
        if angle > 180:
            angle = None
        return angle

    # 計算手指的角度
    def calHandAngle(self, hand):
        handAngle = []
        # 大拇指;
        angle = self.calAngle(
            (int(hand[0][0]-hand[1][0]), int(hand[0][1]-hand[1][1])),
            (int(hand[3][0]-hand[4][0]), int(hand[3][1]-hand[4][1]))
        )
        handAngle.append(angle)
        # 1: 食指; 2: 中指; 3: 無名指; 4: 小拇指
        for i in range(1, 5):
            base = i * 4
            angle = self.calAngle(
                (int(hand[0][0]-hand[base+2][0]),
                 int(hand[0][1]-hand[base+2][1])),
                (int(hand[base+3][0]-hand[base+4][0]),
                 int(hand[base+3][1]-hand[base+4][1]))
            )
            handAngle.append(angle)
        # 食指與中指的夾角
        angle = self.calAngle(
            (int(hand[5][0]-hand[8][0]), int(hand[5][1]-hand[8][1])),
            (int(hand[9][0]-hand[12][0]), int(hand[9][1]-hand[12][1]))
        )
        return handAngle, angle

    # 判斷手勢
    def judgeGesture(self, handAngle, angle, label):
        if None in handAngle:
            return None, None
        # 手勢
        gesture = None
        act = None
        # 彎曲的臨界值
        threshold = 100
        threshold_thumb = 90
        # 伸直的臨界值
        threshold_straight = 30
        if label == "Left":
            if handAngle[0] > threshold_thumb and handAngle[1] < threshold_straight and handAngle[2] > threshold and handAngle[3] > threshold and handAngle[4] > threshold:
                # one
                gesture = 'Play/Pause'
                act = 'play'
            elif handAngle[0] < threshold_straight and handAngle[1] < threshold_straight and handAngle[2] < threshold_straight and handAngle[3] < threshold_straight and handAngle[4] < threshold_straight:
                # five
                gesture = 'Full Screen'
                act = 'full'
            elif handAngle[0] < threshold_straight and handAngle[1] > threshold and handAngle[2] > threshold and handAngle[3] > threshold and handAngle[4] > threshold:
                # thumb
                gesture = 'Last Episode'
                act = 'previous'
            elif handAngle[0] > threshold_thumb and handAngle[1] > threshold and handAngle[2] > threshold and handAngle[3] > threshold and handAngle[4] < threshold_straight:
                # little finger
                gesture = 'Mute'
                act = 'mute'
            elif handAngle[0] > threshold_thumb and handAngle[1] < threshold_straight and handAngle[2] < threshold_straight and handAngle[3] > threshold and handAngle[4] > threshold:
                # two
                if angle < 10:
                    gesture = 'Rewind'
                    act = '-5'
                elif angle > 15 and angle < 90:
                    gesture = 'Fast forward'
                    act = '+5'
        elif label == "Right":
            if handAngle[0] < threshold_straight and handAngle[1] > threshold and handAngle[2] > threshold and handAngle[3] > threshold and handAngle[4] > threshold:
                # thumb
                gesture = 'Next Episode'
                act = 'next'
            elif handAngle[0] < threshold_straight and handAngle[1] < threshold_straight and handAngle[2] < threshold_straight and handAngle[3] < threshold_straight and handAngle[4] < threshold_straight:
                # five
                gesture = 'Theater Mode'
                act = 'movie'
            elif handAngle[0] > threshold_thumb and handAngle[1] > threshold and handAngle[2] > threshold and handAngle[3] > threshold and handAngle[4] < threshold_straight:
                # little finger
                gesture = 'Subtitle'
                act = 'cc'
            elif handAngle[0] > threshold_thumb and handAngle[1] < threshold_straight and handAngle[2] < threshold_straight and handAngle[3] > threshold and handAngle[4] > threshold:
                # two
                if angle < 10:
                    gesture = 'Volumn Down'
                    act = 'voice-'
                elif angle > 15 and angle < 90:
                    gesture = 'Volumn Up'
                    act = 'voice+'
        return gesture, act

    def model(self):
        # 繪圖工具
        self.myDrawing = mp.solutions.drawing_utils
        # hands是檢測手部關鍵點的函数
        self.myHand = mp.solutions.hands
        self.hands = self.myHand.Hands(
            # False: 輸入視為video stream; True: 輸入視為photo; (default: False)
            static_image_mode=False,
            # 可以檢測到的手的數量的最大值 (default: 2)
            max_num_hands=2,
            # 手部檢測的最小可信度值，大於這個數值被認為是成功的檢測 (default: 0.5)
            min_detection_confidence=0.75,
            # 目標跟蹤模型的最小可信度值，大於這個數值將被視為已成功跟蹤的手部，如果static_image_mode = true，則忽略此操作。 (default: 0.5)
            min_tracking_confidence=0.5
        )

    def detect(self):
        # 攝影機擷取(0: 第一支攝影機; 1: 第二支攝影機)
        cap = cv2.VideoCapture(0)
        while(True):
            gesture = None
            act = None
            # 從攝影機讀取畫面影像 (ret: True->成功; False->失敗）(frame: 畫面影像)
            ret, frame = cap.read()
            # 將影像從BGR轉到RGB (default: BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 將影像水平翻轉 (1: 水平翻轉; 0: 垂直翻轉; -1: 水平垂直翻轉;)
            # 因為攝影機為鏡像
            frame = cv2.flip(frame, 1)
            # 開始判斷
            result = self.hands.process(frame)

            # 將圖片水平翻轉
            newFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # 如果有手

            if result.multi_hand_landmarks:
                # 畫出來
                # get the label to claim right or left
                res = str(result.multi_handedness[0])
                label = res.split('"')
                for handLandmark in result.multi_hand_landmarks:
                    self.myDrawing.draw_landmarks(
                        newFrame, handLandmark, self.myHand.HAND_CONNECTIONS)
                    # 將landmark標準化後的(x, y)轉回實際位置
                    handLocal = []
                    for i in range(21):
                        x = handLandmark.landmark[i].x * newFrame.shape[1]
                        y = handLandmark.landmark[i].y * newFrame.shape[0]
                        handLocal.append((x, y))
                    if handLocal:
                        # 計算手指的角度
                        handAngle, angle = self.calHandAngle(handLocal)
                        # 判斷手勢
                        gesture, act = self.judgeGesture(
                            handAngle, angle, label[1])
                        # 在畫面中顯示文字(畫面, 文字, 位置, 字型, 大小(縮放比例), 顏色, 線條寬度, 線條種類))
                        cv2.putText(newFrame, gesture, (50, 50), 0,
                                    1.3, (0, 0, 255), 3, cv2.LINE_AA)
                        cv2.putText(newFrame, act, (400, 50), 0,
                                    1.3, (0, 0, 255), 3, cv2.LINE_AA)

            # 顯示
            cv2.imshow('camera', newFrame)
            print(act)
            try:
                self.chrome.executeIns(act)
            except:
                break
            # 若按下ESC鍵(ASCII:27)離開迴圈
            if self.chrome.isClosed() or cv2.waitKey(1) & 0xFF == 27:
                break

            time.sleep(0.5)

        cap.release()
        cv2.destroyAllWindows()   # close all imshow()


url = 'https://www.youtube.com/watch?v=wrf5KzT0954&t=195s'
# url = 'https://www.google.com/'

if __name__ == '__main__':
    gesture = Gesture(False, url)
