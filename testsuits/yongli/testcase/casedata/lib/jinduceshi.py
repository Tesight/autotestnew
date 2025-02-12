import requests,json,time,math
import josn
import yaml
from filelock import FileLock
ESMAJ = 6378137.0 # Semi-major axis of Earth, meters
EFLAT = 0.00335281066474
ESMIN = ESMAJ * (1.0 - EFLAT)
EECC_SQUARED = (((ESMAJ*ESMAJ) - (ESMIN*ESMIN)) / (ESMAJ*ESMAJ))
Pi    = 3.1415926535898 # Pi used in the GPS coordinate

def sensitivity_test_loop(max_test_time =300,step = 1,continuous_length = 10,distance_threshold = 100,address = ''):
    time_diff = 0
    res_list = []
    time_start = time.time()
    return_message = {'status':None}
    return_message['time_start'] = time_start
    sim_lla = None
    rsv_lla = None
    while time_diff < max_test_time:
        time.sleep(step)
        try:
            sim_location = requests.get(url='http://'+address+'/vehicleinfo').json()
            rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
            time_stamp = time.time()
            
            if sim_location['status'] == 'success':
                sim_lla = Lla(
                    lat=toRadian(sim_location['message']['latitude']),
                    lon = toRadian(sim_location['message']['longitude']),
                    alt = sim_location['message']['altitude'])
                is_valid = rsv_location['message'].get('isValid')
                if is_valid:
                    rsv_lla = Lla(
                        lat=toRadian(rsv_location['message']['lat_deg']),
                        lon=toRadian(rsv_location['message']['lon_deg']),
                        alt=rsv_location['message']['alt'])
                    enu_res = rsv_lla.toEnu(sim_lla)
                    distance = math.sqrt(enu_res.east**2+enu_res.north**2+enu_res.up**2)
                    if distance > distance_threshold:
                        res_list = []
                    else:
                        res_list.append((distance,time_stamp))
                    if len(res_list) >= continuous_length:
                        return_message['status'] = 'success'
                        return_message['time_diff'] = time_diff
                        return_message['located_time'] = res_list[0][1]

                        return return_message
        except Exception as e:
            pass   
        time_diff = time.time() - time_start
    if sim_lla == None or rsv_lla == None:
        return_message['status'] = 'error'
        return_message['time_diff'] = time_diff
        return return_message
    return_message['status'] = 'fail'
    return_message['time_diff'] = time_diff
    return return_message 
        

def sensitivity_test(data_num =100,time_step = 30,address = ''):
    return_message = {'status':None}
    res_list = []
    sim_location = requests.get(url='http://'+address+'/vehicleinfo').json()
    try:
        if sim_location['status'] == 'success':
            sim_lla = Lla(
                lat=toRadian(sim_location['message']['latitude']),
                lon = toRadian(sim_location['message']['longitude']),
                alt = sim_location['message']['altitude'])
            for i in range(data_num):
                time.sleep(time_step)
                rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
                is_valid = rsv_location['message'].get('isValid')
                if is_valid:
                    rsv_lla = Lla(
                        lat=toRadian(rsv_location['message']['lat_deg']),
                        lon=toRadian(rsv_location['message']['lon_deg']),
                        alt=rsv_location['message']['alt'])
                    enu_res = rsv_lla.toEnu(sim_lla)
                    res_list.append(enu_res)
            if len(res_list)>0:
                sum_h = 0
                sum_v = 0
                for res_enu in res_list:
                    sum_h += res_enu.east**2+res_enu.north**2
                    sum_v += res_enu.up**2  
          
                return_message['status'] = 'success'
                return_message['result_mh'] = math.sqrt(sum_h/len(res_list))
                return_message['result_mv'] = math.sqrt(sum_v/len(res_list))
                return return_message   
        else:
            return_message['status'] = 'fail'
            return return_message   
    except Exception as e:
        return_message['status'] = 'error'
        return_message['message'] = str(e)
        return return_message   

   #静态定位误差             
