import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask,request
from flask_restful import Api,Resource,fields,marshal_with,reqparse
from funcs import * 
import json,traceback
from common.logger import Log

sim = MySimulator()
pathTrajectory = PathTrajectory()
antennaModel = AntennaModel()

app = Flask(__name__)
api = Api(app)
rsv = Receiver()

request_json = {
    "simulatorIP": "127.0.0.1",# 仿真器的 IP 地址，通常是本地地址或远程仿真器的地址
    "mode": "standard",## 模式类型，可能有 "standard"（标准模式）和其他模式（如 "custom" 或 "advanced"）
    "standardScene": "", # 标准场景的名称或标识符，用于指定仿真时使用的默认场景。为空表示没有指定特定场景 ClearSky/UrbanCanyon/None
    "standardSignal":"",# 标准信号类型或信号源，可能是仿真器使用的默认信号类型。为空表示没有特定信号 Full,BeiDou
    "env": "", # 环境设置，如温度、湿度、气压等环境参数。为空表示默认环境设置 ClearSky/UrbanCanyon/None
    "signals": [], # 信号列表，可能包含多个信号源或不同类型的信号，供仿真过程使用
    "pathTrajectory": "",#  static/dynamic
    "startLla": [], # 启动时的经纬度和高度（Latitude, Longitude, Altitude），通常用于设置仿真物体的初始位置
    "orientation": [],   # 初始方位角（例如，俯仰角、滚转角、航向角），用于设定仿真物体的初始朝向
    "startTime": "", # start time:unix timestamp,None for current time
    "customizedPath": [],# 定制路径，允许用户定义自定义的仿真路径，作为一个数组或列表提供
    "simulatorControl": "start",# 仿真器控制指令，通常有 "start"（启动）、"stop"（停止）等，表示仿真器操作状态
    "radioType":"",# 无线电类型，可能影响仿真中的通信方式或信号传播模型"NoneRT","DTA-2115B","DTA-2116"
    "deviceserialnum":"",#设备序列号
    "decivetype":"",#设备类型
    "externalattenuation":"",#外部衰减
    "dc_block_mounting":"",#隔直器安装
    "comPort":"",#串口号
    "baudRate":"",#波特率
    "byteSize":"",#字节大小
    "stopBite":"",#停止位
    "dut_connection_mode":"",#DUT连接方式
    "dut_IP":"",#DUT IP地址以太网模式
    "dut_port":"",#DUT端口以太网模式
    "output_reference_power":"",#输出基准功率
}
   

def verification(args,param):
    allowed_scenes = ["ClearSky", "UrbanCanyon", "None"]
    allowed_trajectories = ["static", "dynamic"]
    allowed_simulatorControl = ["start", "stop"]
    allowed_signals = ["L1CA","L1C","L1P","G1","E1","B1","B1C","SBASL1","QZSSL1CA","QZSSL1CB","QZSSL1C","QZSSL1S","L2C","L2P","L5","G2","E5a","E5b","B2","B2a","B3I","SBASL5","QZSSL2C","QZSSL5","QZSSL5S","NAVICL5"]
    allowed_radioType = ["NoneRT","DTA-2115B","DTA-2116"]
    allowed_standardSignal = ["Full","BeiDou"]  
    allowed_controlFunction = ["active","globalPowerOffset","setManualPowerOffsetForSV"]
    if param == "StandardScene":
        if args[param] not in allowed_scenes:
            return False
    elif param == "pathTrajectory":
        if args[param] not in allowed_trajectories:
            return False
    elif param == "startLla":
        if args[param] is None:
            return False
        if len(args[param]) != 3:
            return False
        for i in range(3):
            if type(args[param][i]) is not float:
                return False 
    elif param == "orientation":
        if args[param] is None:
            return False
        if len(args[param]) != 3:
            return False
        for i in range(3):
            if type(args[param][i]) is not float:
                return False
    elif param == "simulatorControl":
        if args[param] not in allowed_simulatorControl:
            return False   
    elif param == "customizedPath":
        try:
            for path in args[param]:
                json.loads(path.replace("'",'"'))
        except:
            return False
    elif param == "signals":
        for sig in args[param]:
            if sig not in allowed_signals:
                return False   
    elif param == "radioType":
        if args[param] not in allowed_radioType:
            return False   
    elif param == "standardSignal":
        if args[param] not in allowed_standardSignal:
            return False    
    elif param == "controlFunction":
        if args[param] not in allowed_controlFunction:
            return False    
    elif param == 'startTime':
        # print(args[param])
        if args[param][0] is None:
            return True
        elif type(args[param]) is str:
            try:
                r = eval(args[param])
                if len(r)>=6:
                    return True
                else:
                    return False    
            except Exception as e:
                return False
        elif type(args[param]) is list:
            if len(args[param])>=6:
                return True
            else:
                return False    
    
    return True   

