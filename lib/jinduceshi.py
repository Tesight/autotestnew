import requests,json,time,math
import yaml
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
from common.logger import Log
from filelock import FileLock
import math
ESMAJ = 6378137.0 # Semi-major axis of Earth, meters
EFLAT = 0.00335281066474
ESMIN = ESMAJ * (1.0 - EFLAT)
EECC_SQUARED = (((ESMAJ*ESMAJ) - (ESMIN*ESMIN)) / (ESMAJ*ESMAJ))
Pi    = 3.1415926535898 # Pi used in the GPS coordinate
yaml_file = '测试报告.yaml'

#静态定位误差
def static_position_bias(data_num =900,wait_time=180,time_step = 1,address = '',standard=15):#time_step取数间隔时间，addressIP地址,point为坐标
    return_message = {'status':None}
    result_bias=[]#存储平均坐标误差
    time_result_bias=[]#存储实时坐标误差
    count=0
    sum=0
    wait=False
    try:
      for i in range(wait_time):
          time.sleep(time_step)
          rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
          # print(rsv_location)
          is_valid = rsv_location['message'].get('isValid')
          if is_valid:
              wait=True
              break
      if wait==True:  
        for i in range(data_num):
          time.sleep(time_step)
          sim_location = requests.get(url='http://'+address+'/vehicleinfo').json()
          rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
          is_valid = rsv_location['message'].get('isValid')#判断是否有效
          if sim_location['status'] == 'success' and is_valid:
            sim_lla = Lla(
                  lat=toRadian(sim_location['message']['latitude']),
                  lon = toRadian(sim_location['message']['longitude']),
                  alt = sim_location['message']['altitude'])
            # 将数据存储在 YAML 文件中
            data = {    
              'sim_current_time':sim_location['message']['sim_current_time'],
                'sim_lat': sim_location['message']['latitude'],
                'sim_lon': sim_location['message']['longitude'],
                'sim_alt': sim_location['message']['altitude'],
                'sim_v': 0,
                }
            print(data)
            with FileLock("静态定位精度模拟器参数.yaml.lock"):
              with open('静态定位精度模拟器参数.yaml', 'w') as file:
                yaml.dump(data, file)
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
            print(data)
            with FileLock("静态定位精度待测件参数.yaml.lock"):
              with open('静态定位精度待测件参数.yaml', 'w') as file:
                yaml.dump(data, file)
            h=enu_res.east**2+enu_res.north**2
            v=enu_res.up**2
            bias=math.sqrt(h+v)
            sum+=bias
            biasx=sum/(count+1)
            count=count+1
            data = {
              'count': count,
              'time': rsv_location['message']['datetime'],
              'bias':  bias,#即时误差
              'biasx': biasx,#平均误差
              }
            print(data)
            with FileLock("静态定位计算数据.yaml.lock"):
              with open('静态定位计算数据.yaml', 'w') as file:
                yaml.dump(data, file)
            time_result_bias.append(bias)
            result_bias.append(biasx)
        data = {
            '测试项目': '静态定位精度',
            '测试数据': biasx,#平均误差
            '标准要求值': standard,
            '测试结果': 'PASS' if biasx <= standard else 'FAIL'
          }
        print(data)
        if append_test_item(yaml_file, data):
            print(f"测试项目已添加到测试项目列表中")
            Log().logger.info(f"静态定位误差结果已经添加到列表中")
        else:
            print(f"添加测试项目失败")
            Log().logger.error(f"添加静态定位误差测试项目失败")
        return_message['result_current_bias']=time_result_bias
        return_message['result_static_bias']=result_bias
        return_message['status'] = 'success'
        return_message['result_static_mbias'] = biasx#平均误差
        return return_message
      else:
        return_message['status'] = 'fail'
        return_message['message'] = '静态定位测试项目失败,待测件信号无效'
        return return_message
    except Exception as e:
        return_message['status'] = 'error'
        return_message['message'] = str(e)
        return return_message

      #动态定位误差