def static_position_bias(data_num =900,time_step = 1,address = ''):#time_step取数间隔时间，addressIP地址,point为坐标
    return_message = {'status':None}
    res_list = []#存储ENU坐标
    result_bias=[]#存储平均坐标误差
    time_result_bias=[]#存储实时坐标误差
    count=0
    sim_location = requests.get(url='http://'+address+'/vehicleinfo').json()
    try:
        if sim_location['status'] == 'success':
            # 将数据存储在 YAML 文件中
            data = {        'sim_current_time':sim_location['message']['time'],
                            'sim_lat': sim_location['message']['latitude'],
                            'sim_lon': sim_location['message']['longitude'],
                            'sim_alt': sim_location['message']['altitude'],
                            'sim_v': 0,
                           
                        }
            with FileLock("静态定位精度参数.yaml.lock"):
              with open('静态定位精度参数.yaml', 'w') as file:
                yaml.dump(data, file)
            sim_lla = Lla(
                lat=toRadian(sim_location['message']['latitude']),
                lon = toRadian(sim_location['message']['longitude']),
                alt = sim_location['message']['altitude'])
            
            for i in range(data_num):
                time.sleep(time_step)
                rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
                is_valid = rsv_location['message'].get('isValid')#判断是否有效
                if is_valid:
                    rsv_lla = Lla(
                        lat=toRadian(rsv_location['message']['lat_deg']),
                        lon=toRadian(rsv_location['message']['lon_deg']),
                        alt=rsv_location['message']['alt'])
                    enu_res = rsv_lla.toEnu(sim_lla)
                    # res_list.append(enu_res)
                    # 将数据存储在 YAML 文件中
                    data = {        
                            'dut_current_time':rsv_location['message']['datetime'],
                            'dut_lat': rsv_location['message']['lat_deg'],
                            'dut_lon': rsv_location['message']['lon_deg'],
                            'dut_alt': rsv_location['message']['alt'],
                            'dut_v': 0,
                        }
                    with FileLock("静态定位精度参数.yaml.lock"):
                      with open('静态定位精度参数.yaml', 'w') as file:
                        yaml.dump(data, file)
                    h=enu_res.east**2+enu_res.north**2
                    v=enu_res.up**2
                    sum_h += h
                    sum_v += v
                    bias=math.sqrt(h+v)
                    biasx=math.sqrt(sum_h/(i+1)+sum_v/(i+1))
                    count=count+1
                    data = {        
                            'count': count,
                            'time': rsv_location['message']['datetime'],
                            'bias':  bias,#即时误差
                            'biasx': biasx,#平均误差
                        }
                    with FileLock("静态定位计算数据.yaml.lock"):
                      with open('静态定位计算数据.yaml', 'w') as file:
                        yaml.dump(data, file)
                    time_result_bias.append(bias)
                    result_bias.append(biasx)
                return_message['result_current_bias']=time_result_bias
                return_message['result_static_bias']=result_bias
                return_message['status'] = 'success'
                return_message['result_static_mbias'] = math.sqrt(sum_h/count+sum_v/count)#平均误差
                return return_message   
        else:
            return_message['status'] = 'fail'
            return return_message
    except Exception as e:
        return_message['status'] = 'error'
        return_message['message'] = str(e)
        return return_message   

      #动态定位误差          
