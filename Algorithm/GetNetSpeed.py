#!usr/bin/env python
# coding:utf-8
import paramiko
import datetime
import time
import os

hostname = "182.254.189.71"
username = 'liu'
password = '13137438608'
port = 22


def getUpLoadSpeed(sftp):
    upspeed = 0
    time.process_time()
    for i in range(10, 20):
        before = time.perf_counter()
        sftp.put('upload\\' + str(1 << i) + ".txt", "/home/liu/upload/" + str(1 << i) + ".txt")
        after = time.perf_counter()
        upspeed += (1 << i) / (1024 * (after - before))
    speed = upspeed / 10
    print("upload netspeed is:%d KB/S\n" % speed)


def getDownLoadSpeed(sftp):
    downspeed = 0
    time.process_time()
    for i in range(10, 20):
        before = time.perf_counter()
        sftp.get("/home/liu/download/" + str(1 << i) + ".txt", 'download\\' + str(1 << i) + ".txt")
        after = time.perf_counter()
        downspeed += (1 << i) / (1024 * (after - before))
    speed = downspeed / 10
    print("download netspeed is: %d KB/S" % speed)


if __name__ == '__main__':
    transport = paramiko.Transport((hostname, 22))
    transport.connect(username=username, password=password)
    # 关闭连接
    sftp = paramiko.SFTPClient.from_transport(transport)
    getUpLoadSpeed(sftp)
    getDownLoadSpeed(sftp)
    transport.close()