def dunamic_position_bias(data_num =900,wait_time=180,time_step = 1,address = '',standard=15):#time_step取数间隔时间，addressIP地址,point为坐标
    return_message = {'status':None}
    result_bias=[]#存储坐标误差
    result_mbias=[]#存储平均坐标误差
    count=0
    mtamp=0
    wait=False
    try:
        for i in range(wait_time):
            time.sleep(time_step)
            rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
            is_valid = rsv_location['message'].get('isValid')
            if is_valid:
               wait=True
               break
        if wait==True:
          for i in range(data_num):
            time.sleep(time_step)
            sim_location = requests.get(url='http://'+address+'/vehicleinfo').json()
            rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
            is_valid = rsv_location['message'].get('isValid')#判断是否有效
            if sim_location['status'] == 'success' and is_valid:
              sim_lla = Lla(
                    lat=toRadian(sim_location['message']['latitude']),
                    lon = toRadian(sim_location['message']['longitude']),
                    alt = sim_location['message']['altitude'])

              data = {        'sim_current_time':sim_location['message']['sim_current_time'],
                              'sim_lat': sim_location['message']['latitude'],
                              'sim_lon': sim_location['message']['longitude'],
                              'sim_alt': sim_location['message']['altitude'],
                              'sim_v': sim_location['message']['speed'],#速度

                          }
              with FileLock("动态定位精度模拟器参数.yaml.lock"):
                with open('动态定位精度模拟器参数.yaml', 'w') as file:
                  yaml.dump(data, file)

              rsv_lla = Lla(
                    lat=toRadian(rsv_location['message']['lat_deg']),
                    lon=toRadian(rsv_location['message']['lon_deg']),
                    alt=rsv_location['message']['alt'])
              rsv_v=rsv_location['message']['speed']*(1852/3600)#转换为m/s
              data = {        'dut_current_time':rsv_location['message']['datetime'],
                              'dut_lat': rsv_location['message']['lat_deg'],
                              'dut_lon': rsv_location['message']['lon_deg'],
                              'dut_alt': rsv_location['message']['alt'],
                              'dut_v':  rsv_v,#速度
                          }
              with FileLock("动态定位精度待测件参数.yaml.lock"):
                with open('动态定位精度待测件参数.yaml', 'w') as file:
                  yaml.dump(data, file)
              enu_res = rsv_lla.toEnu(sim_lla)
              x = enu_res.east**2
              y = enu_res.north**2
              z = enu_res.up**2
              bias  = math.sqrt(x+y+z)#即时误差
              mtamp += bias#即时误差相加
              xbias = mtamp/(count+1)#平均即时误差均值
              count=count+1
              data = {
                              'count': count,
                              'time': rsv_location['message']['datetime'],
                              'bias':  bias,#即时误差
                              'biasx': xbias,#平均误差
                          }
              with FileLock("动态定位计算数据.yaml.lock"):
                with open('动态定位计算数据.yaml', 'w') as file:
                  yaml.dump(data, file)
              result_bias.append(bias)
              result_mbias.append(xbias)
          data = {
                    '测试项目': '动态定位精度',
                    '测试数据': xbias,#平均误差
                    '标准要求值': standard,
                    '测试结果': 'PASS' if xbias <= standard else 'FAIL'
                            }
          if append_test_item(yaml_file, data):
              print(f"测试项目已添加到测试项目列表中")
              Log().logger.info(f"动态定位误差结果已经添加到列表中")
          else:
              print(f"添加测试项目失败")
              Log().logger.error(f"添加动态定位误差测试项目失败")
          return_message['result_dynamic_bias']=result_bias
          return_message['result_dynamic_mbias']=result_mbias
          return_message['status'] = 'success'
          return_message['result_dynamic_sumbias'] = xbias#平均误差
          return return_message
        else:
          return_message['status'] = 'fail'
          return_message['message'] = '动态定位测试项目失败,待测件信号无效'
          return return_message
    except Exception as e:
        return_message['status'] = 'error'
        return_message['message'] = str(e)
        return return_message

    #测速偏差
