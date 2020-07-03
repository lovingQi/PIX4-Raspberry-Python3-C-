#writing by XBL 
# -*- coding: utf-8 -*
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
import binascii
import serial  
import time
import os
import threading
#import re
plane_number = 1
ground_number = 7
flag_order = 1
flag_jump = 1
flag_main = True
flag_RSSI = 0
flag_GPS = 0
flag_mission =0
flag_fly = 0
flag_discharm = 0
flag_restart = 0
# RSSI Message start format
magic = 'FE'
lenstart = '01'
seq = '01'
sysid = 'FF' #get from plane later
compid = 'BE' #get from plane later
msgid = '00' 
payload0 = 'FF'
checksum = 'FFFF'
TXTMSG =''.join([magic,lenstart,seq,sysid,compid,msgid,payload0,checksum])
print('msgshow:',TXTMSG)
#RSSI Messgae  monitor 
#magic = 'FE'
lenstart2 = '18'
#GPSMSG = 'GPS time ...\n'
MissionMSG = 'writing mission\n'
FLYMSG = 'implent mission\n'
DischarmMSG = 'discharm\n'
RspresetMSG = 'The Raspberry is restart Now\n'

#sysid = 'FF' #get from plane later
#compid = 'BE' #get from plane later
#msgid = '00' 
#payload1time = '060708090A0B0C0D'
#payload2GPS = '0E0F10111213141516171819'
#payload3ATD = '1A1B1C1D'
#checksum2 = 'FFFF'
#TXTMSG1 =''.join([magic,lenstart2,seq2,sysid,compid,msgid,payload1time,payload2GPS,payload3ATD,checksum2])
#print('msgshow:',TXTMSG)
seq_int = 2
def hexShow(argv):        #十六进制显示 方法1
    try:
        result = ''  
        hLen = len(argv)  
        for i in range(hLen):  
            hvol = argv[i]
            hhex = '%02x'%hvol  
            result += hhex+' '  
        print('hexShow:',result)
         
    except:
        pass
def exchange(data1):
    x2 = ''
    x3 = ''
    length = len(data1)
    for i in range(0,length-2,2):
        x = data1[i:i+2]
        if int(x,16) < 96 :
            x2=x[1]
            x3 = ''.join([x3,x2])
        else:
            x2 = hex(int(x)-51)
            x2 = x2[2:]
            x3 = ''.join([x3,x2])
    # for i in range(1,length-2,2):
        # x = data1[i:i+1]
        # x2 = ''.join([x2,x])
        
    return x3
    #print(x3)
def ip_from_num(num):#根据飞机的编号获取相应的xbee模块ip地址
    numbers = {
        1:'0013A20041075240',
        2:'0013A20041075202',
        3:'0013A2004155D5DA',
        4:'0013A200410713E8',
        5:'0013A20041574718',
        6:'0013A2004107149A',
        7:'0013A2004155D66F'
    }
    return numbers.get(num,None)
def xbeeencode (plane_ip,SendMsg):
    len_pay = int(len(SendMsg)/2)+0x0E
    #print(len_pay)
    #len_pay = hex(len_pay)
    if len_pay < 0x10:
        len_pay = hex(len_pay)
        len_pay = ''.join(['0',len_pay[2:]])
        
    else:
        len_pay = hex(len_pay)
        len_pay = len_pay[2:]
        
    noncheckmsg = ''.join(['7E00',len_pay,'1000',plane_ip,'FFFE0000',SendMsg]) 
    #noncheckmsg = noncheckmsg.encode(encoding="utf-8") 
    checksum = 0
    length = len(noncheckmsg)
    for i in range(6,length,2):
        string = ''.join([noncheckmsg[i],noncheckmsg[i+1]])
        x=int(string,16)
        checksum = checksum + x 
    while checksum > 0xFF: # 上溢出
        checksum = ~checksum&0xFF     
    #print(checksum) 
    checksum=remove0x(hex(checksum))
    #checksum = checksum[2:]
   # checksum = checksum.upper()
    SendMsgencode = ''.join([noncheckmsg,checksum])
    return SendMsgencode
    
