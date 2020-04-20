import pandas as pd
from pandas_datareader import data
from datetime import datetime, timedelta
from Operations import ReadSheet,catDict
import RPi.GPIO as GPIO
import time
import os



def LedOnOff_Blue():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(24,GPIO.OUT)
    print("LED on")
    GPIO.output(24,GPIO.HIGH)
    time.sleep(1)
    print("LED off")
    GPIO.output(24,GPIO.LOW)





# Declare class
readSheet=ReadSheet()

# Declare function
sheetCList=readSheet.Authorization_Currency()
sheetOList=readSheet.Authorization_Oil()
sheetSList=readSheet.Authorization_Stock()
todayStr, nowDate, nowTime=readSheet.GetDateTime()

today=datetime.now()
dm1 = today - timedelta(days=1)
dm3 = today - timedelta(days=3)
d=todayStr
dm3=dm3.strftime("%Y-%m-%d")

groupList=[]
ckeys=list(catDict.keys())
for m in ckeys:
    for n in catDict[m]:
        groupList.append(n)

readFlag=False
def ReadData(groupList,d,dm3,readFlag):
    try:
        dfIn= data.DataReader(groupList,start=d,data_source='yahoo') #['Adj Close']
        readFlag=True
        print(' Today data logged ')
    except:
        dfIn= data.DataReader(groupList,start=dm3,data_source='yahoo') #['Adj Close']
        readFlag=False
        print(' today data not available ')
    return dfIn, readFlag

iteration=10
for i in range(1,iteration):
    print('attempt :',i)
    if(readFlag==False):
        dfIn, readFlag=ReadData(groupList,d,dm3,readFlag)
    else:
        break

dfPre=dfIn.tail(1).copy()

dfOil=dfPre['Adj Close'][catDict['oil']]
dfCurrency=dfPre['Adj Close'][catDict['currency']]

listDfCurrency=[]
for n in catDict['currency']:
    dfn=dfPre['Adj Close'][n].to_frame()
    dfn.columns=['Adj Close']
    listDfCurrency.append(dfn)

listDfStock=[]
for n in catDict['stock']:
    dfn=pd.concat([dfPre['Volume'][n],dfPre['Adj Close'][n]],axis=1)
    dfn.columns=['Volume','Adj Close']
    listDfStock.append(dfn)
   
listDfOil=[]
for n in catDict['oil']:
    dfn=dfPre['Adj Close'][n].to_frame()
    dfn.columns=['Adj Close']
    listDfOil.append(dfn)
    
czip=zip(sheetCList, listDfCurrency)
for i,j in czip:
    #print(i, ' :: ',j['Adj Close'].values.tolist()[0],' :: ',readSheet.Date2TString(j.index.tolist()[0]))
    sheet=i
    dateIn= readSheet.Date2TString(j.index.tolist()[0])  
    priceIn= str(j['Adj Close'].values.tolist()[0])
    readSheet.InsertNewValue_1(todayStr, nowDate, nowTime, sheet, dateIn, priceIn)

ozip=zip(sheetOList, listDfOil)
for i,j in ozip:
    #print(i, ' :: ',j['Adj Close'].values.tolist()[0],' :: ',readSheet.Date2TString(j.index.tolist()[0]))
    sheet=i
    dateIn= readSheet.Date2TString(j.index.tolist()[0])  
    priceIn= str(j['Adj Close'].values.tolist()[0])
    readSheet.InsertNewValue_1(todayStr, nowDate, nowTime, sheet, dateIn, priceIn)

szip=zip(sheetSList, listDfStock)
for i,j in szip:
    #print(i, ' :: ',j['Adj Close'].values.tolist()[0],' :: ',readSheet.Date2TString(j.index.tolist()[0]))
    sheet=i
    dateIn= readSheet.Date2TString(j.index.tolist()[0])  
    priceIn= str(j['Adj Close'].values.tolist()[0])
    volumeIn=str(j['Volume'].values.tolist()[0])
    readSheet.InsertNewValue_2(todayStr, nowDate, nowTime, sheet, dateIn, priceIn,volumeIn)

LedOnOff_Blue()