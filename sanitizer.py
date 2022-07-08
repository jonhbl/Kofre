import re
import numpy as np
import os
from datetime import datetime, timedelta

START_OF_CALL_EVENT = "Controlling Zone Update - Start of Call"
START_OF_CALL_UPDATE_EVENT = "Call Activity Update - Start of Call"
PTT_EVENT = "Controlling Zone Update - PTT-ID Active Control"
PTT_UPDATE_EVENT = "Call Activity Update - PTT-ID Update Active"
END_OF_CALL_EVENT = "Controlling Zone Update - End of Call"
CALL_INFORMATION_EVENT = "Call Activity Update - Call Information Change"
CALL_EVENT_CODE = 1
PTT_EVENT_CODE = 2
CALL_INFORMATION_EVENT_CODE = 3
COMPLETE_EVENT = ['Data', 'ID', 'Grupo', 'Evento', 'CodEvento', 'Canal', 'site', 'Duracao']

def getCallId(callColumn: str, sequenceColumn: str) -> str:
        callId = callColumn.split('=')[-1].replace(' ','')
        if "(" in callId:
                callId = callId.split("(")[0]
        sequence = sequenceColumn.split('=')[-1].replace(' ','')
        if "(" in sequence:
            sequence = sequence.split("(")[0]   
        return f"{callId}_{sequence}"

def getSite(siteColumn: str) -> str:
    """
    
    """
    site = siteColumn.split('=')[-1].replace(' ','')
    if "(" in site:
            site = site.split("(")[0]
    return int(site)

def getParamsPos(line: str) -> tuple:
    for i,param in enumerate(line.split(';')):
        if('REQUESTER {Individual = ' in param):
            id_ = i
        if('TARGET {Secondary ID = ' in param):
            channel = i
            talk_group = i
    return id_, channel, talk_group

def getIDChannelTalkGroup(column: list) -> tuple:
    id_ = re.search(r'Individual =(.*?)\(',column[ID_POS]).group(1).replace(' ','')
    channel = re.search(r'\"(.*?)\"',column[CHANNEL_POS]).group(1).replace(' ','')
    talkGroup = re.search(r'Secondary ID =(.*?)\(', column[TALK_GROUP_POS]).group(1).replace(' ','')
    return id_, channel, talkGroup

def StartOfCallEvent(events: dict, column: list, line: str)->None:
    callId = getCallId(column[0], column[1])
    startTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S") 
    id_, channel, talkGroup = getIDChannelTalkGroup(column)
    if callId not in events:
        events[callId] = {}
        events[callId]["Data"] = startTime
        events[callId]["ID"] = id_
        events[callId]["Grupo"] = talkGroup
        events[callId]["Evento"] = line.replace(';',',').replace('\n','').replace("\"","'").replace("'","")
        events[callId]["CodEvento"] = CALL_EVENT_CODE
        events[callId]["Canal"] = channel
    return events

def StartOfCallUpdateEvent(events: dict, column: list)->None:
    callId = getCallId(column[0], column[1])
    if callId in events:
        if events[callId]["CodEvento"] == CALL_EVENT_CODE:
            siteId = getSite(column[7])
            events[callId]["site"] = siteId
    return events

def PttEvent(events: dict, column: list, line: str)->None:
    callId = getCallId(column[0], column[1]).split("_")[0]
    sequence = int(getCallId(column[0], column[1]).split("_")[1])
    callIdSequence = f"{callId}_{str(sequence)}"
    startTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S") 
    id_, channel, talkGroup = getIDChannelTalkGroup(column)
    if (sequence > 1):
        try:
            previousCall = f"{callId}_{str(sequence-1)}"
            events[previousCall]["Duracao"] = int((startTime - events[previousCall]["Data"]).total_seconds())
        except KeyError:
            try:    
                previousCall = [event for event in events.keys() if callId in event][-1]
                events[previousCall]["Duracao"] = int((startTime - events[previousCall]["Data"]).total_seconds())
            except IndexError:
                #Eventos anteriores
                return events
    if callIdSequence not in events:
        events[callIdSequence] = {}
        events[callIdSequence]["Data"] = startTime
        events[callIdSequence]["ID"] = id_
        events[callIdSequence]["Grupo"] = talkGroup
        events[callIdSequence]["Evento"] = line.replace(';',',').replace('\n','').replace("\"","'").replace("'","")
        events[callIdSequence]["CodEvento"] = PTT_EVENT_CODE
        events[callIdSequence]["Canal"] = channel
    return events

def PttUpdateEvent(events: dict, column: list)->None:
    callId = getCallId(column[0], column[1])
    if callId in events:
        if events[callId]["CodEvento"] == PTT_EVENT_CODE:
            siteId = getSite(column[6])
            events[callId]["site"] = siteId
    return events

def CallInformationEvent(events: dict, column: list,line: str)->None:
    callId = getCallId(column[0], column[1])
    siteId = column[6].split('=')[-1].replace(' ','')
    startTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S") 
    if callId not in events:
        events[callId] = {}
        events[callId]["site"] = siteId
        events[callId]["Evento"] = line.replace(';',',').replace('\n','').replace("\"","'").replace("'","")
        events[callId]["Data"] = startTime
        events[callId]["CodEvento"] = CALL_INFORMATION_EVENT_CODE
    return events

