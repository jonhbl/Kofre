import re
from datetime import datetime
import csv
from os import listdir

files = listdir('logs')
calls = []
Events = {}
for fileName in files:

    file = open("logs"+'/'+fileName, 'r', encoding='utf-16')
    fileLines = file.readlines()
    
    firstLogLine = 0
    for line in fileLines:
        if ";" in line:
            firstLogLine = fileLines.index(line)
            break

    def getCallId(callColumn: str, sequenceColumn: str) -> str:
        callId = callColumn.split('=')[-1].replace(' ','')
        if "(" in callId:
                callId = callId.split("(")[0]
        sequence = sequenceColumn.split('=')[-1].replace(' ','')
        if "(" in sequence:
            sequence = sequence.split("(")[0]
        return callId+"_"+sequence

    def getSite(siteColumn: str) -> str:
        site = siteColumn.split('=')[-1].replace(' ','')
        if "(" in site:
                site = site.split("(")[0]
        return site

    logLines = fileLines[firstLogLine:]

    START_OFF_CALL_EVENT = "Controlling Zone Update - Start of Call"
    START_OF_CALL_UPDATE_EVENT = "Call Activity Update - Start of Call"
    PTT_EVENT = "Controlling Zone Update - PTT-ID Active Control"
    PTT_UPDATE_EVENT = "Call Activity Update - PTT-ID Update Active"
    END_OFF_CALL_EVENT = "Controlling Zone Update - End of Call"
    CALL_INFORMATION_EVENT = "Call Activity Update - Call Information Change"
    CALL_EVENT_CODE = 1
    PTT_EVENT_CODE = 2
    CALL_INFORMATION_EVENT_CODE = 3

    
    callIds = []
    print(f"{datetime.now()} - Arquivo {fileName} com {len(logLines)} linhas")
    for line in logLines:
        column = line.split(";")
        if START_OFF_CALL_EVENT in column[0]:
            callId = getCallId(column[0], column[1])
            startTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S") 
            id = re.search(r'Individual =(.*?)\(',column[14]).group(1).replace(' ','')
            channel = re.search(r'\"(.*?)\"',column[18]).group(1).replace(' ','')
            talkGroup = re.search(r'Secondary ID =(.*?)\(', column[18]).group(1).replace(' ','')
            if callId not in Events:
                Events[callId] = {}
                Events[callId]["Data"] = startTime
                Events[callId]["ID"] = id
                Events[callId]["Grupo"] = talkGroup
                Events[callId]["Evento"] = line
                Events[callId]["CodEvento"] = CALL_EVENT_CODE
                Events[callId]["Canal"] = channel
        elif START_OF_CALL_UPDATE_EVENT in column[0]:
            callId = getCallId(column[0], column[1])
            if callId in Events:
                if Events[callId]["CodEvento"] == CALL_EVENT_CODE:
                    siteId = getSite(column[6])
                    Events[callId]["site"] = siteId
        elif PTT_EVENT in column[0]:
            callId = getCallId(column[0], column[1]).split("_")[0]
            sequence = int(getCallId(column[0], column[1]).split("_")[1])
            callIdSequence = callId+"_"+str(sequence)
            startTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S") 
            id = re.search(r'Individual =(.*?)\(',column[14]).group(1).replace(' ','')
            talkGroup = re.search(r'Secondary ID =(.*?)\(', column[18]).group(1).replace(' ','')
            channel = re.search(r'\"(.*?)\"',column[18]).group(1).replace(' ','')
            if (sequence > 1):
                previousCall = callId+"_"+str(sequence-1)
                Events[previousCall]["Duracao"] = int((startTime - Events[previousCall]["Data"]).total_seconds())

            if callIdSequence not in Events:
                Events[callIdSequence] = {}
                Events[callIdSequence]["Data"] = startTime
                Events[callIdSequence]["ID"] = id
                Events[callIdSequence]["Grupo"] = talkGroup
                Events[callIdSequence]["Evento"] = line
                Events[callIdSequence]["CodEvento"] = PTT_EVENT_CODE
                Events[callIdSequence]["Canal"] = channel
        elif PTT_UPDATE_EVENT in column[0]:
            callId = getCallId(column[0], column[1])
            if callId in Events:
                if Events[callId]["CodEvento"] == PTT_EVENT_CODE:
                    siteId = getSite(column[6])
                    Events[callId]["site"] = siteId
        elif CALL_INFORMATION_EVENT in column[0]:
            callId = getCallId(column[0], column[1])
            siteId = column[6].split('=')[-1].replace(' ','')
            startTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S") 
            if callId not in Events:
                Events[callId] = {}
                Events[callId]["site"] = siteId
                Events[callId]["Evento"] = line.replace(';',',')
                Events[callId]["Data"] = startTime
                Events[callId]["CodEvento"] = CALL_INFORMATION_EVENT_CODE
        elif END_OFF_CALL_EVENT in column[0]:
            callId = getCallId(column[0], column[1]).split("_")[0]
            sequence = int(getCallId(column[0], column[1]).split("_")[1])
            endTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S")
            callIdSequence = callId+"_"+str(sequence-1)
            if callIdSequence in Events:
                Events[callIdSequence]["Duracao"] = int((endTime - Events[callIdSequence]["Data"]).total_seconds())
                if Events[callIdSequence]["CodEvento"] is CALL_INFORMATION_EVENT_CODE:
                    id = re.search(r'Individual =(.*?)\(',column[14]).group(1).replace(' ','')
                    talkGroup = re.search(r'Secondary ID =(.*?)\(', column[18]).group(1).replace(' ','')
                    channel = re.search(r'\"(.*?)\"',column[18]).group(1).replace(' ','')
                    Events[callIdSequence]["Grupo"] = talkGroup
                    Events[callIdSequence]["Canal"] = channel
                    Events[callIdSequence]["ID"] = id
                    
    
for call in Events.items():
    if "Duracao" in call[1]:
        calls.append(call[1])

with open('logs.csv','w') as file:
    writer = csv.DictWriter(file, delimiter=';',fieldnames={"Data":1 , "ID":1 , "Grupo":1 , "Canal":1 , "Evento":1 , "CodEvento":1 , "Duracao":1, "site":1})
    writer.writeheader()
    for row in calls:
        writer.writerow(row)

print(f"{datetime.now()} - Execução finalizada")


        


        