def speed_measurement_bias(data_num =900,wait_time=180,time_step = 1,address = '',standard=15):#time_step取数间隔时间，addressIP地址,point为坐标
    return_message = {'status':None}
    res_listv = []#储存及时速度差
    result_v = []#存储误差均值
    count=0
    sum_v=0
    wait=False
    try:
        for i in range(wait_time):
            time.sleep(time_step)
            rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
            is_valid = rsv_location['message'].get('isValid')
            if is_valid:
               wait=True
               break
        if wait==True:
          for i in range(data_num):
              time.sleep(time_step)
              sim_location = requests.get(url='http://'+address+'/vehicleinfo').json()
              rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
              is_valid = rsv_location['message'].get('isValid')#判断是否有效
              if sim_location['status'] == 'success' and is_valid:
                sim_v=sim_location['message']['speed']
                data = {      'sim_current_time':sim_location['message']['sim_current_time'],
                              'sim_lat': sim_location['message']['latitude'],
                              'sim_lon': sim_location['message']['longitude'],
                              'sim_alt': sim_location['message']['altitude'],
                              'sim_v': sim_v,#速度
                          }
                with FileLock("测速精度模拟器参数.yaml.lock"):
                  with open('测速精度模拟器参数.yaml', 'w') as file:
                    yaml.dump(data, file)
                rsv_v=rsv_location['message']['speed']*(1852/3600)#转换为m/s
                data = {        'dut_current_time':rsv_location['message']['datetime'],
                                'dut_lat': rsv_location['message']['lat_deg'],
                                'dut_lon': rsv_location['message']['lon_deg'],
                                'dut_alt': rsv_location['message']['alt'],
                                'dut_v':rsv_v,#速度
                            }
                with FileLock("测速精度待测件参数.yaml.lock"):
                  with open('测速精度待测件参数.yaml', 'w') as file:
                    yaml.dump(data, file)
                v=abs(sim_v-rsv_v)
                sum_v+=v
                v_bias=sum_v/(count+1)
                count=count+1
                data = {
                              'count': count,
                              'time': rsv_location['message']['datetime'],
                              'bias':  v,#即时误差
                              'biasx': v_bias,#平均误差
                          }
                with FileLock("测数偏差计算数据.yaml.lock"):
                  with open('测数偏差计算数据.yaml', 'w') as file:
                    yaml.dump(data, file)
                res_listv.append(v)
                result_v.append(v_bias)
          data = {
                    '测试项目': '测数精度',
                    '测试数据': v_bias,#平均误差
                    '标准要求值': standard,
                    '测试结果': 'PASS' if v_bias <= standard else 'FAIL'
                            }
          if append_test_item(yaml_file, data):
              Log().logger.info(f"测速偏差结果已经添加到列表中")
          else:
              Log().logger.error(f"添加测速偏差测试项目失败") 
          return_message['result_v']=res_listv
          return_message['result_mv'] = result_v
          return_message['status'] = 'success'
          return_message['result_sumv'] = v_bias
          return return_message
        else:
          return_message['status'] = 'fail'
          return_message['message'] = '测速偏差测试项目失败,待测件信号无效'
          return return_message
    except Exception as e:
        return_message['status'] = 'error'
        return_message['message'] = str(e)
        return return_message