def CallInformationEvent(events: dict, column: list,line: str)->None:
    callId = getCallId(column[0], column[1])
    siteId = column[6].split('=')[-1].replace(' ','')
    startTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S") 
    if callId in events:
        #events[callId] = {}
        #events[callId]["site"] = siteId
        #events[callId]["Evento"] = line.replace(';',',').replace('\n','').replace("\"","'").replace("'","")
        #events[callId]["Data"] = startTime
        events[callId]["CodEvento"] = CALL_INFORMATION_EVENT_CODE
    return events

def EndOfCallEvent(events: dict, column: list)->None:
    callId = getCallId(column[0], column[1]).split("_")[0]
    sequence = int(getCallId(column[0], column[1]).split("_")[1])
    endTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S")
    callIdSequence = f"{callId}_{str(sequence-1)}"
    if callIdSequence in events:
        events[callIdSequence]["Duracao"] = int((endTime - events[callIdSequence]["Data"]).total_seconds())
        if events[callIdSequence]["CodEvento"] is CALL_INFORMATION_EVENT_CODE:
            id_, channel, talkGroup = getIDChannelTalkGroup(column)
            events[callIdSequence]["Grupo"] = talkGroup
            events[callIdSequence]["Canal"] = channel
            events[callIdSequence]["ID"] = id_
    return events

def readFile(fileName: str)->list:
    with open(fileName, 'r', encoding='utf-16') as file:
        fileLines = file.readlines()
        firstLogLine = 0
        for line in fileLines:
            if ";" in line:
                firstLogLine = fileLines.index(line)
                break
        logLines = fileLines[firstLogLine:]
    return logLines

def attEvents(events: dict, column: list, line: str)->None:
    if START_OF_CALL_EVENT in column[0]:
        events = StartOfCallEvent(events, column, line)

    elif START_OF_CALL_UPDATE_EVENT in column[0]:
        events = StartOfCallUpdateEvent(events, column)

    elif PTT_EVENT in column[0]:
        events = PttEvent(events, column, line)

    elif PTT_UPDATE_EVENT in column[0]:
        events = PttUpdateEvent(events, column)

    elif CALL_INFORMATION_EVENT in column[0]:
        events = CallInformationEvent(events, column, line)

    elif END_OF_CALL_EVENT in column[0]:
        events = EndOfCallEvent(events, column)

def incompleteEventBefore():
    pass

def incompleteEventAfter():
    pass

def getNextFileName(dir: str, fileName: str, )->str:
    try:
        yearIndex = 0
        monthIndex = 1
        dayIndex = 2
        hourIndex = 3
        fileInfo = fileName.split('_')
        time_str = "_".join(fileName.split('.')[1].split('_')[:5])
        next_time = datetime.strptime(time_str,"%Y_%m_%d_%H_%M")+timedelta(hours=1)

        fileInfo[yearIndex] = f"log.{next_time.year}"
        fileInfo[monthIndex] = f"{(next_time.month):02d}"
        fileInfo[dayIndex] = f"{(next_time.day):02d}"
        fileInfo[hourIndex] = f"{(next_time.hour):02d}"

        nextFileInfo = "_".join(fileInfo[:hourIndex+1])
        files_arr = np.asarray(os.listdir(dir))
        position = np.flatnonzero(np.core.defchararray.find(files_arr,nextFileInfo)!=-1)[0]
        return files_arr[position]
    except IndexError:
        print(f'Próximo arquivo não está presente!')
        return None

def getEvents(dir: str, fileName: str)->dict:
    filePath = os.path.join(dir, fileName)
    calls = []
    events = {}     
    logLines = readFile(filePath)
    print(f"{datetime.now()} - Arquivo {fileName} com {len(logLines)} linhas")
    global ID_POS, CHANNEL_POS, TALK_GROUP_POS
    for line in logLines:
        try:
            ID_POS, CHANNEL_POS, TALK_GROUP_POS = getParamsPos(line)
            print('Atributos encontrados!')
            break
        except UnboundLocalError:
            pass
            #print('Não há os atributos aqui!')
    
    for line in logLines:
        column = line.split(";")
        attEvents(events, column, line)
    
    incompleteEvents = [key for key,value in events.items() if list(value.keys())!=COMPLETE_EVENT]
    if(incompleteEvents):
        print('Existem eventos incompletos.')
        try:
            nextFileName = getNextFileName(dir, fileName)
            nextFilePath = os.path.join(dir, nextFileName)
            nextLogLines = readFile(nextFilePath)
            for event in incompleteEvents:
                eventId = event.split('_')[0]
                for line in [line for line in nextLogLines if eventId in line]:
                    column = line.split(";")
                    attEvents(events, column, line)
                print(f"Evento {eventId} foi adicionado pela informação subsequente!")
        except FileNotFoundError:
            print(f'Próximo arquivo não está presente!\n\t{nextFileName}')
        except IndexError:
            print(f'Arquivo: {fileName} está fora do padrão!')

    for call in events.items():
        if "Duracao" in call[1]:
            calls.append(call[1])

    #print(f"{datetime.now()} - Execução finalizada")

    return events


