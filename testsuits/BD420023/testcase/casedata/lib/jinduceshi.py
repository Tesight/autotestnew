import requests,json,time,math

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
                print(rsv_location)
                
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
   