#里程偏差
def mileage_bias(data_num=900, wait_time=180,time_step=1, address='',standard=15):
    return_message = {'status': None}
    sum_sim_distance = 0.0
    sum_rsv_distance = 0.0
    prev_sim_ecef = None
    prev_rsv_ecef = None
    result_bias = []
    result_mbias = []#存储平均坐标误差
    count = 0
    wait=False
    try:
        for i in range(wait_time):
            time.sleep(time_step)
            rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
            is_valid = rsv_location['message'].get('isValid')
            if is_valid:
              wait=True
              break
        if wait==True:
          for i in range(data_num):
              time.sleep(time_step)
              # 获取模拟器和接收机数据
              sim_location = requests.get(url='http://'+address+'/vehicleinfo').json()
              rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
              is_valid = rsv_location['message'].get('isValid')

              if sim_location['status'] == 'success' and is_valid:
                  # 转换模拟器坐标
                sim_v=sim_location['message']['speed']
                data = {      
                  'sim_current_time':sim_location['message']['sim_current_time'],
                    'sim_lat': sim_location['message']['latitude'],
                    'sim_lon': sim_location['message']['longitude'],
                    'sim_alt': sim_location['message']['altitude'],
                    'sim_v': sim_v,#速度
                          }
                with FileLock("里程精度模拟器参数.yaml.lock"):
                  with open('里程精度模拟器参数.yaml', 'w') as file:
                    yaml.dump(data, file)

                rsv_v=rsv_location['message']['speed']*(1852/3600)#转换为m/s
                data = {        'dut_current_time':rsv_location['message']['datetime'],
                                'dut_lat': rsv_location['message']['lat_deg'],
                                'dut_lon': rsv_location['message']['lon_deg'],
                                'dut_alt': rsv_location['message']['alt'],
                                'dut_v':rsv_v,#速度
                            }
                with FileLock("里程精度待测件参数.yaml.lock"):
                  with open('里程精度待测件参数.yaml', 'w') as file:
                    yaml.dump(data, file)

                sim_ecef = geodetic_to_ecef(
                    sim_location['message']['latitude'],
                    sim_location['message']['longitude'],
                    sim_location['message']['altitude']
                )

                # 转换接收机坐标
                rsv_ecef = geodetic_to_ecef(
                    rsv_location['message']['lat_deg'],
                    rsv_location['message']['lon_deg'],
                    rsv_location['message']['alt']
                )

                # 计算模拟器里程
                if prev_sim_ecef:
                    sim_distance = distance_3d(prev_sim_ecef, sim_ecef)
                    sum_sim_distance += sim_distance

                # 计算接收机里程
                if prev_rsv_ecef:
                    rsv_distance = distance_3d(prev_rsv_ecef, rsv_ecef)
                    sum_rsv_distance += rsv_distance

                # 更新前一点坐标
                prev_sim_ecef = sim_ecef
                prev_rsv_ecef = rsv_ecef

                # 计算里程偏差
                current_bias = sum_rsv_distance - sum_sim_distance
                average_bias = current_bias / (count + 1) if count > 0 else 0
                count += 1

                # 保存结果
                data = {
                    'count': count,
                    'time': rsv_location['message']['datetime'],
                    'sim_mileage': sum_sim_distance,
                    'rsv_mileage': sum_rsv_distance,
                    'current_bias': current_bias,
                    'average_bias': average_bias
                }
                with FileLock("里程偏差数据.yaml.lock"):
                    with open('里程偏差数据.yaml', 'w') as file:
                        yaml.dump(data, file)

                result_bias.append(current_bias)
                result_mbias.append(average_bias)
              # else:
              #     return_message['status'] = 'fail'
              #     return return_message
          data = {
                  '测试项目': '里程偏差',
                  '测试数据': average_bias,#平均误差
                  '标准要求值': standard,
                  '测试结果': 'PASS' if average_bias <= standard else 'FAIL'
                  }
          if append_test_item(yaml_file, data):
              Log().logger.info(f"里程偏差结果已经添加到列表中")
          else:
              Log().logger.error(f"添加里程偏差测试项目失败")
          return_message['status'] = 'success'
          return_message['current_bias'] = result_bias
          return_message['average_bias'] = result_mbias
          return_message['total_sim_mileage'] = sum_sim_distance     #模拟器里程
          return_message['total_rsv_mileage'] = sum_rsv_distance     #接收机里程
          return return_message
        else:
          return_message['status'] = 'fail'
          return_message['message'] = '里程偏差测试项目失败,待测件信号无效'
          return return_message
    except Exception as e:
        return_message['status'] = 'error'
        return_message['message'] = str(e)
        return return_message