def remove0x (inputmsg):
    len_inputmsg = len(inputmsg)
    if(len_inputmsg % 2)==0:
        inputmsg = inputmsg[2:]
        inputmsg=inputmsg.upper()
    else:
        inputmsg = inputmsg[2:]
        inputmsg = ''.join(['0',inputmsg])
        inputmsg=inputmsg.upper()
    return inputmsg

class getgpsThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        if self.threadID == 1:   
        # 获取锁，用于线程同步
            threadLock.acquire()
            getRSSI()    
            print ("startthread： " + self.name)
            print ("%s: %s" % (self.name, time.ctime(time.time())))
        # 释放锁，开启下一个线程
            threadLock.release()
        elif self.threadID == 2:
            threadLock.acquire()
            getingorder()    
            print ("startthread： " + self.name)
            print ("%s: %s" % (self.name, time.ctime(time.time())))
        # 释放锁，开启下一个线程
            threadLock.release()
 
def osoperatonGPS ():
    os.system("./mavlink_GPS")
    #os.system("./kill.sh")
def getGPSMG():
    os.system("./mavlink_GPS")
    f = open("./localtion.txt","r")
    GPSMSG = f.read()
    f.close()
    GPSMSG = GPSMSG.split(',')
    return GPSMSG
    #attitude_current = hex(int(GPSMSG[24:]))
def getGPSMGstream():
    os.system("./mavlink_GPSstream")
    f = open("./localtionstream.txt","r")
    GPSMSG = f.read()
    f.close()
    GPSMSG = GPSMSG.split(',')
    return GPSMSG
def RSSIneedatt(attitude_current):
    os.system("./mavlink_GPS")
    f = open("./localtion.txt","r")
    GPSMSG = f.read()
    GPSMSG = GPSMSG.split(',')
    attitude_current = hex(int(GPSMSG[3]))
    attitude_current = remove0x(attitude_current)
    attitude_current = ''.join(['0000',attitude_current])
    return attitude_current
#获取时间，并以十六进制传输
def getime():
    mytime = time.localtime(time.time())
    time1 = mytime.tm_year
    time2 = mytime.tm_mon
    time3 = mytime.tm_mday
    time4 = mytime.tm_hour
    time5 = mytime.tm_min
    time6 = mytime.tm_sec
    
    time1 = remove0x(hex(time1))#2个字节 ：年
    time2 = remove0x(hex(time2))#1个字节：月
    time3 = remove0x(hex(time3))#1个字节：日
    time4 = remove0x(hex(time4))#1个字节：时
    time5 = remove0x(hex(time5))#1个字节：分
    time6 = remove0x(hex(time6))#1个字节：秒
    timemsg = ''.join([time1,time2,time3,time4,time5,time6])
    return timemsg
    
def fix4bytes(msgin):
    len_msgin = len(msgin)
    while len_msgin < 8:
        msgin = ''.join(['0',msgin])
        len_msgin = len_msgin+1
    else: 
        return msgin
        
        
    

def sendgps():
    t = serial.Serial('/dev/zigbeecom',115200)
    time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
    num=t.inWaiting() 
    #
    #在这里加获取GPS信息的程序 
    #os.system("./mavlink_GPS")
    print('now read gps')
    f = open("./localtion.txt","r")
    GPSMSG = f.read()
    longitude_current = hex(int(GPSMSG[0:10]))
    latitude_current = hex(int(GPSMSG[10:19]))
    high_current = hex(int(GPSMSG[19:24]))
    attitude_current = hex(int(GPSMSG[24:]))
    longitude_current = remove0x(longitude_current)
    latitude_current = remove0x(latitude_current)
    high_current = remove0x(high_current)
    attitude_current = remove0x(attitude_current)
    GPSMSG_total = ''.join([longitude_current,latitude_current,high_current]) 
    f.close()
    GPSMSG_encode = xbeeencode (ground_ip,GPSMSG_total)
    print(GPSMSG_encode)
    t.write(bytes.fromhex(GPSMSG_encode))
    if num:
        data1= str(binascii.b2a_hex(t.read(num)))[2:-1]
        if data1.startswith('99'):
            flag_GPS = 0
            flag_main = True  
        else:
            print('one')  
            pass   