def dunamic_position_bias(data_num =900,time_step = 1,address = ''):#time_step取数间隔时间，addressIP地址,point为坐标
    return_message = {'status':None}
    res_list = []#存储ENU坐标
    result_bias=[]#存储坐标误差
    result_mbias=[]#存储平均坐标误差
    try: 
        for i in range(data_num):
          time.sleep(time_step)
          sim_location = requests.get(url='http://'+address+'/vehicleinfo').json() 
          rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
          if sim_location['status'] == 'success':
            sim_lla = Lla(
                  lat=toRadian(sim_location['message']['latitude']),
                  lon = toRadian(sim_location['message']['longitude']),
                  alt = sim_location['message']['altitude'])
          is_valid = rsv_location['message'].get('isValid')#判断是否有效
          if is_valid:
            rsv_lla = Lla(
                  lat=toRadian(rsv_location['message']['lat_deg']),
                  lon=toRadian(rsv_location['message']['lon_deg']),
                  alt=rsv_location['message']['alt'])
            enu_res = rsv_lla.toEnu(sim_lla)
            res_list.append(enu_res)
        if len(res_list)>0:
                mtamp=0
                for i,res_enu in res_list:
                    sum_x = res_enu.east**2
                    sum_y = res_enu.north**2
                    sum_z = res_enu.up**2 
                    bias  = math.sqrt(sum_x+sum_y+sum_z)#即时误差
                    mtamp += bias#即时误差相加
                    mbias = mtamp/(i+1)#即时误差均值
                    result_bias.append(bias)
                    result_mbias.append(mbias)
                
                return_message['result_dynamic_bias']=result_bias
                return_message['status'] = 'success'
                return_message['result_dynamic_mbias'] = math.sqrt(sum_x+sum_y+sum_z)/len(res_list)#平均误差
                return return_message   
        else:
            return_message['status'] = 'fail'
            return return_message   
    except Exception as e:
        return_message['status'] = 'error'
        return_message['message'] = str(e)
        return return_message  

    #测数偏差
def speed_measurement_bias(data_num =900,time_step = 1,address = ''):#time_step取数间隔时间，addressIP地址,point为坐标
    return_message = {'status':None}
    res_listv = []#储存速度差
    result_v = []#存储误差均值
    try: 
        for i in range(data_num):
            time.sleep(time_step)
            sim_location = requests.get(url='http://'+address+'/vehicleinfo').json() 
            if sim_location['status'] == 'success':
              sim_v=sim_location['message']['speed']
            rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
            is_valid = rsv_location['message'].get('isValid')#判断是否有效
            if is_valid:
              rsv_v=rsv_location['message']['speed']*(1852/3600)#转换为m/hs
              res_listv.append(abs(sim_v-rsv_v))
        if len(res_listv)>0:
              for i,res_v in res_listv:
                sum_v+=res_v
                result_v.append(sum_v/(i+1))
              return_message['result_v']=result_v
              return_message['status'] = 'success'
              return_message['result_mv'] = math.sqrt(sum_v/len(res_listv))
              return return_message   
        else:
            return_message['status'] = 'fail'
            return return_message   
    except Exception as e:
        return_message['status'] = 'error'
        return_message['message'] = str(e)
        return return_message  
#里程偏差
def mileage_recording_bias(locus ='' ,data_num =900,time_step = 1,address = ''):#time_step取数间隔时间，addressIP地址,point为坐标
    return_message = {'status':None}
    res_listv = []#储存速度差
    result_v = []#存储误差均值
    try: 
        for i in range(data_num):
            time.sleep(time_step)
            sim_location = requests.get(url='http://'+address+'/vehicleinfo').json() 
            if sim_location['status'] == 'success':
              sim_v=sim_location['message']['speed']
            rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
            is_valid = rsv_location['message'].get('isValid')#判断是否有效
            if is_valid:
              rsv_v=rsv_location['message']['speed']*(1852/3600)#转换为m/hs
              res_listv.append(abs(sim_v-rsv_v))
        if len(res_listv)>0:
              for i,res_v in res_listv:
                sum_v+=res_v
                result_v.append(sum_v/(i+1))
              return_message['result_v']=result_v
              return_message['status'] = 'success'
              return_message['result_mv'] = math.sqrt(sum_v/len(res_listv))
              return return_message   
        else:
            return_message['status'] = 'fail'
            return return_message   
    except Exception as e:
        return_message['status'] = 'error'
        return_message['message'] = str(e)
        return return_message  
    
