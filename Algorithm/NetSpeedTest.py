import requests
import time
burl = "http://182.254.189.71:8000/polls/"
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
        print("now download netspeed is:%.2f MB/s\n" % ((1<<i)/(after - before)))
        downspeed += (1<<i)/(after - before)
    speed = downspeed / 6
    print("download netspeed is:%.2f MB/S\n" % speed)

def getPostSpeed():
    upspeed = 0
    for i in range(0,6):
        des = "download/"+str(i)+".txt"
        files = {'file':open(des,"rb")}
        r = requests.post(purl,files=files)
        time = float(r.text)
        print("now post netspeed is:%.2f MB/s" % speed)
        upspeed += (1<<i)/time
    speed = upspeed / 5
    print("post netspeed is: %.2f MB/S" % speed)

if __name__ == "__main__":
    getDownLoadSpeed()
    getPostSpeed()