def getRSSI():
    plane_number = 1
    ground_number = 7
    flag_order = 1
    flag_jump = 1
    flag_main = True
    flag_RSSI = 0
    flag_GPS = 0
    flag_mission =0
    flag_fly = 0
    flag_discharm = 0
    flag_restart = 0
    # RSSI Message start format
    magic = 'FE'
    lenstart = '01'
    seq = '01'
    sysid = 'FF' #get from plane later
    compid = 'BE' #get from plane later
    msgid = '00' 
    payload0 = 'FF'
    checksum = 'FFFF'
    TXTMSG =''.join([magic,lenstart,seq,sysid,compid,msgid,payload0,checksum])
    data1 = ''
    print('msgshow:',TXTMSG)
    #RSSI Messgae  monitor 
    #magic = 'FE'
    lenstart2 = '18'
    #GPSMSG = 'GPS time ...\n'
    MissionMSG = 'writing mission\n'
    FLYMSG = 'implent mission\n'
    DischarmMSG = 'discharm\n'
    RspresetMSG = 'The Raspberry is restart Now\n'

    #sysid = 'FF' #get from plane later
    #compid = 'BE' #get from plane later
    #msgid = '00' 
    #payload1time = '060708090A0B0C0D'
    #payload2GPS = '0E0F10111213141516171819'
    #payload3ATD = '1A1B1C1D'
    #checksum2 = 'FFFF'
    #TXTMSG1 =''.join([magic,lenstart2,seq2,sysid,compid,msgid,payload1time,payload2GPS,payload3ATD,checksum2])
    #print('msgshow:',TXTMSG)
    seq_int = 2
    while True:
        t = serial.Serial('/dev/RSSICOM',115200)
            #发第一条指令（启动指令）
        if flag_order==1:
            #TXTMSG = "FE0101030400FF0207"
            try:
                n =t.write(bytes.fromhex(TXTMSG))
                flag_order = 0
                time.sleep(1)  
                num=t.inWaiting()    
            except:
                n =t.write(bytes(TXTMSG,encoding='utf-8'))
                flag_order = 0
                time.sleep(1)  
                num=t.inWaiting()
   
    #发之后的指令（查询指令）
    #TXTMSG1 = "FE1802FFBE00060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F"
    #RSSI Messgae  monitor 
    #magic = 'FE'
        lenstart2 = '18'
    
        seq_hex = hex(seq_int)
        if seq_int < 16 :
            if seq_hex.startswith('0x'):
                seq_hex = seq_hex[2:]
                seq_hex = seq_hex.upper()
                seq_hex = ''.join(['0',seq_hex])
                #print(seq_hex)
        elif 15 < seq_int :
            if seq_hex.startswith('0x'):
                seq_hex = seq_hex[2:]
                seq_hex = seq_hex.upper()
    #sysid = 'FF' #get from plane later
    #compid = 'BE' #get from plane later
        msgid = '00' 
        payload1time = '060708090A0B0C0D'
        payload2GPS = '0E0F10111213141500000000'
        GPSMSG = getGPSMGstream()
        longitude = hex(int(GPSMSG[0]))
        longitude = remove0x(longitude)
        latitude = hex(int(GPSMSG[1]))
        latitude = remove0x(latitude)
        high = hex(int(GPSMSG[2]))
        high = remove0x(high) 
        high = fix4bytes(high) 
        attitude = hex(int(GPSMSG[3]))
        attitude = remove0x(attitude)
        
        attitude_current = remove0x(attitude)
        attitude_current = ''.join(['0000',attitude_current])
        #attitude_current = ''
        #attitude_current = RSSIneedatt(attitude_current)
        LLHMSGA = ''.join([longitude,latitude,high,attitude])
        TIMEMSG = getime()
        #print(TIMEMSG)
        #payload3ATD = '1A1B1C1D'
        checksum2 = '0000'
        TXTMSG1 =''.join([magic,lenstart2,seq_hex,sysid,compid,msgid,payload1time,payload2GPS,attitude_current,checksum2])
        #print(TXTMSG1)
    #print("start translate")
        try:    #如果输入不是十六进制数据-- 
            n =t.write(bytes.fromhex(TXTMSG1))
            print('send recall for rssi')
            if seq_int < 255:
                seq_int = seq_int + 1
            else:
                seq_int = 2
        except: #--则将其作为字符串输出
            n =t.write(bytes(TXTMSG1,encoding='utf-8'))
            print('send recall for rssi')
            if seq_int < 255:
                seq_int = seq_int + 1
            else:
                seq_int = 2
        time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
        num=t.inWaiting()
    
        if num: 
            try:   #如果读取的不是十六进制数据--
                data= str(binascii.b2a_hex(t.read(num)))[2:-1] #十六进制显示方法2
                print(data)
            #f = open("./RSSI/RSSIMSG.txt", 'w+')
                if flag_jump:  #循环重新启动串口
                    t = serial.Serial('/dev/zigbeecom',115200)
                    TXTMSG2 = data[52:68] #场强仪数据之后待改
                    TXTMSG2 = ''.join([TIMEMSG,LLHMSGA,TXTMSG2])
                    print(TXTMSG2)
                    TXTMSG2 = xbeeencode (ground_ip,TXTMSG2)
                    
                    #print(TXTMSG2)
                    try:    #如果输入不是十六进制数据-- 
                        n =t.write(bytes.fromhex(TXTMSG2))
                        flag_jump = 0
                    except: #--则将其作为字符串输出
                        n =t.write(bytes(TXTMSG2,encoding='utf-8'))
                        flag_jump = 0
            except: #--则将其作为字符串读取
                str = t.read(num) 
                hexShow(str)
        serial.Serial.close(t)
        t = serial.Serial('/dev/zigbeecom',115200)
        print('wait for deny')
        time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
        num = t.inWaiting() 
        if num:
            data1= str(binascii.b2a_hex(t.read(num)))[2:-1]
            data1 = data1[30:]
            if data1.startswith('99'):
                flag_RSSI = 0
                flag_main = True
                print('quit now')
            else:
                print('11111111111111111111111111111111111111111111111111111')  
                pass
                    #serial.Serial.close(t)
        #else:
            #print('RSSI bad')
                    
            #except:
              #  str = t1.read(num)
               # print(str)
                #print("two")
                #if data_main[2:3] == 'ff':
                #    flag_RSSI = 1
               #     flag_main = False
               # else:
               #     print('two')
                           
        #print(data)
        #print('\n')
        flag_jump = 1

