# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 13:09:43 2020

@author: SWPraktikum Gruppe
"""

import requests
import socket
import csv

def writer(mcc,mnc,lac,cid,pcid,signal,cCount): 
    myData = [mcc,mnc,lac,cid,pcid,signal,cCount]
    with open('NB_IoT_Position.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=",")
        spamwriter.writerows([myData])
        
def reader():
    reader = csv.reader(open("NB_IoT_Position.csv"), delimiter=",")
    
    for row in reader:
        print(row)
        
def find_pos_NB(mcc,mnc,cid,lac,pcid,signal,cCount): #lac as hex // cid as hex
    lac=int(lac, 16)
    cid=int(cid, 16)
    writeFile = open("NB_IoT_Position.csv", 'a')
    

    url = "https://eu1.unwiredlabs.com/v2/process.php"
    
    payload = "{\"token\": \"7b512cd31c358d\",\"radio\": \"nbiot\",\"mcc\":"+ mcc + ",\"mnc\":"+ mnc+",\"cells\": ["
    payload = payload + "{\"lac\": " + str(lac) + ",\"cid\": "+ str(cid) + ",\"psc\": " + str(pcid[cCount-1]) + ",\"signal\": " + str(signal[cCount-1]) + "}"
    
    while cCount > 1:
        cCount = cCount - 1
        payload = payload + ",{\"psc\": " + str(pcid[cCount-1]) + ",\"signal\": " + str(signal[cCount-1]) + "}"
    
    payload = payload + "],\"address\": 1}"
    response = requests.request("POST", url, data=payload)
    
    response = response.json() #status,balance,lat,lon,accuracy,message,adress
    
    status = response["status"]
    
    if status == "ok":
        lat = response["lat"]
        lon = response["lon"]
        accuracy = response["accuracy"]
        
        print("latitude:"+ str(lat) + "\nlongitude:" + str(lon))
        writeFile.write("Latitude,Longitude")
        writeFile.write("\n" +str(lat) + "," +str(lon) +  "," + str(accuracy) +"\n")
    else:
        message = response["message"]
        writeFile.write("\"" + str(status) + "\"" + "," +  "\"\"" + "," + "\"\"" +  "," + "\"\"" + message + "\n")
    writeFile.close()
    
def find_pos_GSM(mcc,mnc,cid,lac,cidN,lacN,signal,cCount): #lac as hex // cid as hex
    lac=int(lac, 16)
    cid=int(cid, 16)
    
    writeFile = open("GMS_BO-W-RS.csv", 'a')
    

    url = "https://eu1.unwiredlabs.com/v2/process.php"
    
    payload = "{\"token\": \"7b512cd31c358d\",\"radio\": \"gsm\",\"mcc\":"+ mcc + ",\"mnc\":"+ mnc+",\"cells\": ["
    payload = payload + "{\"lac\": " + str(lac) + ",\"cid\": "+ str(cid) + "}"
    
    while cCount > 1:
        cCount = cCount - 1
        payload = payload + ",{\"lac\": " + str(int(lacN[cCount-1], 16)) + ",\"cid\": " + str(int(cidN[cCount-1], 16)) + ",\"signal\": " + str(signal[cCount-1]) + "}"
    
    payload = payload + "],\"address\": 1}"
    response = requests.request("POST", url, data=payload)
    
    response = response.json() #status,balance,lat,lon,accuracy,message,adress
    
    status = response["status"]
    
    if status == "ok":
        lat = response["lat"]
        lon = response["lon"]
        accuracy = response["accuracy"]
        
        print("latitude:"+ str(lat) + "\nlongitude:" + str(lon))
        writeFile.write("\"" +str(lat) + "\"" + "," + "\"" + str(lon) + "\"" +  "," + "\"" + str(accuracy) + "\"" + "\n")
    else:
        message = response["message"]
        writeFile.write("\"" + str(status) + "\"" + "," +  "\"\"" + "," + "\"\"" +  "," + "\"\"" + message + "\n")
    writeFile.close()

if __name__ == '__main__':
    
    TCP_IP=""
    TCP_PORT=5005

    Buffer_Size = 256

    server =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    address = (TCP_IP, TCP_PORT)

    server.bind(address)

    server.listen(1)

    print("[*] Started listening on: ", TCP_IP, ": ", TCP_PORT)

    client, addr = server.accept()
    print("[*] Got a connection from: " , addr[0],":", addr[1])
    
    cellCount = int(1);
    fpcid = []
    fsignal = []
    flacN = []
    fcidN = []

    while True:
    
        recvData = client.recv(Buffer_Size)
        if not recvData: break
    
        client.send(recvData)
         
        del fpcid[:]
        del fcidN[:]
        del flacN[:]
        del fsignal[:]
        
        conElements = recvData.decode().split(',') 
        
        if conElements[0] == "NB":
            for j in range(len(conElements)):
                conElements[j] = conElements[j].strip('"')
                cellCount = int((j-4)/2)
                
                if j == 1 :
                    fmcc = conElements[j]
                elif j == 2:
                    fmnc = conElements[j]
                elif j == 3:
                    fcid = conElements[j]
                elif j == 4:
                    flac = conElements[j]  
                if j > 4 and j%2 == 1:
                    fpcid.append(conElements[j])
                elif j > 4 and j%2 == 0:
                    fsignal.append(conElements[j])  
            
            find_pos_NB(fmcc,fmnc,fcid,flac,fpcid,fsignal,cellCount)  
            
        elif conElements[0] == "GSM":
            for j in range(len(conElements)):
                conElements[j] = conElements[j].strip('"')
                cellCount = int((j-4)/3)
        
                if j == 1 :
                    fmcc = conElements[j]
                elif j == 2:
                    fmnc = conElements[j]
                elif j == 3:
                    flac = conElements[j]
                elif j == 4:
                    fcid = conElements[j]
                elif j > 4 and j%3 == 0:
                    flacN.append(conElements[j])
                elif j > 4 and j%3 == 1:
                    fcidN.append(conElements[j])
                elif j > 4 and j%3 == 2:
                    fsignal.append(conElements[j])
        
            find_pos_GSM(fmcc,fmnc,fcid,flac,fcidN,flacN,fsignal,cellCount)
        
        
      
    