class StandardScene(Resource):#标准skydel模拟器参数设置
    
    resource_fields = {
        'status': fields.String,
        'message': fields.String}

    @marshal_with(resource_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("mode",type=str,help="mode: standard/customized",required=True)  
        parser.add_argument("simulatorIP",type=str,help="simulator IP address is necessary",required=True)  
        parser.add_argument("standardScene",type=str,help="standard scene:ClearSky/UrbanCanyon/None",required=True)
        parser.add_argument("pathTrajectory",type=str,help="path trajectory:static/dynamic",required=True)
        parser.add_argument("startLla",type=float, help="start lla:[latitude,longitude,altitude]",required=True, action='append')
        parser.add_argument("startTime",type = int,help="start time:unix timestamp,None for current time",action = 'append')
        parser.add_argument("orientation",type = float,help="orientation:[yaw,pitch,roll]",action='append') 
        parser.add_argument("radioType",type=str,help="radioType:NoneRT, DTA-2115B,DTA-2116 X300 or N310")
        parser.add_argument("signalStrengthModel",type=bool,help="signalStrengthModel:True/False")
        parser.add_argument("standardSignal",type=str,help="standardSignal:Full,BeiDou" )
        parser.add_argument("GlobalPowerOffset",type=float,help="GlobalPowerOffset:dBm")    
        
        args = parser.parse_args()
        # print(args) 
        if args["mode"] != "standard":
            return {"status":"failed","message":"Only support standard mode"}
         
        if verification(args, "standardScene") == False:
            return {"status":"failed","message":"Wrong input of StandardScene"} 
        if verification(args, "pathTrajectory") == False:
            return {"status":"failed","message":"Wrong input of pathTrajectory"}
        if verification(args, "startLla") == False:
            return {"status":"failed","message":"Wrong input of startLla"} 
        if verification(args,"radioType") == False: 
            return {"status":"failed","message":"Wrong input of radioType"} 
        if verification(args,'startTime') == False:
            return {"status":"failed","message":"Wrong input of startTime"} 
         
        try:
            sim.skydelIpAddress = args["simulatorIP"]
            if not sim.simulator.isConnected():  
                if not sim.simulator_connect():
                    return {"status":"failed","message":"Simulator connect failed"}
            try:
                sim.simulator.stop()
            except Exception as e:
                pass
            sim.radioType = args["radioType"]   
            if args["signalStrengthModel"]  != None:
                sim.signalStrengthModel = args["signalStrengthModel"]   
            sim.pathTrajectoryGenerator.LAT = args["startLla"][0]
            sim.pathTrajectoryGenerator.LONG = args["startLla"][1]
            sim.pathTrajectoryGenerator.ALT = args["startLla"][2]
            sim.startTime = args['startTime'] if args['startTime'][0] != None else None    

            
            if args['standardSignal'] == "Full":
                sim.setSignalFull()
            elif args['standardSignal'] == "BeiDou":
                sim.setSignalBeiDou()      

            if sim.signalStrengthModel == False:
                signals = sim.LOWERL+sim.UPPERL
                signals.remove("SBASL5")
                signals.remove("SBASL1")
                
                sim.setSignalPowerOffset(signals,0)
            if args['standardScene'] == "ClearSky":
                sim.setAntennaClearSky()
            elif args['standardScene'] == "UrbanCanyon":
                sim.setAntennaUrbanCanyon()
            elif args['standardScene'] == "None":
                sim.setAntennaNone()
            


            if args['pathTrajectory'] == "dynamic":
                sim.setDynamic()
            elif args['pathTrajectory'] == "static":
                if verification(args,"orientation"):
                    sim.pathTrajectoryGenerator.YAW = args["orientation"][0]
                    sim.pathTrajectoryGenerator.PITCH = args["orientation"][1]
                    sim.pathTrajectoryGenerator.ROLL = args["orientation"][2]
                sim.setStatic() 
            sim.setGlobalPowerOffset(args["GlobalPowerOffset"])
            # sim.simulator_disconnect()
            return {"status":"success","message":"Standard scene added"}

        except Exception as e:
            # sim.simulator_disconnect()
            return {"status":"failed","message":"Error: "+str(e)}   
            
class CustomizedPath(Resource):#定制skydel模拟器参数
    resource_fields = {
        'status': fields.String,
        'message': fields.String}
    
    @marshal_with(resource_fields)
    def post(self,data):        
        parser = reqparse.RequestParser()
        parser.add_argument("simulatorIP",type=str,help="simulator IP address is necessary")  
        parser.add_argument("longitude",type=float,help="longitude")
        parser.add_argument("latitude",type=float,help="latitude")
        parser.add_argument("altitude",type=float,help="altitude")
        parser.add_argument("startTime",type = int,help="start time:unix timestamp,None for current time",action = 'append')
        parser.add_argument("env",type=str,help="env:ClearSky/UrbanCanyon/None")
        parser.add_argument("signals",
                            type=str,
                            help="signal:L1CA,L1C,L1P,G1,E1,B1,B1C,SBASL1,QZSSL1CA,QZSSL1CB,QZSSL1C,QZSSL1S,L2C,L2P,L5,G2,E5a,E5b,B2,B2a,B3I,SBASL5,QZSSL2C,QZSSL5,QZSSL5S,NAVICL5",   
                            action='append')
        parser.add_argument("customizedPath",
                            type=str,
                            help='customizedPath:[{"type":"straightLine/arc/static","timeStep":0.1,"directionMatrix":[0,1],"initialVelocity":30,"finalVelocity":30,"accelerationDistance":0,"travelTime":300,"radius":20,"rotationDirection":"left/right","lastDirectionMatrix":[0,1]}]',
                            action = 'append')  
        parser.add_argument("radioType",type=str,help="radioType:NoneRT, DTA-2115B,DTA-2116")
        parser.add_argument("GlobalPowerOffset",type=float,help="GlobalPowerOffset:dBm")
        parser.add_argument("propagation_model",type=str)#传播模型
        parser.add_argument("duration_time",type=int,help="duration_time")#持续时间
        parser.add_argument("decivetype",type=str,help="decivetype")
        parser.add_argument("deviceserialnum",type=str,help="deviceserialnum")  
        parser.add_argument("externalattenuation",type=float, help="externalattenuation")
        parser.add_argument("dc_block_mounting",type = int,help="dc_block_mounting")
        parser.add_argument("output_reference_power",type = int,help="output_reference_power")#输出基准功率
        parser.add_argument("systemnum",type = int,help="system's num")#卫星数量


        args = parser.parse_args()
        if data == "connect":
            try:
                sim.skydelIpAddress = args["simulatorIP"]
                try:
                    sim.simulator_disconnect()
                except Exception as e:
                    pass    
                if not sim.simulator.isConnected():  # 如果仿真器未连接
                    if not sim.simulator_connect():  # 连接仿真器，如果返回 False，表示连接失败。
                        Log().logger.error(f"服务器连接skydel仿真器失败")
                        return {"status":"failed","message":"Simulator connect failed"}
                try:
                    sim.simulator.stop()
                except Exception as e:
                    pass
                sim.decivetype=args["decivetype"]
                if sim.decivetype=='GSG-7C':
                    sim.radioType='DTA-2116'
                elif sim.decivetype=='GSG-8C':
                    sim.radioType='DTA-2115B'
                elif sim.decivetype=='GSG-8Gen2':
                    sim.radioType='DTA-2116'
                elif sim.decivetype=='SSE':
                    sim.radioType='NoneRT'
                else:
                    Log().logger.error(f"GNSS设备类型错误,应该为GSG-7C,GSG-8C,GSG-8Gen2,SSE")
                    return {"status":"failed","message":"decivetype error: "}
                sim.deviceserialnum=args["deviceserialnum"]
                sim.externalattenuation=args["externalattenuation"]
                sim.dc_block_mounting=args["dc_block_mounting"]
                Log().logger.info(f"skydel仿真器连接成功,设备序列号：{sim.deviceserialnum},外部衰减：{sim.externalattenuation},隔直器安装：{sim.dc_block_mounting}")
                return {"status":"success","message":"skydel connect successfully"}
            except Exception as e:
            # sim.simulator_disconnect()
                traceback.print_exc(e)
                Log().logger.error(f"skydel连接失败:{str(e)}")
                return {"status":"failed","message":"Error: "+str(e)}
            
        elif data == "frequencyset":
            if verification(args, "signals") == False:
                Log().logger.error(f"信号源设置错误，应该为L1CA,L1C,L1P,G1,E1,B1,B1C,SBASL1,QZSSL1CA,QZSSL1CB,QZSSL1C,QZSSL1S,L2C,L2P,L5,G2,E5a,E5b,B2,B2a,B3I,SBASL5,QZSSL2C,QZSSL5,QZSSL5S,NAVICL5")
                return {"status":"failed","message":"Wrong input of signals"}   
            if verification(args,'startTime') == False:
                Log().logger.error(f"startTime设置错误")
                return {"status":"failed","message":"Wrong input of startTime"} 
            
            try:
                if not sim.simulator.isConnected():  
                    if not sim.simulator_connect():
                        Log().logger.error(f"skydel连接断开")
                        return {"status":"failed","message":"Simulator connect failed"}
                sim.duration_time=args["duration_time"]
                sim.contorl=args["propagation_model"]
                sim.startTime = args['startTime'] if args['startTime'][0] != None else None
                sim.systemnum=args["systemnum"]    
                sim.setSignals(args["signals"])
                Log().logger.info(f"信号频点设置成功")
                sim.setSystemnum()
                Log().logger.info(f"卫星数量设置成功")
                return {"status":"success","message":"skydel frequency set successfully"}
            except Exception as e:
            # sim.simulator_disconnect()
                traceback.print_exc(e)
                Log().logger.error(f"信号频点或卫星数量设置失败:{str(e)}")
                return {"status":"failed","message":"Error: "+str(e)}
            
        elif data == "offset":
            if not verification(args,"output_reference_power"):
                Log().logger.error(f"输出基准功率设置错误")
                return {"status":"failed","message":"Wrong input of output_reference_power"}
            try:
                sim.output_reference_power=args["output_reference_power"]
                if sim.signalStrengthModel == False:
                    signals = sim.LOWERL+sim.UPPERL
                    signals.remove("SBASL5")
                    signals.remove("SBASL1")
                    sim.setSignalPowerOffset(signals,0)
                sim.getSignalPowerOffset2()
                Log().logger.info(f"输出基准功率设置成功")
                return {"status":"success","message":"skydel offset set successfully"}
            except Exception as e:
                traceback.print_exc(e)
                Log().logger.error(f"输出基准功率设置失败:{str(e)}")
                return {"status":"failed","message":"Error: "+str(e)}
        

        elif data == "trajectory":
            if not verification(args,"customizedPath"):
                Log().logger.error(f"自定义路径设置错误")
                return {"status":"failed","message":"Wrong input of customizedPath"}
            # if args["mode"] != "customized":
            #     return {"status":"failed","message":"Only support customized mode"} 
            # if verification(args, "startLla") == False:
            #     return {"status":"failed","message":"Wrong input of startLla"} 
            
            
            try:
                # try:
                #     sim.simulator_disconnect()
                # except Exception as e:
                #     pass    
                if not sim.simulator.isConnected():  
                    if not sim.simulator_connect():
                        Log().logger.error(f"skydel连接断开")
                        return {"status":"failed","message":"Simulator connect failed"}
                # try:
                #     sim.simulator.stop()
                # except Exception as e:
                #     pass
                # sim.radioType = args["radioType"]   
                # sim.startTime = args['startTime'] if args['startTime'][0] != None else None    
                
                # if args["signalStrengthModel"]  != None:
                #     sim.signalStrengthModel = args["signalStrengthModel"] 
                
                # sim.setSignals(args["signals"])
                
                
                
                # if sim.signalStrengthModel == False:
                #     signals = sim.LOWERL+sim.UPPERL
                #     signals.remove("SBASL5")
                #     signals.remove("SBASL1")
                    
                #     sim.setSignalPowerOffset(signals,0)
                    
                sim.pathTrajectoryGenerator.LAT = args["longitude"]
                sim.pathTrajectoryGenerator.LONG = args["latitude"]
                sim.pathTrajectoryGenerator.ALT = args["altitude"]


                # if args['env'] == "ClearSky":
                #     sim.setAntennaClearSky()
                # elif args['env'] == "UrbanCanyon":
                #     sim.setAntennaUrbanCanyon()
                # elif args['env'] == "None":
                #     sim.setAntennaNone()

                sim.customizedTest(args["customizedPath"])

                # sim.simulator_disconnect()
                Log().logger.info(f"自定义路径设置成功")
                return {"status":"success","message":"Customized path added"}

            except Exception as e:
                # sim.simulator_disconnect()
                traceback.print_exc(e)
                Log().logger.error(f"自定义路径设置失败:{str(e)}")
                return {"status":"failed","message":"Error: "+str(e)}
        
class SimulatorControl(Resource):#控制skydel仿真器
    resource_fields = {
        'status': fields.String,
        'message': fields.String}
    
    @marshal_with(resource_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("controlFunction",type = str,help="controlFunction:active",required=True)
        parser.add_argument("simulatorControl",type=str,help="simulatorControl:start/stop")
        parser.add_argument("Offset",type =  int,help="Offset:-45~30dB or -45~10dB")
        parser.add_argument("svID",type=int,help="svID:1~64")
        parser.add_argument("system",type=str,help = "system:GPS/GLONASS/Galileo/BeiDou")
        args = parser.parse_args()
        if verification(args,"controlFunction") == False:
            Log().logger.error(f"controlFunction设置错误")
            return {"status":"failed","message":"Wrong input of controlFunction"}   
        try:
            if not sim.simulator.isConnected():  
                if not sim.simulator_connect():
                    return {"status":"failed","message":"Simulator connect failed"}
            if args["controlFunction"] == "active":
                if args["simulatorControl"] == "start":
                    try:
                        sim.startSimulation()
                        Log().logger.info(f"仿真器启动成功")
                        return {"status":"success","message":"Simulator started"}
                    except Exception as e:
                        # sim.simulator_disconnect()
                        Log().logger.error(f"仿真器启动失败:{str(e)}")
                        return {"status":"failed","message":"Error: "+str(e)}   
                elif args["simulatorControl"] == "stop":
                    sim.stopSimulation()
                    sim.simulator_disconnect()  
                    Log().logger.info(f"仿真器停止成功")
                    return {"status":"success","message":"Simulator stopped"}   
                else:
                    Log().logger.error(f"simulatorControl设置错误")
                    return {"status":"failed","message":"Wrong input of simulatorControl"}
            elif args["controlFunction"] == "globalPowerOffset":
                sim.setGlobalPowerOffset(args["Offset"])
                sim.simulator_disconnect()
                Log().logger.info(f"全局功率偏移设置成功")
                return {"status":"success","message":"Global power offset set"}
            elif args["controlFunction"] == "setManualPowerOffsetForSV":
                sim.setManualPowerOffsetForSV(args["system"],args["svID"],args["Offset"])
                sim.simulator_disconnect()
                Log().logger.info(f"{args["system"]}星座{args["svID"]}号功率偏移设置成功")
                return {"status":"success","message":"Manual power offset set"}
            else:
                Log().logger.error(f"controlFunction设置错误")
                return {"status":"failed","message":"Wrong input of controlFunction"}
        except Exception as e:
            if sim.simulator.isConnected():
                sim.simulator_disconnect()
            Log().logger.error(f"仿真器操作失败:{str(e)}")
            return {"status":"failed","message":"Error: "+str(e)}
 
class VehicleInfo(Resource):#获取skydel模拟数据

    def get(self):
        if not sim.simulator.isConnected():  
            if not sim.simulator_connect():
                Log().logger.error(f"skydel连接断开")
                return {"status":"failed","message":"Simulator connect failed"}
        try:
            lla,odometer,speed,yaw,pitch,roll,pc,time = sim.getVehicleInfo()
            # sim.simulator_disconnect()
            return {"status":"success",
                    "message":{
                        'sim_current_time':time,
                        "latitude":lla.latDeg(),#纬度
                        "longitude":lla.lonDeg(),#经度
                        "altitude":lla.alt,#高度
                        "odometer":odometer,#里程
                        "speed":speed,#速度
                        "yaw":yaw,#偏航角
                        "pitch":pitch,#俯仰角
                        "roll":roll, #滚转角
                        "pc":pc#输出基准功率
                        },
                    }
        except Exception as e:
            # sim.simulator_disconnect()
            Log().logger.error(f"获取skydel模拟数据失败:{str(e)}")
            return {"status":"failed","message":"Error: "+str(e)}
                   
class SimulatorInfo(Resource):#获取可见卫星svid
    def get(self):
        pass
    def post(self):
        parser = reqparse.RequestParser()
        # parser.add_argument("simulatorIP",type=str,help="simulator IP address is necessary",required=True)  
        # parser.add_argument("type",type=str,help="...")
        parser.add_argument("system",type=str,help = "system:GPS,BeiDou,GLONASS,Galileo,SBAS,QZSS,Navic")
        args = parser.parse_args()
        # sim.skydelIpAddress = args["simulatorIP"]  
        # if not sim.simulator.isConnected():  
        #     if not sim.simulator_connect():
        #         return {"status":"failed","message":"Simulator connect failed"}
        try:       
            svids = sim.getVisiableSV(args["system"])
            numSV=len(svids)
            Log().logger.info(f"可见卫星svid获取成功")
            return {"status":"success","message":svids,"numSV":numSV} 
        
        except Exception as e:
            # sim.simulator_disconnect()
            Log().logger.error(f"可见卫星svid获取失败:{str(e)}")
            return {"status":"failed","message":"Error: "+str(e)}    

class SignalPower(Resource):#设置skydel全局，特定星座，特定星座的某颗卫星信号功率
    
    def verify(args,param): 
        
        allowed_type = ["global","signal","svid"]   
        allowed_signalList = ["L1CA","L1C","L1P","G1","E1","B1","B1C","SBASL1","QZSSL1CA","QZSSL1CB","QZSSL1C","QZSSL1S","L2C","L2P","L5","G2","E5a","E5b","B2","B2a","SBASL5","QZSSL2C","QZSSL5","QZSSL5S","NAVICL5"]
        allowed_system = ["GPS","GLONASS","Galileo","BeiDou"]   
        if param == "type":
            if args[param] not in allowed_type: 
                return False    
        elif param == "signalList":
            for signal in args[param]:
                if signal not in allowed_signalList:
                    return False    
        elif param == "system": 
            if args[param] not in allowed_system:   
                return False
            
        return True
    
    def get(self):
        pass
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("simulatorIP",type=str,help="simulator IP address is necessary",required=True)  
        parser.add_argument("type",type= str,help="type:global/signal/svid",required = True)
        parser.add_argument("value",type= int,help="value:dBm",required = True) 
        parser.add_argument("svID",type= int,help="svID:1~64")
        parser.add_argument("signalList",type=str,action='append',help = "L1CA,L1C,L1P,G1,E1,B1,B1C,SBASL1,QZSSL1CA,QZSSL1CB,QZSSL1C,QZSSL1S,L2C,L2P,L5,G2,E5a,E5b,B2,B2a,SBASL5,QZSSL2C,QZSSL5,QZSSL5S,NAVICL5")
        parser.add_argument("system",type=str,help = "system:GPS/GLONASS/Galileo/BeiDou")   
        args = parser.parse_args()
        if SignalPower.verify(args,"type") == False:
            Log().logger.error(f"type设置错误")
            return {"status":"failed","message":"Wrong input of type"}  
        
    
        if SignalPower.verify(args,"system") == False:
            Log().logger.error(f"system设置错误")
            return {"status":"failed","message":"Wrong input of system"}    

            
        sim.skydelIpAddress = args["simulatorIP"]  
        if not sim.simulator.isConnected():  
            if not sim.simulator_connect():
                Log().logger.error(f"skydel连接断开")
                return {"status":"failed","message":"Simulator connect failed"}
        try:
            if args["type"] == "global":    
                sim.setGlobalPowerOffset(args["value"]) 
                # sim.simulator_disconnect()
                Log().logger.info(f"全局功率偏移设置成功")
                return {"status":"success","message":"Global power offset set"}
            elif args["type"] == "signal":
                sim.setSignalPowerOffset(args["signalList"],args["value"])    
                # sim.simulator_disconnect()  
                Log().logger.info(f"信号功率设置成功")
                return {"status":"success","message":"Signal power set"}    
            elif args["type"] == "svid":    
                sim.setManualPowerOffsetForSV(args["system"],args["svID"],args["value"])    
                # sim.simulator_disconnect()
                Log().logger.info(f"{args["system"]}星座{args["svID"]}号功率偏移设置成功")
                return {"status":"success","message":"Manual power offset set"} 
        except Exception as e:
            # sim.simulator_disconnect()
            # traceback.print_exc(e)
            Log().logger.error(f"功率设置失败:{str(e)}")
            return {"status":"failed","message":"Error: "+str(e)}   

class SignalPowerInfo(Resource):#获取skydel全局，特定星座，特定星座的某颗卫星信号功率
    def verify(args,param): 
        
        allowed_type = ["global","signal","svid"]   
        allowed_signalList = ["L1CA","L1C","L1P","G1","E1","B1","B1C","SBASL1","QZSSL1CA","QZSSL1CB","QZSSL1C","QZSSL1S","L2C","L2P","L5","G2","E5a","E5b","B2","B2a","SBASL5","QZSSL2C","QZSSL5","QZSSL5S","NAVICL5"]
        allowed_system = ["GPS","GLONASS","Galileo","BeiDou"]   
        if param == "type":
            if args[param] not in allowed_type: 
                return False    
        elif param == "signal":
            if args[param] not in allowed_signalList:
                return False
        elif param == "system": 
            if args[param] not in allowed_system:   
                return False
            
        return True
      
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("simulatorIP",type=str,help="simulator IP address is necessary",required=True)  
        parser.add_argument("type",type= str,help="type:global/signal/svid",required = True)
        parser.add_argument("svID",type= int,help="svID:0~64")
        parser.add_argument("signal",type=str,help = "L1CA,L1C,L1P,G1,E1,B1,B1C,SBASL1,QZSSL1CA,QZSSL1CB,QZSSL1C,QZSSL1S,L2C,L2P,L5,G2,E5a,E5b,B2,B2a,SBASL5,QZSSL2C,QZSSL5,QZSSL5S,NAVICL5")
        parser.add_argument("system",type=str,help = "system:GPS/GLONASS/Galileo/BeiDou")   
        args = parser.parse_args()       
        if SignalPowerInfo.verify(args,"type") == False:
            Log().logger.error(f"type设置错误")
            return {"status":"failed","message":"Wrong input of type"}  
          
        sim.skydelIpAddress = args["simulatorIP"]  
        if not sim.simulator.isConnected():  
            if not sim.simulator_connect():
                Log().logger.error(f"skydel连接断开")
                return {"status":"failed","message":"Simulator connect failed"}
        try:
            if args["type"] == "global":    
                offset = sim.getGlobalPowerOffset()#获取全局功率偏移
                # sim.simulator_disconnect()
                Log().logger.info(f"全局功率偏移获取成功")
                return {"status":"success","message":offset}
            
            elif args["type"] == "signal":
                offset = sim.getSignalPowerOffset(args["signal"]) #获取特定信号功率偏移
                # sim.simulator_disconnect()
                Log().logger.info(f"{args["signal"]}信号功率偏移获取成功")
                return {"status":"success","message":offset}
            
            elif args["type"] == "svid":
                if args['svID'] == 0:
                    svid = sim.getVisiableSV(args["system"])   #获取可见卫星svid
                    infoList = []
                    num=0
                    for i in svid:
                        infoList.append(sim.getManualPowerOffsetForSV(args["system"],i)) 
                        num=i
                    # sim.simulator_disconnect()
                    Log().logger.info(f"{args["system"]}星座卫星功率偏移获取成功")
                    return {"status":"success","message":infoList,"svidnum":num}   
                else:
                    offset = sim.getManualPowerOffsetForSV(args["system"],args["svID"]) #获取特定卫星功率偏移
                    # sim.simulator_disconnect()
                    Log().logger.info(f"{args["system"]}星座{args["svID"]}号功率偏移获取成功")
                    return {"status":"success","message":offset}
        except Exception as e:
            # sim.simulator_disconnect()
            Log().logger.error(f"功率获取失败:{str(e)}")
            return  {"status":"failed","message":"Error: "+str(e)}  
        
class ExReceiver(Resource):#接收器设置
    def get(self,data):
        
        if data == 'GSV':
            info_dict = rsv.get_GSV_dict()
        else:
            info_dict  = rsv.get_location_dict()

        Log().logger.info(f"接收器信息获取成功")
        return {"status":"success","message":info_dict} 
        
    def post(self,data):
        
        def verify(args,param):
            allowed_function = ['setser','setint','start','stop']
            if param == "function":
                if args[param] not in allowed_function:
                    return False    
            
            return True
            
        
        parser = reqparse.RequestParser()
        parser.add_argument("comPort",type=str,help="comPort")
        parser.add_argument('baudRate',type = int,help = 'baudRate')
        parser.add_argument('byteSize',type = float,help = 'byteSize')
        parser.add_argument('stopBites',type = int,help = 'stopBites')
        parser.add_argument('message',type = str,help = 'message to send')
        parser.add_argument('dutip',type = str,help = 'dutip')
        parser.add_argument('port',type = int,help = 'port')
        
        args = parser.parse_args()
        
    
        if data == "setser":#设置接收器串口
            try: 
               comPort = args.get('comPort')
               baudRate = args.get('baudRate')
               byteSize = args.get('byteSize')
               stopBites = args.get('stopBites')
               print(comPort,baudRate,byteSize,stopBites)
               if comPort and baudRate and byteSize and stopBites:
                   
                   rsv.comPort = comPort
                   rsv.baudRate = baudRate
                   rsv.byteSize = byteSize
                   rsv.stopBit = stopBites
                   
                   err = rsv.reset_com()
                   if err:
                       Log().logger.error(f"接收器串口设置失败")
                       return {"status":"failed","message":str(err)} 
                   Log().logger.info(f"接收器串口设置成功")
                   return {"status":"success","message":"dut serial set successfully"} 
               else:
                   Log().logger.error(f"接收器串口设置错误")
                   return {"status":"failed","message":"Wrong input of params"}
            except Exception as e:
                Log().logger.error(f"接收器串口设置失败:{str(e)}")
                return {"status":"failed","message":e}    
        
        elif data == "setint":#设置接收器IP
            try: 
               dut_IP = args.get('dutip')
               dut_port = args.get('port')
               if dut_IP and dut_port:
                   rsv.dut_IP = dut_IP
                   rsv.dut_port = dut_port

                   
                   err = rsv.reset_ip()
                   if err:
                       Log().logger.error(f"接收器连接失败")
                       return {"status":"failed","message":str(err)} 
                   Log().logger.info(f"接收器连接成功")
                   return {"status":"success","message":"dut http set successfully"} 
               else:   
                   Log().logger.error(f"接收器IP设置错误")
                   return {"status":"failed","message":"Wrong input of params"}
            except Exception as e:
                Log().logger.error(f"接收器连接失败:{str(e)}")
                return {"status":"failed","message":e}               
        elif data == 'start':
            try:
                if rsv.serialPort:
                    rsv.startReceiveMessage()
                    time.sleep(1)
                    if rsv.message_thread.is_alive():
                        Log().logger.info(f"接收器成功接受数据")
                        return {"status":"success","message":"start successfully"}  
                    else:
                        Log().logger.error(f"接收器接受数据失败")
                        return{"status":"failed","message":"failed to start"}   
                else:
                    Log().logger.error(f"接收器串口未初始化")
                    return {"status":"failed","message":"Serial port is not initialized"}       
            except Exception as e:
                Log().logger.error(f"接收器接受数据失败:{str(e)}")
                return {"status":"failed","message":str(e)}  
        elif data == 'stop':
            rsv.running = False
            Log().logger.info(f"接收器停止接受数据")
            return {"status":"success","message":"stop successfully"}   
        elif data == 'send':
            msg = args['message']
            rsv.sendMessage(msg)
            Log().logger.info(f"给接收器发送数据成功")
            return {"status":"success","message":"send successfully"}   
        else:
            Log().logger.error(f"接收器设置错误")
            return {"status":"failed","message":"Wrong input of function"}  






api.add_resource(StandardScene, '/standard',endpoint = 'standard')
api.add_resource(SimulatorControl, '/simulatorcontrol',endpoint = 'simulatorcontrol')
api.add_resource(CustomizedPath, '/customized/<string:data>',endpoint = 'customized') 
api.add_resource(VehicleInfo, '/vehicleinfo',endpoint = 'vehicleinfo')  
api.add_resource(SignalPower,'/signalpower',endpoint='signalpower' )
api.add_resource(SignalPowerInfo,'/signalpowerinfo',endpoint = 'signalpowerinfo')   
api.add_resource(SimulatorInfo,'/simulatorinfo',endpoint = 'simulatorinfo') 
api.add_resource(ExReceiver,'/receiver/<string:data>',endpoint = 'receiver')  


if __name__ == '__main__':
    app.run(debug=True, port=5000) 



def runServer(port):
    app.run(port=port)
    









