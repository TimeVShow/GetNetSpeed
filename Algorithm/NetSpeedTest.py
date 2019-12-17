import requests
import time
burl = "http://192.168.209.129:8000/polls/"
purl = burl+"post/"
def getDownLoadSpeed():
    time.process_time()
    downspeed = 0
    for i in range (0,6):
        des = "download/"+str(i)+".txt"
        before = time.perf_counter()
        durl = burl + str(i)+"/download/"
        r = requests.get(durl)
        after = time.perf_counter()
        with open(des,"wb") as f:
            f.write(r.content)
        downspeed += (1<<i)/(after - before)
    speed = downspeed / 6
    print("download netspeed is:%d MB/S\n" % speed)

def getPostSpeed():
    upspeed = 0
    for i in range(0,6):
        des = "download/"+str(i)+".txt"
        files = {'file':open(des,"rb")}
        r = requests.post(purl,files=files)
        time = float(r.text)
        upspeed += (1<<i)/time
    speed = upspeed / 5
    print("download netspeed is: %d MB/S" % speed)

if __name__ == "__main__":
    getDownLoadSpeed()
    getPostSpeed()