def capture_sensitivity(locus ='' ,data_num =900,time_step = 1,address = ''):#time_step取数间隔时间，addressIP地址,point为坐标
    return_message = {'status':None}
    res_listv = []#储存速度差
    result_v = []#存储速度误差均值
    try: 
        for i in range(data_num):
            time.sleep(time_step)
            sim_location = requests.get(url='http://'+address+'/vehicleinfo').json() 
            if sim_location['status'] == 'success':
              sim_v=sim_location['message']['speed']
            rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
            is_valid = rsv_location['message'].get('isValid')#判断是否有效
            if is_valid:
              rsv_v=rsv_location['message']['speed']*(1852/3600)#转换为m/hs
              res_listv.append(abs(sim_v-rsv_v))
        if len(res_listv)>0:
              for i,res_v in res_listv:
                sum_v+=res_v
                result_v.append(sum_v/(i+1))
              return_message['result_v']=result_v
              return_message['status'] = 'success'
              return_message['result_mv'] = math.sqrt(sum_v/len(res_listv))
              return return_message   
        else:
            return_message['status'] = 'fail'
            return return_message   
    except Exception as e:
        return_message['status'] = 'error'
        return_message['message'] = str(e)
        return return_message  
#return_message['status']message状态，'success'成功，'fail'失败，'error'错误
#return_message['time_start']测试开始时间
#return_message['time_end']测试结束时间
#return_message['time_now']测试当前时间
#return_message['lat']即时纬度
#return_message['lon']即时经度
#return_message['alt']即时高度
#return_message['speed']即时速度
#return_message['message']错误信息
#return_message['static_bias']实时静态定位误差值
#return_message['result_static_bias']静态定位误差列表
#return_message['result_static_mbias']静态定位误差均值
#return_message['dynamic_bias']实时动态定位误差值
#return_message['result_dynamic_bias']动态定位误差列表
#return_message['result_dynamic_mbias']动态定位误差均值
#return_message['speed_bias']实时速度测量误差值
#return_message['result_v]平均速度差列表
#return_message['result_mv']速度误差均值

def toRadian(degree):
  return degree / 180.0 * Pi
  
def toDegree(radian):
  return radian / Pi * 180.0

class Lla:
  def __init__(self, lat, lon, alt=0):
    self.lat = lat # latitude in radians
    self.lon = lon # longitude in radians
    self.alt = alt # altitude in meters
    
  def addEnu(self, enu):
    return enu.toLla(self)
    
  def toEcef(self):
    cos_lat = math.cos(self.lat)
    tmp = (1-EFLAT)*(1-EFLAT)
    ex2 = (2-EFLAT)*EFLAT/tmp
    c = ESMAJ*math.sqrt(1+ex2)
    n = c/math.sqrt(1+ex2*cos_lat*cos_lat)
    return Ecef((n+self.alt)*cos_lat*math.cos(self.lon),(n+self.alt)*cos_lat*math.sin(self.lon), (tmp*n+self.alt)*math.sin(self.lat))

  def toEnu(self, origin):
    return Enu((self.lon - origin.lon) * ESMAJ * math.cos(self.lat),  (self.lat - origin.lat) * ESMAJ, self.alt - origin.alt)
  
  def latDeg(self):
    return toDegree(self.lat)
    
  def lonDeg(self):
    return toDegree(self.lon)
    
  def __str__(self):
   return u"%.7fdeg, %.7fdeg, %.2fm" % (self.latDeg(), self.lonDeg(), self.alt)
    
  def __add__(self, other):
    return Lla(self.lat + other.lat, self.lon + other.lon, self.alt + other.alt)
  
  def __eq__(self, other):
    if other == None:
      return False  
    else:
      return self.lat == other.lat and self.lon == other.lon and self.alt == other.alt
  
  def __ne__(self, other):
    return not (self == other)

