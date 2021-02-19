# python-script-for-fortigate-device-backup
Created on Wed Jan  6 22:26:29 2021
@author: Darren.Lin

Release note
v1:設備檔案備份
v2:新增功能(直接將備份存在\\10.10.10.1\運維部\網路設備&防火牆管理\SW備份中)
v3:新增功能(透過subprocess呼叫cmd去ping個設備確認連通後將設備IP加入OK_List在開始備份)
v4:新增ErrorLog功能
v5:新增功能:將DeviceLists改成去讀取一個excel檔中設備IP
如果有要新增備份設備請至\\10.10.10.1\運維部\網路設備&防火牆管理\網路設備備份IP表\網路設備_備份IP表.xlsx中的fortigate分頁更改
