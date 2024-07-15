import cv2  # 导入OpenCV库

#opencv测试用例

# 创建一个VideoCapture对象，用于从摄像头捕获视频
# 0表示默认摄像头，cv2.CAP_V4L2是用于Linux系统的后端
img = cv2.VideoCapture(0, cv2.CAP_V4L2)

print("请选择图像显示方式：")
print("0:原图形 1:灰度 2:二值化")
img_set = int(input())  # 获取用户输入，并转换为整数


while True:
    ret, frame = img.read()  # 捕获一帧图像，ret表示捕获状态，frame是捕获的图像

    # 如果选择了灰度显示方式，将图像转换为灰度
    if img_set == 1:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 转成灰度图片
    elif img_set == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 转成灰度图片
        ret,frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY); #转为二值化图片
    
    # 如果成功捕获图像，显示图像
    if ret:
        cv2.imshow("frame", frame)  # 显示捕获的图像
    # 如果按下'Esc'键（ASCII码为27），退出循环
    if cv2.waitKey(1) == 27:
        break
# 释放VideoCapture对象并关闭所有窗口，释放对象？
img.release()
cv2.destroyAllWindows()  # 注意：这里是destroyAllWindows，而不是destroyAllwindows，区分大小写import cv2  # 导入OpenCV库

# 创建一个VideoCapture对象，用于从摄像头捕获视频
# 0表示默认摄像头，cv2.CAP_V4L2是用于Linux系统的后端
img = cv2.VideoCapture(0, cv2.CAP_V4L2)

print("请选择图像显示方式：")
print("0:原图形 1:灰度 2:二值化")
img_set = int(input())  # 获取用户输入，并转换为整数


while True:
    ret, frame = img.read()  # 捕获一帧图像，ret表示捕获状态，frame是捕获的图像

    # 如果选择了灰度显示方式，将图像转换为灰度
    if img_set == 1:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 转成灰度图片
    elif img_set == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 转成灰度图片
        ret,frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY); #转为二值化图片
    
    # 如果成功捕获图像，显示图像
    if ret:
        cv2.imshow("frame", frame)  # 显示捕获的图像
    # 如果按下'Esc'键（ASCII码为27），退出循环
    if cv2.waitKey(1) == 27:
        break
# 释放VideoCapture对象并关闭所有窗口，释放对象？
img.release()
cv2.destroyAllWindows()  # 注意：这里是destroyAllWindows，而不是destroyAllwindows，区分大小写