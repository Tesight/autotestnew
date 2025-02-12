import subprocess


def run_cmd(command):
    p = subprocess.Popen(command, shell=True, creationflags=134217728,
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # p.wait(timeout=10)  # 设置超时为10秒    
    p.wait()     
    
    return p.stdout.read() 


def run_cmd_nowait(command):
    p = subprocess.Popen(command, shell=True, creationflags=134217728,
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  


if __name__ == '__main__':
    cmd = 'allure generate D:\\BaiduSyncdisk\\project\\python\\skydel\\scene\\testsuits\\02gjxt_http\\report\\allure\\result --clean'
    print(run_cmd(cmd))