#捕获灵敏度
def capture_sensitivity(locus ='' ,data_num =300,wait_time=180,time_step = 1,address = '',standard=15):#time_step取数间隔时间，addressIP地址,point为坐标
    return_message = {'status':None}
    count=0
    output_reference_power = 0
    sum=0
    wait=False
    try:
        for i in range(wait_time):
            print("等待接收机定位...")
            time.sleep(time_step)
            rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
            print(rsv_location)
            is_valid = rsv_location['message'].get('isValid')
            if is_valid:
               wait=True
               break
        while wait:
            count=0
            sum=0
            sim_location = requests.get(url='http://'+address+'/vehicleinfo').json()
            if sim_location['status'] == 'success':
              # 将数据存储在 YAML 文件中
              data = {      'sim_current_time':sim_location['message']['sim_current_time'],
                            'sim_lat': sim_location['message']['latitude'],
                            'sim_lon': sim_location['message']['longitude'],
                            'sim_alt': sim_location['message']['altitude'],
                            'sim_v': 0,
                        }
              with FileLock("捕获灵敏度模拟器参数.yaml.lock"):
                with open('捕获灵敏度模拟器参数.yaml', 'w') as file:
                  yaml.dump(data, file)
              sim_lla = Lla(
                  lat=toRadian(sim_location['message']['latitude']),
                  lon = toRadian(sim_location['message']['longitude']),
                  alt = sim_location['message']['altitude'])
              output_reference_power = sim_location['message']['pc']
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
                      with FileLock("捕获灵敏度待测件参数.yaml.lock"):
                        with open('捕获灵敏度待测件参数.yaml', 'w') as file:
                          yaml.dump(data, file)
                      h=enu_res.east**2+enu_res.north**2
                      v=enu_res.up**2
                      bias=math.sqrt(h+v)
                      sum+=bias
                      biasx=sum/(count+1)
                      count=count+1
                      data = {
                              'count': count,
                              'time': rsv_location['message']['datetime'],
                              'bias':  bias,#即时误差
                              'biasx': biasx,#平均误差
                              'pc':output_reference_power#输出参考功率
                          }
                      with FileLock("捕获灵敏计算数据.yaml.lock"):
                        with open('捕获灵敏计算数据.yaml', 'w') as file:
                          yaml.dump(data, file)
                      if bias>100 :
                          count=0
                      if count==10:
                        data = {
                              '测试项目': '捕获灵敏度',
                              '测试数据': output_reference_power,#平均误差
                              '标准要求值': standard,
                              '测试结果': 'PASS' if output_reference_power <= standard else 'FAIL'
                          }
                        if append_test_item(yaml_file, data):
                            Log().logger.info(f"捕获灵敏度结果已经添加到列表中")
                        else:
                            Log().logger.error(f"添加捕获灵敏度测试项目失败")
                        return_message['status'] = 'success'
                        return_message['result_static_mbias'] = bias
                        return_message['pc'] = output_reference_power
                        return return_message
              output_reference_power=output_reference_power+1
              url = "http://127.0.0.1:5000/customized/offset2"
              data = {
                "output_reference_power": output_reference_power,
                }
              response = requests.post(url, json=data)
              Log().logger.info(response)
              if response.status_code == 200:
                  Log().logger.info("成功发送请求")
              if response.status_code == 500:
                  Log().logger.info("检测失败")
                  return_message['status'] = 'fail'
                  return_message['message'] = '捕获灵敏度测试项目失败,误差全部大于100米'
                  return return_message
        return_message['status'] = 'fail'
        return_message['message'] = '捕获灵敏度测试项目失败,接收机信号无效'
        return return_message
    except Exception as e:
        return_message['status'] = 'error'
        return_message['message'] = str(e)
        return return_message

