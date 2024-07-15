import cv2              #opencv库
import numpy as np      #numpy矩阵函数库
import sys              #
import os               #os标准库
import time             #时间标准库
# 导入python串口库
import serial
import serial.tools.list_ports

#摄像头类创建
class pi_Camera():
    def __init__(self):
        # 图像初始化配置
        self.Video = cv2.VideoCapture(8, cv2.CAP_V4L2) # 使能摄像头8的驱动

        # 检查摄像头是否打开
        ret = self.Video.isOpened()
        if ret:
            print("The video is opened.")
        else:
            print("No video.")
    
        codec = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        self.Video.set(cv2.CAP_PROP_FOURCC, codec)
        self.Video.set(cv2.CAP_PROP_FPS, 60)  # 帧数
        self.Video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 列 宽度
        self.Video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 行 高度
    
    def GuideLine(self, c1, c2):
        ret, image = self.Video.read()#注意：read返回一个bull值和图像数据list！，需要用两个变量获取
        if ret:
            cv2.line(image, (0, 360), (640, 360), color=(0, 0, 255), thickness=3)  # 红色的线
            cv2.line(image, (0, 240), (640, 240), color=(0, 0, 255), thickness=3)  # 红色的线
            cv2.line(image, (int(c1), 360), (int(c2), 240), color=(0, 255, 0), thickness=2)  # 绘出倾角线
            cv2.imshow("GuideLine", image)

#激光点RGB值获取
def get_pixel_sum(image, coords):
    # 获取图像宽度和高度
    height, width = image.shape[:2]
    radius = 3

    # 确定方圆的左上角和右下角坐标
    x, y = coords
    x_start = max(0, x - radius)
    y_start = max(0, y - radius)
    x_end = min(width - 1, x + radius)
    y_end = min(height - 1, y + radius)

    # 提取方圆区域
    roi = image[y_start:y_end, x_start:x_end]

    # 计算 R 和 G 通道总值
    r_channel = roi[:, :, 2]
    g_channel = roi[:, :, 1]
    r_sum = int(r_channel.sum())
    g_sum = int(g_channel.sum())
    return r_sum, g_sum

#寻找激光点
def detect_lasers(image,last_send_time):
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # 转换颜色空间为HSV

    # 定义红色激光点hsv色彩阈值范围，用作二值化
    lower_laser = np.array([0, 100, 255])
    upper_laser = np.array([179, 255, 255])
    
    # 创建二值化图像
    mask_laser = cv2.inRange(hsv, lower_laser, upper_laser) 
    #cv2.imshow("mask_laser1", mask_laser)

    # 闭运算
    kernel = np.ones((5, 5), np.uint8)
    mask_laser = cv2.morphologyEx(mask_laser, cv2.MORPH_CLOSE, kernel)

    # 寻找轮廓
    contours_laser, _ = cv2.findContours(mask_laser, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    laser_coords = None
    for contour in contours_laser:
        # 获取最小矩形框
        rect = cv2.minAreaRect(contour)
        # 矩形框的中心坐标
        laser_coords = tuple(map(int, rect[0]))
        # 矩形框的四个角点
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        # 绘制矩形框
        cv2.drawContours(image, [box], 0, (0, 0, 0), 2)

    #cv2.imshow("mask_laser2", mask_laser)

    #是否获取到矩形框的中心坐标，防止读取值为空
    if laser_coords is not None:
        #获取激光点的RGB数据
        color_vel = get_pixel_sum(image, laser_coords)
        #在红色激光点中心坐标出绘制圆点图像
        cv2.circle(image, laser_coords, 4, (0, 0, 255), -1)
        #打印文本数据“RED”在红色激光点上 
        cv2.putText(image, "RED", (laser_coords[0] - 10, laser_coords[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)    

        #获取激光点与图像中心坐标或目标坐标的差值
        x_err = laser_coords[0]-center_x
        y_err = laser_coords[1]-center_y 

        #串口发送，数据帧格式:0xFF(帧头),<数据类型>,<数据内容>
        if x_err < 0:
            hex_data = bytes([0xFF, 0x2D, abs(x_err)])#x+
            ser.write(hex_data)
            time.sleep(0.03)
        else:
            hex_data = bytes([0xFF, 0x2B, abs(x_err)])#x-
            ser.write(hex_data)
            time.sleep(0.03)
        
        if y_err < 0:
            #pass
            hex_data = bytes([0xFF, 0x3D, abs(y_err)])#y+
            ser.write(hex_data)
            #ser.write('hi'.encode('UTF-8'))
            time.sleep(0.03)
        else:
            #pass
            hex_data = bytes([0xFF, 0x3B, abs(y_err)])#y-
            ser.write(hex_data)
            time.sleep(0.03)

        print('x:'+ str(x_err))
        print('y:'+ str(y_err))
    else:
        print("没找到激光点")

    cv2.circle(image, (center_x, center_y), 5, (0, 255, 0), -1)
    cv2.imshow("Laser Detection", image)


'''
def trackChanged(x):
    pass
'''

'''
def find_center_PID(measure,calur):
    err = 0
    err_sum = 0
    err_difference =0

    last_err = 0

    kp = 1
    kd=0
    ki=0

    err = measure - calur
    err_difference = err - last_err
    last = err

    return (kp*err + kd*err_difference + ki * err_sum)
'''

#串口初始化
ser = serial.Serial('/dev/ttyS3',19200, timeout=1) # 1s timeout
print(ser)
print("Starting demo now! Press CTRL+C to exit")

'''
# 初始化参数
Kp_initial = 0.0  # 初始值为 0.0
max_Kp = 1.0  # 最大值设为 1.0
# 创建一个回调函数，用于响应滑块数值变化
def trackChanged(value):
    global Kp
    Kp = value / 100.0  # 将整数滑块值转换为 float 类型，这里假设步长为 0.01
# 创建一个显示窗口
cv2.namedWindow('PID')
# 创建滑块，设置最大值为 100，注意这里最大值可以根据需要调整
cv2.createTrackbar("Kp", "PID", int(Kp_initial * 100), int(max_Kp * 100), trackChanged)
'''

# 摄像头
Watch = pi_Camera()  # 创建摄像头实例化对象

#读取第一帧图像，用于获取图像尺寸
ret, frame = Watch.Video.read()

if ret:
    # 创建一个与图像相同大小的空白遮罩
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    # 在遮罩中指定区域赋值为255（即白色），这里是200到400的矩形区域
    mask[140:340,220:420] = 255

# 矩形框的中心坐标
height, width = frame.shape[:2]
center_x = width // 2
center_y = height // 2
last_send_time = time.time()

while True:
    ret, frame = Watch.Video.read() #获取摄像头图像数据
    if ret:
        frame = cv2.bitwise_and(frame, frame, mask=mask) #使用遮罩，获取ROI区域
        detect_lasers(frame,last_send_time) #寻找激光点
    #等待按键事件，退出程序
    if cv2.waitKey(1) == 27:
        break

Watch.Video.release()
cv2.destroyAllWindows()