from skydelsdx.units import Lla
from skydelsdx.units import Enu
from skydelsdx.units import toRadian
from skydelsdx.commands import *
from skydelsdx.commandexception import CommandException 
from datetime import datetime   
from serial import Serial

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
    
        self.path_list_deg = []
        self.push_list_radian = []
        # 统计总路径行驶时间
        self.runningTime = 0
    
    def __StraightLineTrajectory(self,initialVelocity,finalVelocity,accelerationDistance,travelTime,timeStep,directionMatrix):
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
                llaPos = self.ORIGIN.addEnu(Enu(self.lastX, self.lastY, self.lastZ))
                if speed != 0:
                    self.path_list_deg.append([speed,llaPos.latDeg(),llaPos.lonDeg(),llaPos.alt])
                    self.push_list_radian.append([speed,llaPos.lat,llaPos.lon,llaPos.alt])
                i+=timeStep         
        else:
            a = (finalVelocity**2 - initialVelocity**2) / (2 * accelerationDistance) #加速度
            # 计算直线加速轨迹
            t = (finalVelocity-initialVelocity)/a
            self.runningTime+=t
            i = 0.0
            while i<t:
              
                speed = initialVelocity + a * i
                self.lastX += ((speed - a * timeStep) * timeStep + 0.5 * a * timeStep*timeStep) * directionMatrix[0]
                self.lastY += ((speed - a * timeStep) * timeStep + 0.5 * a * timeStep*timeStep) * directionMatrix[1]
                llaPos = self.ORIGIN.addEnu(Enu(self.lastX, self.lastY, self.lastZ))
                if speed!=0:
                    self.path_list_deg.append([speed,llaPos.latDeg(),llaPos.lonDeg(),llaPos.alt])
                    self.push_list_radian.append([speed,llaPos.lat,llaPos.lon,llaPos.alt])
                i+=timeStep
        # print(self.path_list_deg)
    def __uniformArcTrajectory(self,speed,radius,rotationDirection,timeStep,lastDirectionMatrix):
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
        while True:
            angular+=vr*timeStep
            self.runningTime+=timeStep  
            if abs(angular) >=  math.pi/2:
                break  
            self.lastX = x0 + radius * math.sin(r+r_offset+angular)
            self.lastY = y0 + radius * math.cos(r+r_offset+angular)
            llaPos = self.ORIGIN.addEnu(Enu(self.lastX, self.lastY, self.lastZ))
            if speed!=0:
                self.path_list_deg.append([speed,llaPos.latDeg(),llaPos.lonDeg(),llaPos.alt])
                self.push_list_radian.append([speed,llaPos.lat,llaPos.lon,llaPos.alt])
    def __StaticTrajectory(self,travelTime,timeStep):
        speed = 0
        i = 0.0
        while True:
            if i > travelTime:
                break
            self.push_list_radian.append(speed,self.ORIGIN.lat,self.ORIGIN.lon,self.ORIGIN.alt)
            self.path_list_deg.append([speed,self.ORIGIN.latDeg(),self.ORIGIN.lonDeg(),self.ORIGIN.alt])
            
            
            i+= timeStep
        
    
    
    
    
    
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

    def generateCustomerRoute(self,routeList):
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
            if route['type'] == 'straightLine':
                self.__StraightLineTrajectory(initialVelocity=route['initialVelocity'],
                                              finalVelocity=route['finalVelocity'],
                                              accelerationDistance=route['accelerationDistance'],
                                              travelTime=route['travelTime'],
                                              timeStep=route['timeStep'],
                                              directionMatrix=route['directionMatrix'])
            elif route['type'] == 'arc':
                self.__uniformArcTrajectory(speed=route['initialVelocity'],
                                            radius=route['radius'],
                                            rotationDirection=route['rotationDirection'],
                                            timeStep=route['timeStep'],
                                            lastDirectionMatrix=route['lastDirectionMatrix'])   
            elif route['type'] == 'static':
                self.__StaticTrajectory(travelTime=route['travelTime'],
                                        timeStep=route['timeStep'])
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
        self.output_reference_power =  0  #输出基准功率

        self.gain = 0 #SDR增益
        self.globaloffset=0#全局偏移
        self.enabledSignal = []
        
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
        self.externalattenuation=None#外部衰减
        self.dc_block_mounting=None#直流阻塞安装
        


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

        self.simulator.call(EnableSignalStrengthModel(self.signalStrengthModel))    # 关闭信号强度模型
        self.simulator.call(SetVehicleAntennaGainCSV("", AntennaPatternType.AntennaNone, GNSSBand.L1, "Basic Antenna"))#设置天线增益为none
        self.simulator.call(SetVehicleAntennaGainCSV("", AntennaPatternType.AntennaNone, GNSSBand.L2, "Basic Antenna"))
        self.simulator.call(SetVehicleAntennaGainCSV("", AntennaPatternType.AntennaNone, GNSSBand.L5, "Basic Antenna"))
        self.simulator.call(SetVehicleAntennaGainCSV("", AntennaPatternType.AntennaNone, GNSSBand.E6, "Basic Antenna"))
        self.simulator.call(SetVehicleAntennaGainCSV("", AntennaPatternType.AntennaNone, GNSSBand.S, "Basic Antenna"))

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
        # self.simulator.call(SetDuration(3600))
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
            info = self.simulator.lastVehicleInfo()
            lla = info.ecef.toLla()
            yaw = info.attitude.yawDeg()
            pitch = info.attitude.pitchDeg()
            roll = info.attitude.rollDeg()  
        
        
            return lla,info.odometer,info.speed,yaw,pitch,roll
        else:
            raise Exception("No VehicleInfo,maybe the simulator didn't start.") 

    def customizedTest(self,routeList):
        self.__resetStartPoint()
        
        self.pathTrajectoryGenerator.generateCustomerRoute(routeList)
        # print(self.pathTrajectoryGenerator.push_list_radian)
        
        self.pushRouteNode(self.pathTrajectoryGenerator.push_list_radian)
        self.simulator.arm()    

    def setGlobalPowerOffset(self,offset:int):
        #-45---30
        self.simulator.call(SetGlobalPowerOffset(offset))
    
    def getSignalPowerOffset(self):
        self.globaloffset=-(-self.output_reference_power+self.skydel_Benchmark_Power-self.externalattenuation+self.gain)
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

    def reset_com(self):
        if self.serialPort is not None:
            if self.serialPort.isOpen():
                self.serialPort.close() 
        try:
            self.serialPort = Serial(port=self.comPort,baudrate= self.baudRate, timeout=5.0,bytesize=self.byteSize,stopbits=self.stopBit)
            self.sio = io.TextIOWrapper(io.BufferedRWPair(self.serialPort, self.serialPort))
            return None
        except Exception as e:
            return e
        
    def reset_ip(self):
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
        # print(m)
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

    def __startReceive(self):
        errCount = 0
        while self.running:
            # self.infoUpdated = False
            try:
                if self.getMessage():
                    errCount = 0
                    self.infoUpdated = True
                    self.err_message = None
            except Exception as e:
                errCount += 1
                if errCount > 50:
                    self.running = False
                    self.err_message = e

    def startReceiveMessage(self):
        self.running = True
        self.message_thread = threading.Thread(target=self.__startReceive,daemon=True)
        self.message_thread.start() 

    def parse_GGA(self,msg):
        self.location_dict['update_time'] = time.time()
        self.location_dict['receiver_running'] = self.running
        self.location_dict['lat_deg'] = msg.latitude
        self.location_dict['lon_deg'] = msg.longitude
        self.location_dict['alt'] = msg.altitude
        self.location_dict['isValid'] = msg.is_valid
        self.location_dict['message'] = str(msg)
        self.location_dict['num_sats'] = msg.num_sats
        self.location_dict['err_message'] = self.err_message
        self.location_dict['speed'] = msg.spd_over_grnd  # 提取速度信息

    def parse_RMC(self,msg):
        self.location_dict['update_time'] = time.time()
        
        self.location_dict['receiver_running'] = self.running
        self.location_dict['lat_deg'] = msg.latitude
        self.location_dict['lon_deg'] = msg.longitude
        self.location_dict['alt'] = msg.altitude
        self.location_dict['datetime'] = msg.datetime
        self.location_dict['isValid'] = msg.is_valid
        self.location_dict['message'] = str(msg)
        self.location_dict['err_message'] = self.err_message
        self.location_dict['speed'] = msg.spd_over_grnd  # 提取速度信息
        
    def parse_GLL(self,msg):
        self.location_dict['update_time'] = time.time()
        
        self.location_dict['receiver_running'] = self.running
        self.location_dict['lat_deg'] = msg.latitude
        self.location_dict['lon_deg'] = msg.longitude
        self.location_dict['alt'] = msg.altitude
        self.location_dict['isValid'] = msg.is_valid
        self.location_dict['message'] = str(msg)
        self.location_dict['err_message'] = self.err_message
        self.location_dict['speed'] = msg.spd_over_grnd  # 提取速度信息

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
            
        self.GSV_info['update_time'] = time.time()
        
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