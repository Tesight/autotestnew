from skydelsdx.units import Lla
from skydelsdx.units import Enu
from skydelsdx.units import toRadian
from skydelsdx.commands import *
from skydelsdx.commandexception import CommandException 
from datetime import datetime , timedelta  
from serial import Serial
from common.logger import Log

import skydelsdx
import math
import csv
import random
import pynmea2
import io
import threading
import json
import time
import socket


class PathTrajectory:#路径轨迹类
    # 初始化方法
    def __init__(self, latDeg=23.16113124, lonDeg=113.47368533, alt=1.0):
        self.LAT = latDeg     # 初始纬度（度）
        self.LONG = lonDeg    # 初始经度（度）
        self.ALT = alt        # 初始高度（米）
        self.YAW = 0          # 初始航向（度）
        self.PITCH = 0        # 初始俯仰角（度）
        self.ROLL = 0         # 初始滚转角（度）    
        # 将初始经纬度转换成弧度，并创建起点的LLA对象
        self.ORIGIN = Lla(toRadian(self.LAT), toRadian(self.LONG), self.ALT)
        self.lastX = 0
        self.lastY = 0
        self.lastZ = 0
    
        self.path_list_deg = []#路径列表
        self.push_list_radian = []#推送列表
        # 统计总路径行驶时间
        self.runningTime = 0
    
    def __StraightLineTrajectory(self,initialVelocity,finalVelocity=600,accelerationDistance=0,travelTime=0,timeStep=0,directionMatrix=(0,0),flag=0,acceleration=0):
        """_summary_
        生成直线轨迹
        Args:
            initialVelocity (_type_): m/s
            finalVelocity (_type_): m/s
            accelerationDistance (_type_): m
            travelTime(_type_):s
            timeStep (_type_): s
            directionMatrix (_type_): (X,Y)
        """

        if  abs(initialVelocity - finalVelocity) < 1e-6:
            i = 0.0
            speed = initialVelocity
            self.runningTime+= travelTime
            while i< travelTime:
                self.lastX += speed * timeStep * directionMatrix[0]
                self.lastY += speed * timeStep * directionMatrix[1]
                print()
                llaPos = self.ORIGIN.addEnu(Enu(self.lastX, self.lastY, self.lastZ))
                if speed != 0:
                    self.path_list_deg.append([speed,llaPos.latDeg(),llaPos.lonDeg(),llaPos.alt])
                    self.push_list_radian.append([speed,llaPos.lat,llaPos.lon,llaPos.alt])
                i+=timeStep
        elif flag == 1:
            a = (finalVelocity**2 - initialVelocity**2) / (2 * accelerationDistance) #加速度
            # 计算直线加速轨迹
            t = (finalVelocity-initialVelocity)/a
            self.runningTime+=t
            i = 0.0
            while i<t:
                speed = initialVelocity + a * i#
                avg_speed = speed - 0.5 * a * timeStep
                self.lastX += avg_speed * timeStep * directionMatrix[0]
                self.lastY += avg_speed * timeStep * directionMatrix[1]
                llaPos = self.ORIGIN.addEnu(Enu(self.lastX, self.lastY, self.lastZ))
                if speed!=0:
                    self.path_list_deg.append([speed,llaPos.latDeg(),llaPos.lonDeg(),llaPos.alt])
                    self.push_list_radian.append([speed,llaPos.lat,llaPos.lon,llaPos.alt])
                i+=timeStep
        else:
            a = acceleration
            t = (finalVelocity - initialVelocity) / a
            steps = int(t / timeStep)
            for i in range(steps):
                current_time = i * timeStep
                speed = initialVelocity + a * current_time
                dx = speed * timeStep + 0.5 * a * timeStep**2
                self.lastX += dx * directionMatrix[0]
                self.lastY += dx * directionMatrix[1]
                llaPos = self.ORIGIN.addEnu(Enu(self.lastX, self.lastY, self.lastZ))
                self.path_list_deg.append([speed, llaPos.latDeg(), llaPos.lonDeg(), llaPos.alt])
                self.push_list_radian.append([speed, llaPos.lat, llaPos.lon, llaPos.alt])

    def __uniformArcTrajectory(self,speed,radius,rotationDirection,timeStep,lastDirectionMatrix,circle=False):
        """_summary_
        生成弧形轨迹

        Args:
            speed (_type_): _description_
            radius (_type_): _description_
            rotationDirection (_type_): _description_
            timeStep (_type_): _description_
            lastDirectionMatrix (_type_): _description_
        """
        
        # 计算弧形轨迹

        vr=speed/radius          # 角速度
        # 计算圆心
        
        r = math.atan2(lastDirectionMatrix[0], lastDirectionMatrix[1])  # 使用atan2计算夹角

        rotationDirection = str.lower(rotationDirection)    
        if rotationDirection == 'right':
            directionMatrix = (math.sin(r + math.pi/2),math.cos(r + math.pi/2))
            r_offset = -math.pi/2
        else:
            directionMatrix = (math.sin(r - math.pi/2),math.cos(r - math.pi/2))
            vr = - vr
            r_offset = math.pi/2     
        
        x0 = self.lastX + radius*directionMatrix[0]
        y0 = self.lastY + radius*directionMatrix[1]
        angular = 0
        target_angle = 2 * math.pi if circle else math.pi / 2  # 目标角度
        while True:
            angular+=vr*timeStep
            self.runningTime+=timeStep  
            if abs(angular) >= target_angle:
                break
            self.lastX = x0 + radius * math.sin(r+r_offset+angular)
            self.lastY = y0 + radius * math.cos(r+r_offset+angular)
            llaPos = self.ORIGIN.addEnu(Enu(self.lastX, self.lastY, self.lastZ))
            if speed!=0:
                self.path_list_deg.append([speed,llaPos.latDeg(),llaPos.lonDeg(),llaPos.alt])
                self.push_list_radian.append([speed,llaPos.lat,llaPos.lon,llaPos.alt])

    # def __StaticTrajectory(self,travelTime,timeStep):
    #     speed = 0
    #     i = 0.0
    #     while True:
    #         if i > travelTime:
    #             break
    #         self.push_list_radian.append([speed,self.ORIGIN.lat,self.ORIGIN.lon,self.ORIGIN.alt])
    #         self.path_list_deg.append([speed,self.ORIGIN.latDeg(),self.ORIGIN.lonDeg(),self.ORIGIN.alt])
    #         i+= timeStep

    def __RectangleTrajectory(self, speed, length, width, turn_radius, rotation_direction, time_step, direction_matrix):
        """生成矩形轨迹（含圆角）
    
        Args:
        speed (float): 匀速运动速度（m/s）
        length (float): 长边长度（m）
        width (float): 宽边长度（m）
        turn_radius (float): 转弯半径（m）
        rotation_direction (str): 转弯方向（'left'或'right'）
        time_step (float): 时间步长（s）
        direction_matrix (tuple): 初始方向向量（如东方向为(1,0)）
     """
        def rotate_direction(current_dir, rotation):
            """根据旋转方向更新方向矩阵"""
            x, y = current_dir
            if rotation.lower() == 'right':
            # 右转90度：新方向向量为 (y, -x)
                return (y, -x)
            else:
            # 左转90度：新方向向量为 (-y, x)
                return (-y, x)
    
        current_dir = direction_matrix  # 当前方向
    
        # 生成四条边及四个转角
        for i in range(4):
            # 计算当前边长度（交替长和宽）
            current_length = length if i % 2 == 0 else width
            
            # 匀速直线运动
            travel_time = current_length / speed
            self.__StraightLineTrajectory(
                initialVelocity=speed,
                finalVelocity=speed,
                accelerationDistance=0,
                travelTime=travel_time,
                timeStep=time_step,
                directionMatrix=current_dir
            )
            
            # 90度圆弧转弯（最后一边后无需转弯）
            if i < 3:
                self.__uniformArcTrajectory(
                    speed=speed,
                    radius=turn_radius,
                    rotationDirection=rotation_direction,
                    timeStep=time_step,
                    lastDirectionMatrix=current_dir
                )
                # 更新方向
                current_dir = rotate_direction(current_dir, rotation_direction)    
    
    def generate_standard_rectangle_trajectory(self, time_step=0.1):
        """
        生成标准矩形轨迹，带有圆角
        
        轨迹特点：
        1) 起始位置静止3min，北向
        2) 250m内匀加速至100km/h
        3) 保持100km/h运动300s
        4) 250m内减速到20km/h
        5) 顺时针90°转弯，转弯半径r=20m，保持时速20km/h
        6) 重复2-5步完成矩形路径
        
        参数:
            length (float): 矩形长度（米）
            width (float): 矩形宽度（米）
            time_step (float): 时间步长（秒）
        """
        # 速度转换（km/h 到 m/s）
        v_high = 100 / 3.6  # 100 km/h = 27.78 m/s
        v_low = 20 / 3.6    # 20 km/h = 5.56 m/s
        acc_distance = 10   # 加速/减速距离（米）
        turn_radius = 20     # 转弯半径（米）
        cruise_time = 10    # 巡航时间（秒）
        static_time = 10    # 初始静止时间（秒）
        time_step = 0.1      # 时间步长（秒）
        
        # 方向矩阵，表示四个方向 (北, 东, 南, 西)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        # 1. 起始位置静止3min
        # self.__StaticTrajectory(static_time, time_step)
        
        # 进行一个完整的矩形轨迹
        for i in range(4):
            current_dir = directions[i]
            
            # 2. 加速到高速（0到100km/h或20到100km/h）
            initial_v = 0 if i == 0 else v_low
            self.__StraightLineTrajectory(
                initialVelocity=initial_v,
                finalVelocity=v_high,
                accelerationDistance=acc_distance,
                travelTime=0,  # 加速时间由加速度自动计算
                timeStep=time_step,
                directionMatrix=current_dir,
                flag=1
            )
            
            # 3. 保持高速运行300秒
            self.__StraightLineTrajectory(
                initialVelocity=v_high,
                finalVelocity=v_high,
                accelerationDistance=0,
                travelTime=cruise_time,
                timeStep=time_step,
                directionMatrix=current_dir
            )
            
            # 4. 减速到低速（100到20km/h）
            self.__StraightLineTrajectory(
                initialVelocity=v_high,
                finalVelocity=v_low,
                accelerationDistance=acc_distance,
                travelTime=0,  # 减速时间由减速度自动计算
                timeStep=time_step,
                directionMatrix=current_dir,
                flag=1
            )
            
            # 5. 90度顺时针转弯
            if i < 4:  # 最后一边之后不需要转弯
                self.__uniformArcTrajectory(
                    speed=v_low,
                    radius=turn_radius,
                    rotationDirection="right",
                    timeStep=time_step,
                    lastDirectionMatrix=current_dir
                )
        
        # 如果需要继续重复运动轨迹，可以再次调用此方法
    
    
    
    def generateStandardRoute(self,timeSteep):
        """_summary_
        生成路径    

        Args:
            timeSteep (_type_): _description_
        """
        v = 300/3.6      #300km/h
        u = 30/3.6     #30km/h
        
        # self.__uniformAccelerationTrajectory(u,v,250,timeSteep,(1,0))
        # self.__uniformStraightLineTrajectory(v,300,timeSteep,(1,0))   
        # self.__uniformAccelerationTrajectory(v,u,250,timeSteep,(1,0))
        # self.__uniformArcTrajectory(u,20,0,timeSteep,(0,-1))

        # self.__uniformAccelerationTrajectory(u,v,250,timeSteep,(0,-1))
        # self.__uniformStraightLineTrajectory(v,300,timeSteep,(0,-1))   
        # self.__uniformAccelerationTrajectory(v,u,250,timeSteep,(0,-1))
        # self.__uniformArcTrajectory(u,20,math.pi/2,timeSteep,(-1,0))       
          
        # self.__uniformAccelerationTrajectory(u,v,250,timeSteep,(-1,0))
        # self.__uniformStraightLineTrajectory(v,300,timeSteep,(-1,0))   
        # self.__uniformAccelerationTrajectory(v,u,250,timeSteep,(-1,0))
        # self.__uniformArcTrajectory(u,20,math.pi,timeSteep,(0,1))

        # self.__uniformAccelerationTrajectory(u,v,250,timeSteep,(0,1))
        # self.__uniformStraightLineTrajectory(v,300,timeSteep,(0,1))   
        # self.__uniformAccelerationTrajectory(v,u,250,timeSteep,(0,1))
        # self.__uniformArcTrajectory(u,20,math.pi*1.5,timeSteep,(1,0)) 
        
        self.__StraightLineTrajectory(u,v,250,0,timeSteep,(0,1))
        self.__StraightLineTrajectory(v,v,0,300,timeSteep,(0,1))   
        self.__StraightLineTrajectory(v,u,250,0,timeSteep,(0,1))
        self.__uniformArcTrajectory(u,20,"right",timeSteep,(0,1))   
                          
        self.__StraightLineTrajectory(u,v,250,0,timeSteep,(1,0))
        self.__StraightLineTrajectory(v,v,0,300,timeSteep,(1,0))   
        self.__StraightLineTrajectory(v,u,250,0,timeSteep,(1,0))
        self.__uniformArcTrajectory(u,20,"right",timeSteep,(1,0))

        self.__StraightLineTrajectory(u,v,250,0,timeSteep,(0,-1))
        self.__StraightLineTrajectory(v,v,0,300,timeSteep,(0,-1))   
        self.__StraightLineTrajectory(v,u,250,0,timeSteep,(0,-1))
        self.__uniformArcTrajectory(u,20,"right",timeSteep,(0,-1))       
          
        self.__StraightLineTrajectory(u,v,250,0,timeSteep,(-1,0))
        self.__StraightLineTrajectory(v,v,0,300,timeSteep,(-1,0))   
        self.__StraightLineTrajectory(v,u,250,0,timeSteep,(-1,0))
        self.__uniformArcTrajectory(u,20,"right",timeSteep,(-1,0))

    def generateCustomerRoute(self,routeList,time):
        """_summary_
        用户自定义轨迹

        Args:
            routeList (_type_): [ { 'type':'',#类型
                                    'timeStep':,#时间步长
                                    'directionMatrix':,#方向
                                    'initialVelocity':,#初始速度
                                    'finalVelocity':,#最终速度
                                    'accelerationDistance':,#加速距离
                                    'travelTime':,#行驶时间
                                    'directionMatrix':, #方向
                                    'radius':,#半径
                                    'rotationDirection':,#旋转方向
                                    'lastDirectionMatrix':,#上一个方向

                                    } ]
        """
        for route in routeList:
            # print(route)
            if type(route) == str:
               route = json.loads(route.replace("'",'"'))
            if route['type'] == 'straightLine':#匀速直线轨迹
                if route['initialVelocity'] == route['finalVelocity']:

                    self.__StraightLineTrajectory(initialVelocity=route['initialVelocity'],
                                                    finalVelocity=route['finalVelocity'],
                                                    travelTime=route['travelTime'],
                                                    timeStep=route['timeStep'],
                                                    directionMatrix=route['directionMatrix'])
                elif time>(abs(route['initialVelocity']-route['finalVelocity'])/route['acceleration']):
                    T=time-(abs(route['initialVelocity']-route['finalVelocity'])/route['acceleration'])
                    self.__StraightLineTrajectory(initialVelocity=route['initialVelocity'],
                                                    finalVelocity=route['finalVelocity'],
                                                    travelTime=route['travelTime'],
                                                    timeStep=route['timeStep'],
                                                    directionMatrix=route['directionMatrix'],
                                                    flag=0,
                                                    acceleration=route['acceleration'])
                    
                    self.__StraightLineTrajectory(initialVelocity=600,
                                                    finalVelocity=600,
                                                    travelTime=T,
                                                    timeStep=route['timeStep'],
                                                    directionMatrix=route['directionMatrix'],
                                                    )
                else:
                    self.__StraightLineTrajectory(initialVelocity=route['initialVelocity'],
                                                    finalVelocity=600,
                                                    travelTime=route['travelTime'],
                                                    timeStep=route['timeStep'],
                                                    directionMatrix=route['directionMatrix'],
                                                    acceleration=route['acceleration'],
                                                    flag=1
                                                    )
            elif route['type'] == 'arc':#圆形轨迹
                self.__uniformArcTrajectory(speed=route['initialVelocity'],
                                            radius=route['radius'],
                                            rotationDirection=route['rotationDirection'],
                                            timeStep=route['timeStep'],
                                            lastDirectionMatrix=route['lastDirectionMatrix'],
                                            circle=True)   
            # elif route['type'] == 'static':#静态轨迹
            #     self.__StaticTrajectory(travelTime=route['travelTime'],
            #                             timeStep=route['timeStep'])
            elif route['type'] == 'rectangle':#矩形轨迹
                # 初始方向向东，生成顺时针矩形轨迹
                for i in range(route['repeat']):
                    self.generate_standard_rectangle_trajectory(time_step=route['timeStep'])
            else:
                Log().logger.error(f"不支持的轨迹类型: {route['type']}")
    def saveToCSV(self,filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Speed (m/s)', 'Lat (deg)', 'Lon (deg)', 'Alt (m)'])
            for line in self.path_list_deg:
                writer.writerow(line)
    
    def resetResultList(self):
        self.path_list_deg = []
        self.push_list_radian = []
    
class AntennaModel:#天线模型类
    def __init__(self) -> None:
        self.result_list = [[0 for _ in range(120)] for _ in range(60)]  
    
    def saveToCSV(self,filename):#保存天线模型到CSV文件
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for line in self.result_list:
                writer.writerow(line)
    
    def generateUrbanCanyon(self):#生成城市环境下的信号传播
        for i in range(0,60):
            for j in range(0,120):
                if i > 32 and i < 40:
                    if (j >10 and j <50) or (j >70 and j<110):
                        self.result_list[i][j] = -40
                    else:
                        self.result_list[i][j] = 0
                elif i >= 40:
                    self.result_list[i][j] = 0
                else:
                    self.result_list[i][j] = -100
    
    def generateClearSky(self):#生成清晰天空信号传播
        for i in range(0,60):
            for j in range(0,120):  
                if i >31:
                    self.result_list[i][j] = 0
                else:
                    self.result_list[i][j] = -100   

    def resetResultList(self):#重置天线模型
        self.result_list = [[0 for _ in range(120)] for _ in range(60)]  

class MySimulator:#模拟器类
    # 初始化方法
    def __init__(self,targetIPAddress="localhost") -> None:
        self.simulator = skydelsdx.RemoteSimulator()  # 实例化远程模拟器
        self.radioType = "NoneRT"     # 无线电类型，可以是 "NoneRT", "DTA-2115B", "DTA-2116" 
        self.uniqueRadioId = ["uniqueId1","uniqueId2","uniqueId3","uniqueId4" ]  # 无线电的唯一识别ID
        self.multipathLevel = 0#多径级别
        self.startTime = None
        self.signalStrengthModel = False#信号强度模型
        self.skydel_Benchmark_Power = -130 #Skydel基准功率
        self.output_reference_power =  -130  #输出基准功率pc
        self.control = False#是否启用传播模型

        self.gain = 0 #SDR增益
        self.globaloffset=0#全局偏移
        self.enabledSignal = []
        self.duration_time=0#持续时间
        
        self.skydelIpAddress = targetIPAddress  # Skydel的IP地址，如果脚本不在Skydel的PC上运行，需要设置为Skydel的PC的IP地址
        
        # 特定于X300和N310的设置
        self.radioAddress = "192.168.40.2"   # 确保此地址指向你的USRP
        
        self.pathTrajectoryGenerator = PathTrajectory()#路径轨迹生成器
        self.antennaModelGenerator = AntennaModel()#天线模型生成器
        
        self.UPPERL = ["L1CA","L1C","L1P","G1","E1","B1","B1C","SBASL1","QZSSL1CA","QZSSL1CB","QZSSL1C","QZSSL1S"]
        self.LOWERL = ["L2C","L2P","L5","G2","E5a","E5b","B2","B2a","B3I","SBASL5","QZSSL2C","QZSSL5","QZSSL5S","NAVICL5"]
        self.SIGNALS_GPS = ["L1CA","L1C","L1P","L2C","L2P","L5"]
        self.SIGNALS_BeiDou = ["B1","B1C","B2","B2a","B3I"]
        self.SIGNALS_Galileo = ["E1","E5a","E5b"]
        self.SIGNALS_GLONASS = ["G1","G2"]
        self.SIGNALS_QZSS = ["QZSSL1CA","QZSSL1CB","QZSSL1C","QZSSL1S","QZSSL2C","QZSSL5","QZSSL5S"]
        self.SIGNALS_SBAS = ["SBASL1","SBASL5"]
        self.SIGNALS_NAVIC = ["NAVICL5"]

        self.decivetype=None#gnss设备类型
        self.deviceserialnum=None#gnss设备序列号
        self.externalattenuation=0#外部衰减
        self.dc_block_mounting=None#直流阻塞安装
        self.systemnum=[]#卫星数量
        


    # 连接到模拟器
    def simulator_connect(self):
        try:
            self.simulator.setVerbose(False)  # 设置详细模式
            self.simulator.connect(self.skydelIpAddress)  # 连接到Skydel
            return True
        except Exception as e:
            print(e)
            return False

    # 解除连接
    def simulator_disconnect(self):
        self.simulator.disconnect() 
        
    # 初始化全局设置
    def __simulator_init_preference(self):
        # 检查Skydel的引擎延迟设置
        if self.simulator.call(GetEngineLatency()).latency() != self.skydelEngineLatencyMs:
            self.simulator.call(SetEngineLatency(self.skydelEngineLatencyMs))

    # 创建一个新的配置并设置相关参数
    def __simulator_init_new_config(self,bandList,signalList):
        self.simulator.call(New(True, False))  # 创建新配置，忽略默认配置
        if self.radioType == "NoneRT":
            self.gain=0
            for index,band in enumerate(bandList):
                # 设置输出目标
                self.simulator.call(SetModulationTarget(self.radioType, "",  "", True, self.uniqueRadioId[index]))
                # 设置信号参数
                self.simulator.call(ChangeModulationTargetSignals(0, 12500000, 100000000, band, signalList[index], 0, False, self.uniqueRadioId[index]))
      
        if self.radioType == "DTA-2115B":
            self.gain=50
            for index,band in enumerate(bandList):
                # 设置输出目标
                self.simulator.call(SetModulationTarget(self.radioType, "",  "", True, self.uniqueRadioId[index]))
                # 设置信号参数
                self.simulator.call(ChangeModulationTargetSignals(0, 12500000, 100000000, band, signalList[index], 50, False, self.uniqueRadioId[index]))
        
        if self.radioType == "DTA-2116":
            self.gain=50
            for index,band in enumerate(bandList):
                # 设置输出目标
                self.simulator.call(SetModulationTarget(self.radioType, "",  "", True, self.uniqueRadioId[index]))
                # 设置信号参数
                self.simulator.call(ChangeModulationTargetSignals(0, 12500000, 100000000, band, signalList[index], 50, False, self.uniqueRadioId[index]))
        
        if self.control==False:
            self.simulator.call(EnableSignalStrengthModel(self.signalStrengthModel))    # 关闭信号强度模型
            self.simulator.call(SetVehicleAntennaGainCSV("", AntennaPatternType.AntennaNone, GNSSBand.L1, "Basic Antenna"))#设置天线增益为none
            self.simulator.call(SetVehicleAntennaGainCSV("", AntennaPatternType.AntennaNone, GNSSBand.L2, "Basic Antenna"))
            self.simulator.call(SetVehicleAntennaGainCSV("", AntennaPatternType.AntennaNone, GNSSBand.L5, "Basic Antenna"))
            self.simulator.call(SetVehicleAntennaGainCSV("", AntennaPatternType.AntennaNone, GNSSBand.E6, "Basic Antenna"))
            #self.simulator.call(SetVehicleAntennaGainCSV("", AntennaPatternType.AntennaNone, GNSSBand.S, "Basic Antenna"))


        # 启用日志记录
        self.simulator.call(EnableLogRaw(False))  # 可以启用原始日志记录并进行比较（接收器位置信息特别有用）
        self.antennaModelGenerator.resetResultList()#重置天线模型
        self.pathTrajectoryGenerator.resetResultList()#重置路径轨迹

    def __setStartTime(self):
        # 设置时间为当前时间
        if self.startTime is None:
            self.simulator.call(SetStartTimeMode("Computer"))
        else:
            if type(self.startTime) == str:
                self.startTime = eval(self.startTime)  
            sim_time = datetime(self.startTime[0],self.startTime[1],self.startTime[2],self.startTime[3],self.startTime[4],self.startTime[5])
            self.simulator.call(SetStartTimeMode("Custom"))
            self.simulator.call(SetGpsStartTime(sim_time))
        self.simulator.call(SetDuration(self.duration_time))#设置持续时间
            
    def __set_multiPath(self,constellation,level):
        # 
        elevation_mask_0 = 20  # (20 * math.pi) / 180
        elevation_mask_1 = 45  # (40 * math.pi) / 180
        elevation_mask_2 = 60  # (40 * math.pi) / 180
        list_id = []
        
        
        
        def add_multipath(svId,signal,los_en,l_powerloss,l_pseu,l_doppler,l_carrier):
            self.simulator.call(EnableLosForSV(constellation, svId, los_en))
            
            id = constellation+"-echo1-" + str(svId)
            if id not in list_id:
                list_id.append(id)
            self.simulator.call(SetMultipathForSV(signal, svId, l_powerloss[0], l_pseu[0], l_doppler[0], l_carrier[0], 1, id))
            
            id = constellation+"-echo2-" + str(svId)
            if id not in list_id:
                list_id.append(id)
            self.simulator.call(SetMultipathForSV(signal, svId, l_powerloss[1], l_pseu[1], l_doppler[1], l_carrier[1], 2, id))

            id = constellation+"-echo3-" + str(svId)
            if id not in list_id:
                list_id.append(id)
            self.simulator.call(SetMultipathForSV(signal, svId, l_powerloss[2], l_pseu[2], l_doppler[2], l_carrier[2], 3, id))

            id = constellation+"-echo4-" + str(svId)
            if id not in list_id:
                list_id.append(id)
            self.simulator.call(SetMultipathForSV(signal, svId, l_powerloss[3], l_pseu[3], l_doppler[3], l_carrier[3], 4, id))
 
        def get_mp_para(level,eg_level):
            level = min(max(level, 0), 5)
            pseu_1 = random.randint(1 * level, 50*level)
            pseu_2 = random.randint(25*level, 75*level)
            pseu_3 = random.randint(50*level, 100*level)
            pseu_4 = random.randint(75*level, 150*level)
            if eg_level == 1:
                k_list = [1,1,1,1]
            elif eg_level == 2:
                k_list = [1,1,1,0]
            elif eg_level == 3:
                k_list = [1,1,0,0]
            elif eg_level == 4:
                k_list = [1,0,0,0]
            else:
                k_list = [0,0,0,0]

            l_powerloss = [0,0,0,0]
            l_pseu = [pseu_1*k_list[0],pseu_2*k_list[1],pseu_3*k_list[2],pseu_4*k_list[3]]
            l_doppler =  [0,0,0,0]
            l_carrier =  [0,0,0,0]
            
            return l_powerloss,l_pseu,l_doppler,l_carrier
 
        def renameSignal(signal):
            if signal == 'C/A':
                return 'L1CA'
            
            
            return signal
 
        visibles = self.simulator.call(GetVisibleSV(constellation))
        
        for svId in visibles.svId():  # Echo and LOS

            # Get the power of that satellite
            el_az = self.simulator.call(GetElevationAzimuthForSV(constellation, svId))
            el_az_func = el_az.elevationAzimuth()
            el = el_az_func['Elevation']
            az = el_az_func['Azimuth']
            el_eg = (el * 180) / math.pi
            signals = self.simulator.call(GetEnabledSignalsForSV(constellation,svId)).signalArray()
            
            if el_eg <= elevation_mask_0:   # 如果仰角小于25度，在每颗卫星上应用四个多径，并禁用LOS效应：
                l_powerloss,l_pseu,l_doppler,l_carrier = get_mp_para(level,1)
                for signal in signals:
                    signal = renameSignal(signal)
                    add_multipath(svId,signal,False,l_powerloss,l_pseu,l_doppler,l_carrier)

            elif el_eg >= elevation_mask_0 and el_eg <= elevation_mask_1:   # 如果仰角在25-45°,在每颗卫星上应用上个多径，并禁用LOS效应：
                l_powerloss,l_pseu,l_doppler,l_carrier = get_mp_para(level,2)
                for signal in signals:
                    signal = renameSignal(signal)
                    add_multipath(svId,signal,False,l_powerloss,l_pseu,l_doppler,l_carrier)


            elif el_eg >= elevation_mask_1 and el_eg <= elevation_mask_2:   # 如果仰角在45-60°，在每颗卫星上应用两个多径，并启用LOS效应：
                l_powerloss,l_pseu,l_doppler,l_carrier = get_mp_para(level,3)
                for signal in signals:
                    signal = renameSignal(signal)
                    add_multipath(svId,signal,True,l_powerloss,l_pseu,l_doppler,l_carrier)

            else:   # 在所有其他情况下（即对于所有高于 60度的卫星），在每颗卫星上应用一个多径，并启用LOS效应：
                l_powerloss,l_pseu,l_doppler,l_carrier = get_mp_para(level,4)
                for signal in signals:
                    signal = renameSignal(signal)
                    add_multipath(svId,signal,True,l_powerloss,l_pseu,l_doppler,l_carrier)

    def set_multipath(self):
        gnss_constellations = ['GPS','GLONASS','GALILEO','BEIDOU','SBAS','QZSS','NAVIC']
        for constellation in  gnss_constellations:
            self.__set_multiPath(constellation,self.multipathLevel)
     
    def __resetStartPoint(self):
        self.pathTrajectoryGenerator.ORIGIN.lat = toRadian(self.pathTrajectoryGenerator.LAT)
        self.pathTrajectoryGenerator.ORIGIN.lon = toRadian(self.pathTrajectoryGenerator.LONG)
        self.pathTrajectoryGenerator.ORIGIN.alt = self.pathTrajectoryGenerator.ALT  # 设置起点
                
    def setStatic(self):
        # 设置定点
        self.simulator.call(SetVehicleTrajectoryFix("Fix",
                                                    toRadian(self.pathTrajectoryGenerator.LAT),
                                                    toRadian(self.pathTrajectoryGenerator.LONG),
                                                    self.pathTrajectoryGenerator.ALT,
                                                    toRadian(self.pathTrajectoryGenerator.YAW),
                                                    toRadian(self.pathTrajectoryGenerator.PITCH),
                                                    toRadian(self.pathTrajectoryGenerator.ROLL)
                                                    )) 
        self.simulator.call(SetDuration(self.duration_time))
        self.simulator.arm()
    
    def setStatic2(self,time):
        # 设置定点
        self.simulator.call(SetVehicleTrajectoryFix("Fix",
                                                    toRadian(self.pathTrajectoryGenerator.LAT),
                                                    toRadian(self.pathTrajectoryGenerator.LONG),
                                                    self.pathTrajectoryGenerator.ALT,
                                                    toRadian(self.pathTrajectoryGenerator.YAW),
                                                    toRadian(self.pathTrajectoryGenerator.PITCH),
                                                    toRadian(self.pathTrajectoryGenerator.ROLL)
                                                    )) 
        self.simulator.call(SetDuration(time))
        self.simulator.arm()    

    def setDynamic(self):
        # self.antennaModelGenerator.generateClearSky()
        # # self.__simulator_init_new_config(bandList= ["UpperL"], signalList=["L1CA,G1,E1,B1"])    
        # self.__setAntennaModel("clearSky",self.antennaModelGenerator.result_list)
        self.__resetStartPoint()
        self.pathTrajectoryGenerator.generateStandardRoute(0.1)
        self.pushRouteNode(self.pathTrajectoryGenerator.push_list_radian)   # 推送节点
        self.simulator.arm()

    def setAntennaClearSky(self):#设置天线模型清晰天空信号传播
        self.antennaModelGenerator.generateClearSky()
        self.__setAntennaModel("clearSky",self.antennaModelGenerator.result_list)
        
    def setAntennaUrbanCanyon(self):#设置天线模型城市环境下的信号传播
        self.antennaModelGenerator.generateUrbanCanyon()
        self.__setAntennaModel("urbanCanyon",self.antennaModelGenerator.result_list)
        
    def setAntennaNone(self):#设置天线模型无天线
        self.__setAntennaModelNone()
      
    def setSignalFull(self):
        self.enabledSignal = ["L1C","B1","E1","G1"] 
        self.setSignals(self.enabledSignal )

      
    def setSignalBeiDou(self):
        self.enabledSignal  = ["B1",]
        self.setSignals( self.enabledSignal)
      
    def setSignals(self,enabledSignalList: list):
        """_summary_
        "L1CA","L1C","L1P","G1","E1","B1","B1C","SBASL1","QZSSL1CA","QZSSL1CB","QZSSL1C","QZSSL1S"
        "L2C","L2P","L5","G2","E5a","E5b","B2","B2a","B3I","SBASL5","QZSSL2C","QZSSL5","QZSSL5S","NAVICL5"
        Args:
            enabledSignalList (list): _description_
            startTime (datetime): _description_

        Raises:
            Exception: _description_
        """
        bandList = []
        signalListU = []
        signalListL = []
        signalList = []
        
        for sig in enabledSignalList:
            if sig in self.UPPERL:
                signalListU.append(sig) 
                # self.enabledSignal.append(sig)
            elif sig in self.LOWERL:
                # self.enabledSignal.append(sig)
                signalListL.append(sig) 
            else:
                raise Exception("不支持的信号")
        self.enabledSignal = enabledSignalList
        if signalListU:
            bandList.append("UpperL")
            signalList.append(",".join(signalListU))    
        if signalListL:
            bandList.append("LowerL")
            signalList.append(",".join(signalListL))    

        self.__simulator_init_new_config(bandList, signalList)
        self.__setStartTime()

    def setSystemnum(self):
        if(self.systemnum[0]!=0 and self.systemnum[0]>4):
            gps=self.getVisiableSV('GPS')  
            num_satellites = max(0, min(self.systemnum[0], len(gps)))
            # 选择要启用的卫星
            satellites_to_enable = gps[:num_satellites]
            satellites_to_disable = gps[num_satellites:]
            
            # 启用选定的卫星
            for sv_id in satellites_to_enable:
                self.simulator.call(EnableRFOutputForSV('GPS', sv_id, True))
                
            # 禁用其余卫星
            for sv_id in satellites_to_disable:
                self.simulator.call(EnableRFOutputForSV('GPS', sv_id, False))
        
        if(self.systemnum[1]!=0):
            bei=self.getVisiableSV('BeiDou') 
            num_satellites = max(0, min(self.systemnum[1], len(bei)))
            satellites_to_enable = bei[:num_satellites]
            satellites_to_disable = bei[num_satellites:]
            
            # 启用选定的卫星
            for sv_id in satellites_to_enable:
                self.simulator.call(EnableRFOutputForSV('BeiDou', sv_id, True))
                
            # 禁用其余卫星
            for sv_id in satellites_to_disable:
                self.simulator.call(EnableRFOutputForSV('BeiDou', sv_id, False))
        
        if(self.systemnum[2]!=0):
            galileo=self.getVisiableSV('Galileo') 
            num_satellites = max(0, min(self.systemnum[2], len(galileo)))
                        # 选择要启用的卫星
            satellites_to_enable = galileo[:num_satellites]
            satellites_to_disable = galileo[num_satellites:]
            
            # 启用选定的卫星
            for sv_id in satellites_to_enable:
                self.simulator.call(EnableRFOutputForSV('Galileo', sv_id, True))
                
            # 禁用其余卫星
            for sv_id in satellites_to_disable:
                self.simulator.call(EnableRFOutputForSV('Galileo', sv_id, False))
        
        if(self.systemnum[3]!=0):
            glonass=self.getVisiableSV('GLONASS') 
            num_satellites = max(0, min(self.systemnum[3], len(glonass)))
            satellites_to_enable = glonass[:num_satellites]
            satellites_to_disable = glonass[num_satellites:]
            
            # 启用选定的卫星
            for sv_id in satellites_to_enable:
                self.simulator.call(EnableRFOutputForSV('GLONASS', sv_id, True))
                
            # 禁用其余卫星
            for sv_id in satellites_to_disable:
                self.simulator.call(EnableRFOutputForSV('GLONASS', sv_id, False))
        
    def pushRouteNode(self,pushRouteNode):
        self.simulator.call(SetVehicleTrajectory("Route"))
        self.simulator.beginRouteDefinition()  
        for node in pushRouteNode:
            self.simulator.pushRouteLla(node[0],Lla(node[1],node[2],node[3]))    
        self.simulator.endRouteDefinition()

    
    def __setAntennaModelNone(self):
        try:
            self.simulator.call(AddEmptyVehicleAntennaModel("None"))
        except CommandException:
            pass
        self.simulator.call( SetDefaultVehicleAntennaModel("None"))
        
    def __setAntennaModel(self,model,genMatrix):
        try:
            self.simulator.call(AddEmptyVehicleAntennaModel(model))
        except CommandException:
            pass
        finally:    
            self.simulator.call(SetVehicleAntennaGain(genMatrix,AntennaPatternType.Custom,GNSSBand.L1,model))    
            self.simulator.call(SetVehicleAntennaGain(genMatrix,AntennaPatternType.Custom,GNSSBand.L2,model))  
            self.simulator.call(SetVehicleAntennaGain(genMatrix,AntennaPatternType.Custom,GNSSBand.L5,model))  
            self.simulator.call(SetVehicleAntennaGain(genMatrix,AntennaPatternType.Custom,GNSSBand.E6,model))  
            self.simulator.call( SetDefaultVehicleAntennaModel(model) )
        
    def startSimulation(self):
        self.simulator.beginVehicleInfo()
        self.simulator.start()  # 开始模拟
    
    def stopSimulation(self):
        self.simulator.endVehicleInfo()
        self.simulator.stop()  # 停止模拟   

    def getVehicleInfo(self):
        """_summary_
        获取车辆信息

        Args:
            _type_ (_type_): _description_

        Returns:
            lla: 位置信息
            odometer: 里程计
            speed: 速度 
        """
        if self.simulator.hasVehicleInfo():

            time = self.get_current_simulation_time()
            info = self.simulator.lastVehicleInfo()
            lla = info.ecef.toLla()
            yaw = info.attitude.yawDeg()
            pitch = info.attitude.pitchDeg()
            roll = info.attitude.rollDeg()  
            pc=self.output_reference_power
            #print("lla:"+str(lla),"info"+str(info),"yaw:"+str(yaw),"pitch:"+str(pitch),"roll:"+str(roll),"pc:"+str(pc),"time:"+str(time))
            return lla,info.odometer,info.speed,yaw,pitch,roll,pc,time
        else:
            raise Exception("No VehicleInfo,maybe the simulator didn't start.") 

    def customizedTest(self,routeList):
        self.__resetStartPoint()#重置起点为弧度制
        for route in routeList:
            # print(route)
            if type(route) == str:
               route = json.loads(route.replace("'",'"'))
            if route['type'] != 'static':#匀速直线轨迹
                self.pathTrajectoryGenerator.generateCustomerRoute(routeList,self.duration_time)
            # print(self.pathTrajectoryGenerator.push_list_radian)
                self.pushRouteNode(self.pathTrajectoryGenerator.push_list_radian)
                self.simulator.arm() 
            else:
                self.setStatic2(route['travelTime'])
        
    def setGlobalPowerOffset(self,offset:int):
        #-45---30
        self.simulator.call(SetGlobalPowerOffset(offset))
    
    def getSignalPowerOffset2(self):#获取信号功率偏移
        self.globaloffset=-(-self.output_reference_power+self.skydel_Benchmark_Power-self.externalattenuation+self.gain)
        # print(str(self.globaloffset)+"***************************")
        if self.globaloffset < -45 or self.globaloffset > 30:
            raise Exception("Global Power Offset out of range")
        else:
            self.setGlobalPowerOffset(self.globaloffset)

    def setSignalPowerOffset(self,signalList:list,offset:int):
        #-45---10
        # full_signals = self.LOWERL + self.UPPERL
        # full_signals.remove("SBASL5")
        # full_signals.remove("SBASL1")
        # if signalList == full_signals:
        #     pass
        # elif self.enabledSignal:
        #     for sig in signalList:
        #         if sig not in self.enabledSignal:
        #             raise Exception(" Signal and system do not match")  
                    
        for signal in signalList:
            self.simulator.call(SetSignalPowerOffset(signal,offset))

    def setManualPowerOffsetForSV(self,system,svid,offset:int):
        #-45---10
        if self.enabledSignal:
            if system == 'GPS':
                for sig in self.enabledSignal:
                    if sig in self.SIGNALS_GPS:
                        break
                else:
                    raise Exception(" Signal({}) and system({}) do not match".format(sig,system)) 
            elif system == 'BeiDou':
                for sig in self.enabledSignal:
                    if sig in self.SIGNALS_BeiDou:
                        break
                else:
                    raise Exception(" Signal({}) and system({}) do not match".format(sig,system))  
            elif system == 'Galileo':
                for sig in self.enabledSignal:
                    if sig in self.SIGNALS_Galileo:
                        break
                else:
                    raise Exception(" Signal({}) and system({}) do not match".format(sig,system))  
            elif system == 'GLONASS':
                for sig in self.enabledSignal:
                    if sig in self.SIGNALS_GLONASS:
                        break
                else:
                    raise Exception(" Signal({}) and system({}) do not match".format(sig,system))  
            elif system == 'QZSS':
                for sig in self.enabledSignal:
                    if sig in self.SIGNALS_QZSS:
                        break
                else:
                    raise Exception(" Signal({}) and system({}) do not match".format(sig,system))  
            elif system == 'SBAS':
                for sig in self.enabledSignal:
                    if sig in self.SIGNALS_SBAS:
                        break
                else:
                    raise Exception(" Signal({}) and system({}) do not match".format(sig,system))  
            elif system == 'NAVIC':
                for sig in self.enabledSignal:
                    if sig in self.SIGNALS_NAVIC:
                        break
                else:
                    raise Exception(" Signal({}) and system({}) do not match".format(sig,system))  
            else:
                raise Exception("Unsupported system")   
        
        self.simulator.call(SetManualPowerOffsetForSV(system,svid,{"All":offset},False))   

    def getGlobalPowerOffset(self):
        return self.simulator.call(GetGlobalPowerOffset()).offset()

    def getSignalPowerOffset(self,signal):
        return self.simulator.call(GetSignalPowerOffset(signal)).offset()    
    
    def getManualPowerOffsetForSV(self,system,svID):
        s = self.simulator.call(GetManualPowerOffsetForSV(system,svID,["All"]))
        info_dict = {}
        info_dict["svId"] = s.svId()
        signals_dict = {}
        for k,i in enumerate(s.signalPowerOffsetDict().items()):
            signals_dict[i[0]] = i[1]
        info_dict["SignalPowerOffsetDict"] = signals_dict
        return info_dict
    
    def getVisiableSV(self,system):
        visibles = self.simulator.call(GetVisibleSV(system))
        return visibles.svId()


    def get_current_simulation_time(self):
        # 获取模拟器已运行的毫秒数
        elapsed_time_result = self.simulator.call(GetSimulationElapsedTime())
        # 从结果对象中提取毫秒值
        elapsed_milliseconds = elapsed_time_result.milliseconds()
        # 现在可以正确创建 timedelta 对象
        delta = timedelta(milliseconds=elapsed_milliseconds)
        # 计算当前模拟时间
        if self.startTime is None:
            self.startTime = datetime.now()
        current_time = self.startTime + delta
        return current_time
    
    

class Receiver:#dut类
    def __init__(self,comPort:str = None,baudRate: int = 9600,byteSize: int = 8,stopBit: int = 1) -> None:
        self.serialPort = None
        self.comPort = comPort
        self.baudRate = baudRate
        self.byteSize = byteSize
        self.stopBit = stopBit

        self.socket = None#
        self.dut_ip = None
        self.dut_port = None
        self.timeout = 5.0#超时时间
        self.sio = None#IO包装器
        

        self.running = False
        self.message_thread = None
        self.err_message = None
        self.GSV_info = {
            'num_sv_in_view':{
                'GPS':0,
                'BeiDou':0,
                'Galileo':0,
                'GLONASS':0,
                'all':0
                },
            'update_time':time.time(),

            }
        self.location_dict = {
            'update_time':time.time(),#更新时间
            'receiver_running':False,#接收器是否运行
            'lat_deg':0,#纬度
            'lon_deg':0,#经度
            'alt':0,#海拔
            'isValid':False,#是否有效
            'message':0,#原始数据
            'num_sats':0,#卫星数
            'datetime':0,#时间
            'err_message':self.err_message,#错误信息
            'speed':0#速度（节）
        }

    def reset_com(self):#重置串口
        if self.serialPort is not None:
            if self.serialPort.isOpen():
                self.serialPort.close() 
        try:
            self.serialPort = Serial(port=self.comPort,baudrate= self.baudRate, timeout=5.0,bytesize=self.byteSize,stopbits=self.stopBit)
            self.sio = io.TextIOWrapper(io.BufferedRWPair(self.serialPort, self.serialPort))
            return None
        except Exception as e:
            return e
        
    def reset_ip(self):#重置IP
        if self.socket is not None:
            try:
                self.socket.close()
            except Exception:
                pass
        try:
            # socket.AF_INET:
            # 表示使用 IPv4 地址族。
            # 用于指定网络协议族，这里是 IPv4。
            # socket.SOCK_STREAM:
            # 表示使用 TCP 协议。
            # 提供可靠的、面向连接的字节流服务。
            # 创建新的 TCP 连接
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.dut_ip, self.dut_port))
           # 创建 IO 包装器，保持与原代码类似的读写接口
            socket_file = self.socket.makefile(mode='rwb')
            self.sio = io.TextIOWrapper(io.BufferedRWPair(socket_file, socket_file))
            return None
        except Exception as e:
            return e        
        
    def getMessage(self):
        m = self.sio.readline()#读取一行数据
        # m = m.decode()
        # print(m, flush=True)
        # 同时保存到文件
        # with open('nmea_log.txt', 'a') as f:
        #     f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {m}\n")
        msg = pynmea2.parse(m)#解析数据
        if msg.sentence_type == "GGA":
            self.parse_GGA(msg)
            return True
        elif msg.sentence_type == "GSV":
            self.parse_GSV(msg,m)
            return True
        elif msg.sentence_type == 'RMC':
            self.parse_RMC(msg)
            return True
        elif msg.sentence_type == 'GLL':
            self.parse_GLL(msg) 
            return True
        else:
            return False    
        
    def getSerialMessage(self):
        sm = self.serialPort.readline()
        print(sm)

    def get_location_dict(self):
        return self.location_dict

    def get_GSV_dict(self):
        self.GSV_info['receiver_running'] = self.running
        return self.GSV_info

    # def __startReceive(self):
    #     errCount = 0
    #     while self.running:
    #         # self.infoUpdated = False
    #         try:
    #             print(1)
    #             if self.getMessage():
    #                 errCount = 0
    #                 self.infoUpdated = True
    #                 self.err_message = None
    #         except Exception as e:

    #             errCount += 1
    #             if errCount > 200:
    #                 self.running = False
    #                 self.err_message = e

    def __startReceive(self):
        errCount = 0
        while self.running:
            try:
                if self.getMessage():
                    errCount = 0
                    self.infoUpdated = True
                    self.err_message = None
            except Exception as e:
                # 添加详细错误记录
                error_type = type(e).__name__
                error_msg = str(e)
                print(f"接收错误: {error_type} - {error_msg}")
                
                # 区分不同类型的错误
                if isinstance(e, (pynmea2.ParseError, UnicodeDecodeError)):
                    # 解析错误不计入严重错误
                    print("NMEA解析错误，不增加错误计数")
                else:
                    errCount += 1
                    print(f"错误计数增加: {errCount}/200")
                
                if errCount > 200:
                    print(f"错误计数超限，停止接收线程")
                    self.running = False
                    self.err_message = e

    def startReceiveMessage(self):
        self.running = True
        self.message_thread = threading.Thread(target=self.__startReceive,daemon=True)
        self.message_thread.start() 

    def parse_GGA(self, msg):
        # self.location_dict['update_time'] = msg.datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.location_dict['receiver_running'] = self.running
        # 格式化经纬度高度到固定小数位
        formatted_lat = round(msg.latitude, 6)  # 纬度保留6位小数
        formatted_lon = round(msg.longitude, 6)  # 经度保留6位小数
        # 计算椭球高度并格式化
        altitude = float(msg.altitude) if msg.altitude else 0
        geo_sep = float(msg.geo_sep) if msg.geo_sep else 0
        formatted_alt = round(altitude + geo_sep, 3)  # 高度保留3位小数
        self.location_dict['lat_deg'] = formatted_lat
        self.location_dict['lon_deg'] = formatted_lon
        self.location_dict['alt'] = formatted_alt
        self.location_dict['isValid'] = msg.is_valid
        self.location_dict['message'] = str(msg)
        self.location_dict['num_sats'] = msg.num_sats
        self.location_dict['err_message'] = self.err_message

    def parse_RMC(self, msg):
        self.location_dict['receiver_running'] = self.running
        
        # 格式化经纬度
        formatted_lat = round(msg.latitude, 6)
        formatted_lon = round(msg.longitude, 6)
        
        self.location_dict['lat_deg'] = formatted_lat
        self.location_dict['lon_deg'] = formatted_lon
        self.location_dict['datetime'] = msg.datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.location_dict['isValid'] = msg.is_valid
        self.location_dict['message'] = str(msg)
        self.location_dict['err_message'] = self.err_message
        self.location_dict['speed'] = round(msg.spd_over_grnd, 2) if msg.spd_over_grnd else 0
        
    def parse_GLL(self, msg):
        self.location_dict['receiver_running'] = self.running
        
        # 格式化经纬度
        formatted_lat = round(msg.latitude, 6)
        formatted_lon = round(msg.longitude, 6)
        
        self.location_dict['lat_deg'] = formatted_lat
        self.location_dict['lon_deg'] = formatted_lon
        self.location_dict['isValid'] = msg.is_valid
        self.location_dict['message'] = str(msg)
        self.location_dict['err_message'] = self.err_message

    def parse_GSV(self,msg,line): 
        num_sv_in_view = int(msg.num_sv_in_view)
           
        if 'GP' in line:
            self.GSV_info['num_sv_in_view']['GPS'] = num_sv_in_view
        elif 'BD' in line or 'GB' in line:
            self.GSV_info['num_sv_in_view']['BeiDou'] = num_sv_in_view 
        elif 'GL' in line:
            self.GSV_info['num_sv_in_view']['Galileo'] = num_sv_in_view
        elif 'GA' in line:
            self.GSV_info['num_sv_in_view']['GLONASS'] = num_sv_in_view 
            
        
        self.GSV_info['num_sv_in_view']['all'] = self.GSV_info['num_sv_in_view']['GPS']+self.GSV_info['num_sv_in_view']['BeiDou']+self.GSV_info['num_sv_in_view']['Galileo']+self.GSV_info['num_sv_in_view']['GLONASS']
    
    def sendMessage(self,message):
        self.sio.write(message)
    
    @staticmethod
    def parse_lat(lat,dir):
        deg = lat//100
        min_ = (lat-deg*100)/60 
        lat = deg + min_    
        if dir == 'S':
            lat = -lat
        return lat  
    
    @staticmethod
    def parse_lon(lon,dir):
        deg = lon//100
        min_ = (lon-deg*100)/60 
        lon = deg + min_    
        if dir == 'W':
            lon = -lon
        return lon  