def getingorder():  
    plane_number = 1
    ground_number = 7
    flag_order = 1
    flag_jump = 1
    flag_main = True
    flag_RSSI = 0
    flag_GPS = 0
    flag_mission =0
    flag_fly = 0
    flag_discharm = 0
    flag_restart = 0
    # RSSI Message start format
    magic = 'FE'
    lenstart = '01'
    seq = '01'
    sysid = 'FF' #get from plane later
    compid = 'BE' #get from plane later
    msgid = '00' c444444444444444444
    payload0 = 'FF'
    checksum = 'FFFF'
    TXTMSG =''.join([magic,lenstart,seq,sysid,compid,msgid,payload0,checksum])
    print('msgshow:',TXTMSG)
    #RSSI Messgae  monitor 
    #magic = 'FE'
    lenstart2 = '18'
    #GPSMSG = 'GPS time ...\n'
    MissionMSG = 'writing mission\n'
    FLYMSG = 'implent mission\n'
    DischarmMSG = 'discharm\n'
    RspresetMSG = 'The Raspberry is restart Now\n'

    #sysid = 'FF' #get from plane later
    #compid = 'BE' #get from plane later
    #msgid = '00' 
    #payload1time = '060708090A0B0C0D'
    #payload2GPS = '0E0F10111213141516171819'
    #payload3ATD = '1A1B1C1D'
    #checksum2 = 'FFFF'
    #TXTMSG1 =''.join([magic,lenstart2,seq2,sysid,compid,msgid,payload1time,payload2GPS,payload3ATD,checksum2])
    #print('msgshow:',TXTMSG)
    seq_int = 2
    while True:
        #对应四种状态，根据指令不同改变自己的状态
        #主状态：等待接收地面端指令，加以判别从而进入不同状态。
        plane_ip = ip_from_num(plane_number)
        ground_ip = ip_from_num(ground_number)
        while flag_main:
            t1 = serial.Serial('/dev/zigbeecom',115200)
            time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
            num=t1.inWaiting()
            if num:
                data_main = str(binascii.b2a_hex(t1.read(num)))[2:-1]
                #print (data_main)
                data_main = data_main[30:]
                #try:   #如果读取的不是十六进制数据--
                #data_main= t1.read(num)
                #data_main= data_main.decode(encoding="utf-8")
                #print(data_main)
                if data_main.startswith('01'):
                    flag_RSSI = 1
                    flag_main = False 
                elif data_main.startswith('02'):
                    flag_GPS = 1
                    flag_main = False
                elif data_main.startswith('03'):
                    flag_mission = 1
                    flag_main = False
                elif data_main.startswith('04'):
                    flag_fly = 1
                    flag_main = False
                elif data_main.startswith('05'):
                    flag_discharm = 1
                    flag_main = False
                elif data_main.startswith('06'):
                    flag_restart = 1
                    flag_main = False
                
                else:
                    print('not')  
                    pass
                #except:
                  #  str = t1.read(num)
                   # print(str)
                    #print("two")
                    #if data_main[2:3] == 'ff':
                    #    flag_RSSI = 1
                   #     flag_main = False
                   # else:
                   #     print('two')
            else:
                pass
                
                msg_waiting = 'FF'
                #msg_waiting = msg_waiting.hex()
                msg_waiting = xbeeencode (ground_ip,msg_waiting)
                
                print(msg_waiting)
                #t1.write(bytes(msg_waiting,encoding='utf-8'))
                t1.write(bytes.fromhex(msg_waiting))
                #print('waiting for order')
                
        #循环重新启动串口,开关获取场强仪数据    
        while flag_RSSI:  
            t = serial.Serial('/dev/RSSICOM',115200)
            #发第一条指令（启动指令）
            if flag_order==1:
                #TXTMSG = "FE0101030400FF0207"
                try:
                    n =t.write(bytes.fromhex(TXTMSG))
                    flag_order = 0
                    time.sleep(1)  
                    num=t.inWaiting()    
                except:
                    n =t.write(bytes(TXTMSG,encoding='utf-8'))
                    flag_order = 0
                    time.sleep(1)  
                    num=t.inWaiting()
       
        #发之后的指令（查询指令）
        #TXTMSG1 = "FE1802FFBE00060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F"
        #RSSI Messgae  monitor 
        #magic = 'FE'
            lenstart2 = '18'
        
            seq_hex = hex(seq_int)
            if seq_int < 16 :
                if seq_hex.startswith('0x'):
                    seq_hex = seq_hex[2:]
                    seq_hex = seq_hex.upper()
                    seq_hex = ''.join(['0',seq_hex])
                    #print(seq_hex)
            elif 15 < seq_int :
                if seq_hex.startswith('0x'):
                    seq_hex = seq_hex[2:]
                    seq_hex = seq_hex.upper()
        #sysid = 'FF' #get from plane later
        #compid = 'BE' #get from plane later
            msgid = '00' 
            payload1time = '060708090A0B0C0D'
            payload2GPS = '0E0F10111213141500000000'
            GPSMSG = getGPSMG()
            longitude = hex(int(GPSMSG[0]))
            longitude = remove0x(longitude)
            latitude = hex(int(GPSMSG[1]))
            latitude = remove0x(latitude)
            high = hex(int(GPSMSG[2]))
            high = remove0x(high) 
            high = fix4bytes(high) 
            attitude = hex(int(GPSMSG[3]))
            attitude = remove0x(attitude)
            attitude_current = ''
            attitude_current = RSSIneedatt(attitude_current)
            LLHMSGA = ''.join([longitude,latitude,high,attitude])
            TIMEMSG = getime()
            #print(TIMEMSG)
            #payload3ATD = '1A1B1C1D'
            checksum2 = '0000'
            TXTMSG1 =''.join([magic,lenstart2,seq_hex,sysid,compid,msgid,payload1time,payload2GPS,attitude_current,checksum2])
            #print(TXTMSG1)
        #print("start translate")
            try:    #如果输入不是十六进制数据-- 
                n =t.write(bytes.fromhex(TXTMSG1))
                print('send recall for rssi')
                if seq_int < 255:
                    seq_int = seq_int + 1
                else:
                    seq_int = 2
            except: #--则将其作为字符串输出
                n =t.write(bytes(TXTMSG1,encoding='utf-8'))
                print('send recall for rssi')
                if seq_int < 255:
                    seq_int = seq_int + 1
                else:
                    seq_int = 2
            time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
            num=t.inWaiting()
        
            if num: 
                try:   #如果读取的不是十六进制数据--
                    data= str(binascii.b2a_hex(t.read(num)))[2:-1] #十六进制显示方法2
                    print(data)
                #f = open("./RSSI/RSSIMSG.txt", 'w+')
                    if flag_jump:  #循环重新启动串口
                        t = serial.Serial('/dev/zigbeecom',115200)
                        TXTMSG2 = data[52:68] #场强仪数据之后待改
                        TXTMSG2 = ''.join([TIMEMSG,LLHMSGA,TXTMSG2])
                        print(TXTMSG2)
                        TXTMSG2 = xbeeencode (ground_ip,TXTMSG2)
                        
                        #print(TXTMSG2)
                        try:    #如果输入不是十六进制数据-- 
                            n =t.write(bytes.fromhex(TXTMSG2))
                            flag_jump = 0
                        except: #--则将其作为字符串输出
                            n =t.write(bytes(TXTMSG2,encoding='utf-8'))
                            flag_jump = 0
                except: #--则将其作为字符串读取
                    str = t.read(num) 
                    hexShow(str)
            serial.Serial.close(t)
            t = serial.Serial('/dev/zigbeecom',115200)
            print('wait for deny')
            time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
            num = t.inWaiting() 
            if num:
                data1= str(binascii.b2a_hex(t.read(num)))[2:-1]
                data1 = data1[30:]
                if data1.startswith('99'):
                    flag_RSSI = 0
                    flag_main = True
                    print('quit now')
                else:
                    print('11111111111111111111111111111111111111111111111111111')  
                    pass
                        #serial.Serial.close(t)
            #else:
                #print('RSSI bad')
                        
                #except:
                  #  str = t1.read(num)
                   # print(str)
                    #print("two")
                    #if data_main[2:3] == 'ff':
                    #    flag_RSSI = 1
                   #     flag_main = False
                   # else:
                   #     print('two')
                               
            #print(data)
            #print('\n')
            flag_jump = 1
                
                
            #serial.Serial.close(t)
        
        #获取飞机各项信息
        while flag_GPS:
            threadLock = threading.Lock()
            threads = []
            thread1 = getgpsThread(1,"Thread-1")
            thread2 = getgpsThread(2,"Thread-2")
            thread1.start()
            thread2.start()

    # 添加线程到线程列表
            threads.append(thread1)
            threads.append(thread2)
            for t in threads:
                t.join()
            print ("退出获取GPS的主线程")
            #serial.Serial.close(t)
        
        #写入飞行任务
        while flag_mission:
            t = serial.Serial('/dev/zigbeecom',115200)
            time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
            num=t.inWaiting()
            #
            #在这里加写入航点的程序 
            #
            #data1= str(binascii.b2a_hex(t.read(num)))[2:-1] #十六进制显示方法2
            #print(data)
            
            #n =t.write(bytes(MissionMSG,encoding='utf-8'))#给地面站反馈
            if num:
               # data1= str(binascii.b2a_hex(t.read(num)))[2:-1]
                 
                #data1 = t.read(num)
                #data1 = data1.decode(encoding="utf-8")
                data1= str(binascii.b2a_hex(t.read(num)))[2:-1]
                print(data1)
                data1 = data1[30:]
                #if data1.startswith('99'):
                #    flag_mission = 0
                #    flag_main = True
                #    print('quit now')
                #else:
                    #data1 = data1.encode(encoding="utf-8")
                print("thedatareceive1,%s" %data1)
                data1=str(exchange(data1))
                print("thedatareceive2,%s" %data1)
                longitude_set = str(int((data1[0:8]),16))
                latitude_set = str(int((data1[8:16]),16))
                #high_setint = 
                high_set = str(int((data1[16:19]),16))
                
                f = open("./longitude_set.txt","w")
                f.write(longitude_set)
                f.close()
                f = open("./latitude_set.txt","w")
                f.write(latitude_set)
                f.close()
                f = open("./high_set.txt","w")
                f.write(high_set)
                f.close()
                GPSMSG = getGPSMG()
                longitude_takeoff = GPSMSG[0]
                latitude_takeoff= GPSMSG[1]
                high_takeoff = GPSMSG[2]
                
                f = open("./longitude_takeoff.txt","w")
                f.write(longitude_takeoff)
                f.close()
                f = open("./latitude_takeoff.txt","w")
                f.write(latitude_takeoff)
                f.close()
                f = open("./high_takeoff.txt","w")
                f.write(high_takeoff)
                f.close()
                os.system("./mavlink_controlwrite")
                print('设定经度:',longitude_set)
                print('设定纬度:',latitude_set)
                print('设定高度:',high_set)
                #pass
                flag_mission = 0
                flag_main = True
                #serial.Serial.close(t)
            
            
        #执行飞行任务
        while flag_fly:
            t = serial.Serial('/dev/zigbeecom',115200)
            time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
            num=t.inWaiting()
            #
            #在这里加写入执行任务的程序 
            #
            n =t.write(bytes(FLYMSG,encoding='utf-8'))
            os.system("./mavlink_controlimp")
            
            
            #退出当前工作模式
            #if num:
            #    data1= str(binascii.b2a_hex(t.read(num)))[2:-1]
            #    if data1.startswith('99'):
           #         flag_fly = 0
             #       flag_main = True  
             #   else:
             #       print('one')  
             #       pass
            flag_fly = 0
            flag_main = True
        
        #一键解锁
        while flag_discharm:
            t = serial.Serial('/dev/zigbeecom',115200)
            time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
            num=t.inWaiting()
            #
            #在这里加写入执行任务的程序 
            #
            n =t.write(bytes(DischarmMSG,encoding='utf-8'))
            os.system("./mavlink_controldischarm")
            
            
            #退出当前工作模式
            #if num:
            #    data1= str(binascii.b2a_hex(t.read(num)))[2:-1]
            #    if data1.startswith('99'):
           #         flag_fly = 0
             #       flag_main = True  
             #   else:
             #       print('one')  
             #       pass
            flag_discharm = 0
            flag_main = True
            #serial.Serial.close(t)
            
       #树莓派一键重启
        while flag_restart:
            t = serial.Serial('/dev/zigbeecom',115200)
            time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
            num=t.inWaiting()
            #
            #在这里加写入执行任务的程序 
            #
            n =t.write(bytes(RspresetMSG,encoding='utf-8'))
            os.system("sudo reboot")
            #退出当前工作模式
            #if num:
            #    data1= str(binascii.b2a_hex(t.read(num)))[2:-1]
            #    if data1.startswith('99'):
            #        flag_fly = 0
             #       flag_main = True  
             #   else:
             #       print('one')  
             #       pass
            flag_restart = 0
            flag_main = True
        
while True:
    threadLock = threading.Lock()
    threads = []
    thread1 = getgpsThread(1,"Thread-1")
    thread2 = getgpsThread(2,"Thread-2")
    thread1.start()
    thread2.start()

# 添加线程到线程列表
    threads.append(thread1)
    threads.append(thread2)
    for t in threads:
        t.join()
    print ("退出获取GPS的主线程")
    #serial.Serial.close(t)
        
            
            
        
        
        