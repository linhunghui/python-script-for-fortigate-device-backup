# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 22:26:29 2021
@author: Darren.Lin

Release note
v1:設備檔案備份
v2:新增功能(直接將備份存在\\10.10.10.1\運維部\網路設備&防火牆管理\SW備份中)
v3:新增功能(透過subprocess呼叫cmd去ping個設備確認連通後將設備IP加入OK_List在開始備份)
v4:新增ErrorLog功能
v5:新增功能:將DeviceLists改成去讀取一個excel檔中設備IP
如果有要新增備份設備請至\\10.10.10.1\運維部\網路設備&防火牆管理\網路設備備份IP表\網路設備_備份IP表.xlsx中的fortigate分頁更改

Bug:
    20200107
    1.偵測各設備通聯性並將成功通聯設備加入OK_List迴圈內判斷值為returncode,
    可針對Ping通與要求等候逾時做判斷，但下列情況無法判別
    回覆自 123.51.250.57: 目的地主機無法連線。
    

"""
from netmiko import ConnectHandler,NetmikoTimeoutException,NetmikoAuthenticationException
import datetime
import time
import os
import subprocess
import pandas as pd

#導入時間並格式化
datetime_dt=datetime.datetime.today()
datetime_str=datetime_dt.strftime("%Y_%m%d_%H%M") 


#將現在時間與NAS資料夾路徑結合新資料夾名稱
file='//10.10.10.1/運維部/網路設備&防火牆管理/FW備份/'+datetime_str

#建立備份檔存放目錄路徑
path=file+"/"

#開新資料夾
os.mkdir(file)

#OK_List先歸零
OK_List=[]
Nok_Lists=[]

"""原設備清單已由v5功能取代

#將設備IP存成List
Device_lists=[
#InternetFW-501E-1
'10.10.10.1',

#IntranetFW-501E-2
'10.10.10.1',

#反向案例Ping的到但不是對的設備看會不會有錯誤Log
#'1.1.1.1',

#反向案例Ping不到時會不會丟到OK_List
#'1.2.3.4',

]

"""

#sheet_name=None表示把所有分頁讀出來，讀取特定的工作表(sheet)，就是在sheet_name關鍵字參數的地方進行指定
df = pd.read_excel(r'//10.10.10.1/運維部/網路設備&防火牆管理/網路設備備份IP表/網路設備_備份IP表.xlsx',sheet_name='fortigate')  

#將cisco分頁中的IP讀取後存成list
Device_lists=df['IP'].tolist()

#程式執行顯示
print("針對下列設備開始通聯測試\n",Device_lists)

#將通聯設備清單記錄成Log
AlreadyBackupList = open(path+"此次備份設備清單"+datetime_str+".txt", "a")
print("針對下列設備開始通聯測試\n",Device_lists,file=AlreadyBackupList)
AlreadyBackupList.close()

#偵測各設備通聯性並將成功通聯設備加入OK_List
for i in Device_lists:
    #組合Ping指令
    ping_cmd='ping '+i
    
    #呼叫CMD模塊執行pingcmd
    ping_run=subprocess.run(ping_cmd)
    
    #擷取returncode,0=ping success ,1=ping fail
    ping_result=ping_run.returncode
    
    #將ping_result轉換成字串已越來作判別式
    ping_returnCode=str(ping_result)
    
    #判斷式Ping通的存成OK_IP_List,不通的記錄下來
    if "0" in ping_returnCode:
        print(i+" 通聯成功")
        OK_List +=[i]
    else:
        print(i+" 無法通聯")
        Nok_Lists +=[i]

#將無法通聯設備清單記錄成Log
AlreadyBackupList = open(path+"此次備份設備清單"+datetime_str+".txt", "a")
print("\n以下設備通聯成功\n",OK_List,file=AlreadyBackupList)
print("\n以下設備通聯失敗\n",Nok_Lists,file=AlreadyBackupList)
print("\n----------------------開始設備備份---------------------------",file=AlreadyBackupList)
AlreadyBackupList.close()

#程式執行顯示
print("以下設備通聯失敗\n",Nok_Lists,"\n請於每周一至周五早上0900-1800聯絡網路組人員協助處理")
print("備份以下設備\n",OK_List,"\n----------------------開始設備備份---------------------------")


#針對可通聯設備進行備份
for i in OK_List:
    forti = {
    	'device_type':'fortinet',
    	'ip':i,
    	'username':'yourusername',
    	'password': 'yourpassword', 
    }
    try:
        net_connect = ConnectHandler(**forti)
        output = net_connect.send_command("show full-configuration")
        fp = open(path+i+"備份日期"+datetime_str +".conf", "a", encoding="utf-8")
        fp.write("show full-configuration\n")
        fp.write(output)
        fp.close()
        print(i+" 備份已完成")
        AlreadyBackupList = open(path+"此次備份設備清單"+datetime_str+".txt", "a")
        print(i,"  備份完成",file=AlreadyBackupList)
        AlreadyBackupList.close()
    except NetmikoAuthenticationException : #认证失败报错记录
        ErrorLog1 = open(path+"錯誤日誌_認證失敗"+datetime_str+".txt", "a")
        print(datetime_str,i,'[Error 1]認證失敗!!!\n',file = ErrorLog1)
        ErrorLog1.close()
        AlreadyBackupList = open(path+"此次備份設備清單"+datetime_str+".txt", "a")
        print(i,"  備份失敗",file=AlreadyBackupList)
        AlreadyBackupList.close()
    except NetmikoTimeoutException : #登录超时报错记录
        ErrorLog2 = open(path+"錯誤日誌_連線超時"+datetime_str+".txt", "a")
        print(i,'[Error 2] 連線超時!!!\n',file=ErrorLog2)
        ErrorLog2.close()
        AlreadyBackupList = open(path+"此次備份設備清單"+datetime_str+".txt", "a")
        print(i,"  備份失敗",file=AlreadyBackupList)
        AlreadyBackupList.close()
    except : #未知报错记录
        ErrorLog3 = open(path+"錯誤日誌_未知錯誤"+datetime_str+".txt", "a")
        print(i,'[Error 3] Unknown error.\n',file = ErrorLog3)
        ErrorLog3.close()
        AlreadyBackupList = open(path+"此次備份設備清單"+datetime_str+".txt", "a")
        print(i,"  備份失敗",file=AlreadyBackupList)
        AlreadyBackupList.close()
    net_connect.disconnect()
	
AlreadyBackupList = open(path+"此次備份設備清單"+datetime_str+".txt", "a")
print("如有問題，請於每周一至周五早上0900-1800聯絡網路組人員協助處理",file=AlreadyBackupList)
AlreadyBackupList.close()
 
print("全部備份完成!!!!")

time.sleep(5)