#跟踪灵敏度
def tracking_sensitivity(locus ='' ,data_num =300,wait_time=180,time_step = 1,address = '',standard=15):#time_step取数间隔时间，addressIP地址,point为坐标
    return_message = {'status':None}
    count=0
    sum=0
    output_reference_power = 0
    wait=False
    try:
        for i in range(wait_time):
          time.sleep(time_step)
          rsv_location = requests.get(url='http://'+address+'/receiver/location').json()
          is_valid = rsv_location['message'].get('isValid')
          if is_valid:
            wait=True
            break
        while wait:
          count=0
          sum=0
          over=True
          for i in range(data_num):
            time.sleep(time_step)
            sim_location = requests.get(url='http://'+address+'/vehicleinfo').json()
            if sim_location['status'] == 'success':
            # 将数据存储在 YAML 文件中
              data = {    
                  'sim_current_time':sim_location['message']['sim_current_time'],
                    'sim_lat': sim_location['message']['latitude'],
                    'sim_lon': sim_location['message']['longitude'],
                    'sim_alt': sim_location['message']['altitude'],
                    'sim_v': 0,
                      }
              with FileLock("跟踪灵敏度模拟器参数.yaml.lock"):
                with open('跟踪灵敏度模拟器参数.yaml', 'w') as file:
                  yaml.dump(data, file)
              sim_lla = Lla(
                  lat=toRadian(sim_location['message']['latitude']),
                  lon = toRadian(sim_location['message']['longitude']),
                  alt = sim_location['message']['altitude'])
              output_reference_power = sim_location['message']['pc']
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
                  with FileLock("跟踪灵敏度待测件参数.yaml.lock"):
                    with open('跟踪灵敏度待测件参数.yaml', 'w') as file:
                      yaml.dump(data, file)
                  h=enu_res.east**2+enu_res.north**2
                  v=enu_res.up**2
                  bias=math.sqrt(h+v)
                  sum+=bias
                  biasx=sum/(count+1)
                  count=count+1
                  data = {
                          'count': count,
                          'time': rsv_location['message']['datetime'],
                          'bias':  bias,#即时误差
                          'biasx': biasx,#平均误差
                          'pc':output_reference_power#输出参考功率
                      }
                  with FileLock("跟踪灵敏度计算数据.yaml.lock"):
                    with open('跟踪灵敏度计算数据.yaml', 'w') as file:
                      yaml.dump(data, file)
                  if bias>100 :
                      count=0
                  if count==10:
                      over=False
                      output_reference_power=output_reference_power-1
                      url = "http://127.0.0.1:5000/customized/offset2"
                      data = {
                        "output_reference_power": output_reference_power,
                        }
                      response = requests.post(url, json=data)
                      Log().logger.info(response)
                      if response.status_code == 200:
                        Log().logger.info("成功发送请求，当前pc为"+str(output_reference_power))
                        break
                      if response.status_code == 500:
                        Log().logger.info("检测成功")
                        return_message['status'] = 'success'
                        return_message['result_static_mbias'] = bias
                        return_message['pc'] = output_reference_power
                        output_reference_power=output_reference_power+1
                        data = {
                                '测试项目': '跟踪灵敏度',
                                '测试数据': output_reference_power,#平均误差
                                '标准要求值': standard,
                                '测试结果': 'PASS' if output_reference_power <= standard else 'FAIL'
                            }
                        if append_test_item(yaml_file, data):
                            print(f"测试项目已添加到测试项目列表中")
                            Log().logger.info(f"跟踪灵敏度结果已经添加到列表中")
                        else:
                            print(f"添加测试项目失败")
                            Log().logger.error(f"添加跟踪灵敏度测试项目失败")
                        return return_message
          if over:
            output_reference_power=output_reference_power+1
            data = {
                    '测试项目': '跟踪灵敏度',
                    '测试数据': output_reference_power,#平均误差
                    '标准要求值': standard,
                    '测试结果': 'PASS' if output_reference_power <= standard else 'FAIL'
                }
            if append_test_item(yaml_file, data):
                print(f"测试项目已添加到测试项目列表中")
                Log().logger.info(f"跟踪灵敏度结果已经添加到列表中")
            else:
                print(f"添加测试项目失败")
                Log().logger.error(f"添加跟踪灵敏度测试项目失败")
            return_message['status'] = 'success'
            return_message['result_static_mbias'] = bias
            return_message['pc'] = output_reference_power
            return return_message
        return_message['status'] = 'fail'
        return_message['message'] = '跟踪灵敏度测试项目失败,接收机信号无效'
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


