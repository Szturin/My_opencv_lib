#!/usr/bin/env python3
import math
import os
import cv2
import numpy as np
import serial
import time
import serial.tools.list_ports
import Hobot.GPIO as GPIO

direction = 302 #设置目标拟合线坐标（列数）

#占空比初值定义
val1 = 25
val2 = 25

#摄像头
class pi_Camera():
    def __init__(self):
        #图像初始化配置
        self.Video = cv2.VideoCapture(8, cv2.CAP_V4L2) #使能摄像头8的驱动
        #检查摄像头是否打开
        ret = self.Video.isOpened()
        if ret:
            print("The video is opened.")
        else:
            print("No video.")
    
        codec = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        self.Video.set(cv2.CAP_PROP_FOURCC, codec)
        self.Video.set(cv2.CAP_PROP_FPS, 30) #帧数
        self.Video.set(cv2.CAP_PROP_FRAME_WIDTH, 640) #列 宽度
        self.Video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # 行 高度
    
    def GuideLine(self, image, c1, c2):
        cv2.line(image, (0, 360), (640, 360), color=(0, 0, 255), thickness=3) # 红色的线
        cv2.line(image, (0, 240), (640, 240), color=(0, 0, 255), thickness=3) # 红色的线
        cv2.line(image, (int(c1), 360), (int(c2), 240), color=(0, 255, 0), thickness=2) # 绘出倾角线    

#串口进程
def Serial_Process():
    #串口选择
    print("List of enabled UART:")
    os.system('ls /dev/tty[a-zA-Z]*')
    uart_dev = input("请输出需要测试的串口设备名:")
    baudrate = input("请输入波特率(9600,19200,38400,57600,115200,921600):")
    ser = serial.Serial(uart_dev, int(baudrate), timeout=1) # 1s timeout
    print(ser)
    print("Starting demo now! Press CTRL+C to exit")

#控制
class pi_Control():
    def __init__(self, LOGICA_1, LOGICA_2, LOGICB_1, LOGICB_2, pwm_pin1, pwm_pin2):
        GPIO.setmode(GPIO.BOARD) #设置GPIO为硬件编码格式
        GPIO.setwarnings(False) #关闭GPIO警告

        GPIO.setup(LOGICB_1, GPIO.OUT, initial=GPIO.HIGH) #bn1
        GPIO.setup(LOGICB_2, GPIO.OUT, initial=GPIO.LOW)  #bn2
        GPIO.setup(LOGICA_1, GPIO.OUT, initial=GPIO.HIGH) #an1
        GPIO.setup(LOGICA_2, GPIO.OUT, initial=GPIO.LOW)  #an2

        self.LOGICA_1 = LOGICA_1
        self.LOGICA_2 = LOGICA_2
        self.LOGICB_1 = LOGICB_1
        self.LOGICB_2 = LOGICB_2

        self.PWM_A = GPIO.PWM(pwm_pin1, 48000)
        self.PWM_B = GPIO.PWM(pwm_pin2, 48000)

    def PWM_Set(self, Speed_L, Speed_R):
        if Speed_L >= 0:
            GPIO.output(self.LOGICA_1, GPIO.HIGH)
            GPIO.output(self.LOGICA_2, GPIO.LOW)
        elif Speed_L < 0:
            GPIO.output(self.LOGICA_2, GPIO.HIGH)
            GPIO.output(self.LOGICA_1, GPIO.LOW)
        
        if Speed_R >= 0:
            GPIO.output(self.LOGICB_1, GPIO.HIGH)
            GPIO.output(self.LOGICB_2, GPIO.LOW)
        elif Speed_R < 0:
            GPIO.output(self.LOGICB_2, GPIO.HIGH)
            GPIO.output(self.LOGICB_1, GPIO.LOW)   

        self.PWM_A.ChangeDutyCycle(Speed_L)
        self.PWM_B.ChangeDutyCycle(Speed_R)
        self.PWM_A.start(abs(Speed_L))
        self.PWM_B.start(abs(Speed_R))

def PID(measure, caclu):
    Kp = 0.06
    Ki = 0
    Kd = 0
    last_err = 0

    err = measure - caclu
    err_difference = err - last_err
    last_err = err
    err_sum += err_difference

    if err_sum > 2000:
        err_sum = 2000
    elif err_sum < -2000:
        err_sum = -2000

    return Kp * err + Ki * err_sum + Kd * err_difference
 
Serial_Process() #串口进程
Control = pi_Control(11, 13, 16, 15, 32, 33) #控制模块
Watch = pi_Camera() #摄像头模块
Control.PWM_Set(30, 30) #小车初速度
time.sleep(0.5)

prev_frame_time = 0
new_frame_time = 0

while True:
    ret, frame = Watch.Video.read() #从相机获取图像
    if not ret or frame is None:
        print("Failed to grab frame")
        break
    
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #BGR格式转化为灰度
    retval, dst = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)   ##大津法二值化
    dst = cv2.dilate(dst, None, iterations=2) # 膨胀，白区域变大

    print(f"FPS: {int(fps)}") # 打印FPS
    
    cv2.imshow("Trace_Mode", dst) #显示二值化图像
    color = dst[400] #获取第400行像素值，视为最底层
    black_count = np.sum(color == 0) #统计第400行像素个数
    
    if black_count == 0:
        print("黑色像素点为0")
        ser.write("r:0000l:0000\r\n".encode()) #在这里加上了串口
    else:
        black_index = np.where(color == 0) #创建list索引第400行像素值
        
        if black_count > 0:
            center = (black_index[0][black_count - 1] + black_index[0][0]) / 2
            err = direction - center #计算插值

            #PID循迹
            val1 = 15 - PID(center, direction)
            val2 = 15 + PID(center, direction)

            print(err)
            Control.PWM_Set(50, 50)

    #检测'Esc'按下，销毁程序    
    if cv2.waitKey(1) == 27:
        break

#清空PWM, GPIO引脚
Control.stop()
PWM_2.stop()
GPIO.cleanup()
#释放图像
Watch.Video.release()
#销毁CV窗口
cv2.destroyAllWindows()