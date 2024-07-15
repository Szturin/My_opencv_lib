import cv2 as cv
import numpy as np

#数据集采集程序
capture = cv.VideoCapture(0)
cv.namedWindow('cam', cv.WINDOW_NORMAL)
cv.resizeWindow('cam', 360, 360)

count = 1    # 计数器初始值

name = input('请输入图片name:')

while True:

    ret, frame = capture.read()
    # print(frame.shape)  # 查看摄像头输出图像尺寸 （480，640,3）方便后面剪裁为正方形
    cv.imshow('ori', frame)   # 输出原始图像
    img = frame[60:419, 140:499] # 裁剪图像为360x360
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # 灰度处理
    cv.imshow("cam", img)      # 采集图片时用画面

    if cv.waitKey(25) == ord('s'):      # 按下s键保存当前画面
        resize = cv.resize(gray, (60, 60), cv.INTER_AREA)
        cv.imwrite(name + '_' + str(count) + '.jpg', resize)   # 负样本时候直接保存gray
        print('已经保存图片' + str(count))
        count = count + 1
    if cv.waitKey(25) == 27:          # 按下esc退出
        print('采集结束')
        break

capture.release()
cv.destroyAllWindows()