def geodetic_to_ecef(lat, lon, h):
    lat_rad = math.radians(lat)  # 纬度转弧度
    lon_rad = math.radians(lon)  # 经度转弧度
    a = 6378137.0                # WGS84 长半轴
    e_sq = 0.00669437999014      # 第一偏心率平方

    N = a / math.sqrt(1 - e_sq * math.sin(lat_rad)**2)
    x = (N + h) * math.cos(lat_rad) * math.cos(lon_rad)
    y = (N + h) * math.cos(lat_rad) * math.sin(lon_rad)
    z = (N * (1 - e_sq) + h) * math.sin(lat_rad)
    return (x, y, z)

def distance_3d(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    return math.sqrt(dx**2 + dy**2 + dz**2)

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

def read_yaml_file(yaml_path):
    """读取yaml文件"""
    if not os.path.isfile(yaml_path):
        raise FileNotFoundError("文件路径不存在，请检查路径是否正确：%s" % yaml_path)
    with open(yaml_path, 'r', encoding='utf-8') as doc:
        content = yaml.load(doc, Loader=yaml.Loader)
    return content


def write_yaml_file(yaml_path, data):
    """写入yaml文件"""
    if not os.path.isfile(yaml_path):
        raise FileNotFoundError("文件路径不存在，请检查路径是否正确：%s" % yaml_path)
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, Dumper=yaml.Dumper, allow_unicode=True,sort_keys=False)

def append_test_item(yaml_file, test_item, test_info=None):
    """
    向YAML测试报告文件添加新的测试项
    
    参数:
        yaml_file (str): YAML文件路径
        test_item (dict): 要添加的测试项数据，如 {'测试项目': '动态定位精度', ...}
        test_info (dict, optional): 测试基本信息，仅在需要创建新结构时使用
        
    返回:
        bool: 操作成功返回True，否则返回False
    """
    # 如果未提供测试基本信息，使用默认值
    if test_info is None:
        test_info = {
            '测试编号': 'TEST-2025-0228',
            '测试时间': '2025-02-28 14:30:00',
            '测试人': '车载接收机',
            '环境温度': '25°C',
            '环境湿度': '65%',
            '备注': '在开阔场地进行测试，天气晴朗，无电磁干扰'
        }
    
    try:
        # 确保文件存在
        if not os.path.exists(yaml_file):
            with open(yaml_file, 'w', encoding='utf-8') as f:
                pass
                
        with FileLock(f"{yaml_file}.lock"):
            # 读取现有数据
            try:
                data = read_yaml_file(yaml_file)
            except FileNotFoundError:
                # 如果文件不存在但路径有效，创建空文件
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    pass
                data = None
            
            if data is None or not isinstance(data, list) or len(data) == 0:
                # 如果文件为空或格式不正确，创建新的结构
                data = [{
                    '测试基本信息': test_info,
                    '测试项目列表': [test_item]
                }]
            else:
                # 寻找包含"测试项目列表"的条目
                found = False
                for item in data:
                    if isinstance(item, dict) and '测试项目列表' in item:
                        # 找到了测试项目列表，追加新测试项
                        item['测试项目列表'].append(test_item)
                        found = True
                        break
                        
                # 如果没有找到测试项目列表，检查第一个条目是否有测试基本信息
                if not found and len(data) > 0 and isinstance(data[0], dict) and '测试基本信息' in data[0]:
                    # 在第一个条目中添加测试项目列表
                    data[0]['测试项目列表'] = data[0].get('测试项目列表', []) + [test_item]
                    found = True
                    
                # 如果还是没找到合适的位置，删除可能存在的顶层测试项并添加到正确的结构中
                if not found:
                    # 过滤掉可能是单独测试项的顶层条目
                    data = [item for item in data if not (isinstance(item, dict) and '测试项目' in item)]
                    # 如果第一个条目是字典且没有测试基本信息，添加基本信息和测试项目列表
                    if len(data) > 0 and isinstance(data[0], dict):
                        data[0]['测试项目列表'] = data[0].get('测试项目列表', []) + [test_item]
                    else:
                        # 创建新的结构
                        data.insert(0, {
                            '测试基本信息': test_info,
                            '测试项目列表': [test_item]
                        })

            # 写回文件
            write_yaml_file(yaml_file, data)
            return True
            
    except Exception as e:
        print(f"添加测试项目时出错: {str(e)}")
        return False






