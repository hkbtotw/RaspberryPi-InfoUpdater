from pandas_datareader import data
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, datetime
import pytz
import RPi.GPIO as GPIO
import time
import os


colDict={
    'Date':1,
    'Price':2,
    'UpdateTime':3
}


def LedOnOff_Green():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(23,GPIO.OUT)
    print("LED on")
    GPIO.output(23,GPIO.HIGH)
    time.sleep(1)
    print("LED off")
    GPIO.output(23,GPIO.LOW)

class Update_Time(object):
    def __init__(self):
        self.secret_path_1=r'/home/pi/Project/DataCollection/CheckInOutReminder-e2ff28c53e80.json'
        self.secret_path_2=r'./CheckInOutReminder-e2ff28c53e80.json'
        self.scope= ['https://spreadsheets.google.com/feeds',
                              'https://www.googleapis.com/auth/drive']

    def Authorization(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_1, self.scope)
        except:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.secret_path_2, self.scope)
        client = gspread.authorize(creds) 
        sheet = client.open("DataCollection_1").sheet1
        return sheet
    
    def Date2TString(self, dateIn):
        return dateIn.strftime("%Y-%m-%d")

    def GetDateTime(self):
        todayUTC=datetime.today()
        nowUTC=datetime.now()
        # dd/mm/YY H:M:S
        to_zone = pytz.timezone('Asia/Bangkok')

        today=todayUTC.astimezone(to_zone)
        now=nowUTC.astimezone(to_zone)

        todayStr=today.strftime("%Y-%m-%d")
        nowDate = now.strftime("%Y-%m-%d")
        nowTime = now.strftime("%H:%M:%S")

        print(' today : ',todayStr)
        print(nowDate, ' ==> ', nowTime)
        return todayStr, nowDate, nowTime

    def ReadCurrentStatus(self,todayStr, nowDate, nowTime, sheet):
        lenRecords=len(sheet.get_all_values())
        print(" len : ",lenRecords)
        lastDate=sheet.cell(lenRecords,1).value
        print(' lastDate : ',lastDate)
        todayRow=lenRecords
        row_index=todayRow
        col_index=colDict['Price']
        currentPrice=sheet.cell(row_index,col_index).value
        col_index=colDict['Date']
        currentDate=sheet.cell(row_index,col_index).value
        print(' date : ', currentDate, ' ::' , currentPrice)
        return currentDate, currentPrice

    def InsertNewValue(self,todayStr, nowDate, nowTime, sheet, dateIn, priceIn):
        lenRecords=len(sheet.get_all_values())
        list_of_hashes=sheet.get_all_records()
        lenHash=len(list_of_hashes)
        print(" len : ",lenRecords)
        lastDate=sheet.cell(lenRecords,1).value
        print(' lastDate : ',lastDate)
        lenDate=len(list_of_hashes[lenHash-1]['Date'])
        if(todayStr == lastDate):
            todayRow=lenRecords
            row_index=todayRow
            col_index=colDict['Price']
            message=priceIn
            sheet.update_cell(row_index, col_index,message)
            col_index=colDict['UpdateTime']
            message=nowTime
            sheet.update_cell(row_index, col_index,message)
            print('Updated at ', nowTime)
        else:
            todayRow=lenRecords+1
            row_index=todayRow
            col_index=colDict['Date']
            message=todayStr
            sheet.update_cell(row_index, col_index,message)
            col_index=colDict['Price']
            message=priceIn
            sheet.update_cell(row_index, col_index,message)
            col_index=colDict['UpdateTime']
            message=nowTime
            sheet.update_cell(row_index, col_index,message)
            print('Updated on ', todayStr, ' :: ', nowTime)


# Only get the adjusted close.
set= data.DataReader("^SET.BK", 
                       start='2015-1-1', 
                       data_source='yahoo')['Adj Close']

#set.index   #latest date
#set[0]    #value

upTime=Update_Time()
sheet=upTime.Authorization()
todayStr, nowDate, nowTime=upTime.GetDateTime()

currentDate, currentPrice=upTime.ReadCurrentStatus(todayStr, nowDate, nowTime, sheet)

dateIn = upTime.Date2TString(set.index)
LedOnOff_Green()
upTime.InsertNewValue(todayStr, nowDate, nowTime, sheet, dateIn[0], str(set[0]))