class Enu:
  def __init__(self, east, north, up=0):
    self.east = east   # east deviation in meters
    self.north = north # north deviation in meters
    self.up = up       # up deviation in meters
  
  # def toEcef(self, originLla):
  #   originEcef = originLla.toEcef()
  #   sinLon = math.sin(originLla.lon)
  #   cosLon = math.cos(originLla.lon)
  #   sinLat = math.sin(originLla.lat)
  #   cosLat = math.cos(originLla.lat)
    
  #   x = -sinLon * self.east - sinLat * cosLon * self.north + cosLat * cosLon * self.up + originEcef.x
  #   y = cosLon * self.east - sinLat * sinLon * self.north + cosLat * sinLon * self.up + originEcef.y
  #   z = cosLat * self.north + sinLat * self.up + originEcef.z
    
  #   return Ecef(x, y, z)
  
  def toEcef(self, originLla):
      # WGS-84椭球体参数
      a = ESMAJ
      f = EFLAT

      # 计算椭球面的曲率半径
      sin_lat = math.sin(originLla.lat)
      N = a / math.sqrt(1 - EECC_SQUARED * sin_lat ** 2)

      # 计算经过改正的纬度和经度
      dLat = self.north / (N + originLla.alt)
      dLon = self.east / ((N + originLla.alt) * math.cos(originLla.lat))
      dLat = originLla.lat + dLat
      dLon = originLla.lon + dLon

      # 根据改正后的纬度，重新计算曲率半径
      sin_lat_corrected = math.sin(dLat)
      N_corrected = a / math.sqrt(1 - EECC_SQUARED * sin_lat_corrected ** 2)

      # 转换为ECEF坐标系
      cos_lat_corrected = math.cos(dLat)
      cos_lon_corrected = math.cos(dLon)
      sin_lon_corrected = math.sin(dLon)

      x = (N_corrected + originLla.alt) * cos_lat_corrected * cos_lon_corrected
      y = (N_corrected + originLla.alt) * cos_lat_corrected * sin_lon_corrected
      z = ((1 - EECC_SQUARED) * N_corrected + originLla.alt) * sin_lat_corrected

      return Ecef(x, y, z)
    
  def toLla(self, originLla):
    return self.toEcef(originLla).toLla()
    
  def __str__(self):
    return "%.2fm East, %.2fm North, %.2fm Up" % (self.east, self.north, self.up)
  
  def __add__(self, other):
    return Enu(self.east + other.east, self.north + other.north, self.up + other.up)
  
  def __eq__(self, other):
    return self.east == other.east and self.north == other.north and self.up == other.up
    
  def __ne__(self, other):
    return not (self == other)
    
class Ecef:
  def __init__(self, x, y, z):
    self.x = x 
    self.y = y 
    self.z = z
     
  def toLla(self):
    dist_to_z = math.sqrt(self.x*self.x + self.y*self.y)
    lat = math.atan2(self.z, (1 - EECC_SQUARED) * dist_to_z)
    for i in range(1, 5):
      sin_lat = math.sin(lat)
      radius_p = ESMAJ / math.sqrt(1.0 - EECC_SQUARED * sin_lat * sin_lat)
      lat = math.atan2(self.z + EECC_SQUARED * radius_p * sin_lat, dist_to_z)
    lon = math.atan2(self.y, self.x)
    if toDegree(lat) < -85 or toDegree(lat) > 85:
      L = self.z + EECC_SQUARED * radius_p * math.sin(lat)
      alt = L / math.sin(lat) - radius_p
    else:
      alt = dist_to_z / math.cos(lat) - radius_p
    return Lla(lat, lon, alt)
    
  def __str__(self):
   return u"%.2fm, %.2fm, %.2fm" % (self.x, self.y, self.z)
    
  def __add__(self, other):
    return Lla(self.x + other.x, self.y + other.y, self.z + other.z)
  
  def __eq__(self, other):
    return self.x == other.x and self.y == other.y and self.z == other.z
  
  def __ne__(self, other):
    return not (self == other)
    
class Attitude:
  def __init__(self, yaw, pitch, roll):
    self.yaw = yaw
    self.pitch = pitch
    self.roll = roll
    
  def __str__(self):
    return u"%.2fdeg, %.2fdeg, %.2fdeg" % (self.yawDeg(), self.pitchDeg(), self.rollDeg())
    
  def __add__(self, other):
    return Attitude(self.yaw + other.yaw, self.pitch + other.pitch, self.roll + other.roll)
  
  def __eq__(self, other):
    return self.yaw == other.yaw and self.pitch == other.pitch and self.roll == other.roll
  
  def __ne__(self, other):
    return not (self == other)
    
  def yawDeg(self):
    return toDegree(self.yaw)
    
  def pitchDeg(self):
    return toDegree(self.pitch)
    
  def rollDeg(self):
    return toDegree(self.roll)
   







