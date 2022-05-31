#!/usr/bin/env python
# coding: utf-8

# In[41]:


import re
from datetime import datetime
import csv
import os
import pandas as pd
import pyodbc


# In[2]:


def getCallId(callColumn: str, sequenceColumn: str) -> str:
        callId = callColumn.split('=')[-1].replace(' ','')
        if "(" in callId:
                callId = callId.split("(")[0]
        sequence = sequenceColumn.split('=')[-1].replace(' ','')
        if "(" in sequence:
            sequence = sequence.split("(")[0]
        return callId+"_"+sequence


# In[3]:


def getSite(siteColumn: str) -> str:
    site = siteColumn.split('=')[-1].replace(' ','')
    if "(" in site:
            site = site.split("(")[0]
    return site


# In[4]:


def getIDChannelTalkGroup(column):
    id_ = re.search(r'Individual =(.*?)\(',column[ID_POS]).group(1).replace(' ','')
    channel = re.search(r'\"(.*?)\"',column[CHANNEL_POS]).group(1).replace(' ','')
    talkGroup = re.search(r'Secondary ID =(.*?)\(', column[TALK_GROUP_POS]).group(1).replace(' ','')
    return id_,channel,talkGroup


# In[5]:


def StartOfCallEvent(column):
    callId = getCallId(column[0], column[1])
    startTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S") 
    id_, channel, talkGroup = getIDChannelTalkGroup(column)
    if callId not in events:
        events[callId] = {}
        events[callId]["Data"] = startTime
        events[callId]["ID"] = id_
        events[callId]["Grupo"] = talkGroup
        events[callId]["Evento"] = line
        events[callId]["CodEvento"] = CALL_EVENT_CODE
        events[callId]["Canal"] = channel


# In[6]:


def StartOfCallUpdateEvent(column):
    callId = getCallId(column[0], column[1])
    if callId in events:
        if events[callId]["CodEvento"] == CALL_EVENT_CODE:
            siteId = getSite(column[6])
            events[callId]["site"] = siteId


# In[7]:


def PttEvent(column):
    callId = getCallId(column[0], column[1]).split("_")[0]
    sequence = int(getCallId(column[0], column[1]).split("_")[1])
    callIdSequence = callId+"_"+str(sequence)
    startTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S") 
    id_, channel, talkGroup = getIDChannelTalkGroup(column)
    if (sequence > 1):
        previousCall = callId+"_"+str(sequence-1)
        events[previousCall]["Duracao"] = int((startTime - events[previousCall]["Data"]).total_seconds())
    if callIdSequence not in events:
        events[callIdSequence] = {}
        events[callIdSequence]["Data"] = startTime
        events[callIdSequence]["ID"] = id_
        events[callIdSequence]["Grupo"] = talkGroup
        events[callIdSequence]["Evento"] = line
        events[callIdSequence]["CodEvento"] = PTT_EVENT_CODE
        events[callIdSequence]["Canal"] = channel


# In[8]:


def PttUpdateEvent(column):
    callId = getCallId(column[0], column[1])
    if callId in events:
        if events[callId]["CodEvento"] == PTT_EVENT_CODE:
            siteId = getSite(column[6])
            events[callId]["site"] = siteId


# In[9]:


def CallInformationEvent(column):
    callId = getCallId(column[0], column[1])
    siteId = column[6].split('=')[-1].replace(' ','')
    startTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S") 
    if callId not in events:
        events[callId] = {}
        events[callId]["site"] = siteId
        events[callId]["Evento"] = line.replace(';',',')
        events[callId]["Data"] = startTime
        events[callId]["CodEvento"] = CALL_INFORMATION_EVENT_CODE


# In[10]:


def EndOfCallEvent(column):
    callId = getCallId(column[0], column[1]).split("_")[0]
    sequence = int(getCallId(column[0], column[1]).split("_")[1])
    endTime = datetime.strptime(re.search(r'\[(.*?)\]',column[0]).group(1), "%m/%d/%y %H:%M:%S")
    callIdSequence = callId+"_"+str(sequence-1)
    if callIdSequence in events:
        events[callIdSequence]["Duracao"] = int((endTime - events[callIdSequence]["Data"]).total_seconds())
        if events[callIdSequence]["CodEvento"] is CALL_INFORMATION_EVENT_CODE:
            id_, channel, talkGroup = getIDChannelTalkGroup(column)
            events[callIdSequence]["Grupo"] = talkGroup
            events[callIdSequence]["Canal"] = channel
            events[callIdSequence]["ID"] = id_


# In[11]:


START_OF_CALL_EVENT = "Controlling Zone Update - Start of Call"
START_OF_CALL_UPDATE_EVENT = "Call Activity Update - Start of Call"
PTT_EVENT = "Controlling Zone Update - PTT-ID Active Control"
PTT_UPDATE_EVENT = "Call Activity Update - PTT-ID Update Active"
END_OF_CALL_EVENT = "Controlling Zone Update - End of Call"
CALL_INFORMATION_EVENT = "Call Activity Update - Call Information Change"
CALL_EVENT_CODE = 1
PTT_EVENT_CODE = 2
CALL_INFORMATION_EVENT_CODE = 3
ID_POS = 16
TALK_GROUP_POS = 23
CHANNEL_POS = 16


# In[12]:


files = [arq for arq in os.listdir('logs') if '.txt' in arq]
calls = []
events = {}
files


# In[14]:


for fileName in files:
    file = open("logs"+'/'+fileName, 'r', encoding='utf-16')
    fileLines = file.readlines()
    firstLogLine = 0
    for line in fileLines:
        if ";" in line:
            firstLogLine = fileLines.index(line)
            break
    logLines = fileLines[firstLogLine:]
    callIds = []
    print(f"{datetime.now()} - Arquivo {fileName} com {len(logLines)} linhas")
    for line in logLines:
        column = line.split(";")
        if START_OF_CALL_EVENT in column[0]:
            StartOfCallEvent(column)

        elif START_OF_CALL_UPDATE_EVENT in column[0]:
            StartOfCallUpdateEvent(column)

        elif PTT_EVENT in column[0]:
            PttEvent(column)

        elif PTT_UPDATE_EVENT in column[0]:
            PttUpdateEvent(column)

        elif CALL_INFORMATION_EVENT in column[0]:
            CallInformationEvent(column)

        elif END_OF_CALL_EVENT in column[0]:
            EndOfCallEvent(column)


# In[42]:


class SQLConnect():
    def __init__(self,server, database, username=None, password=None, strConnection=None)->None:
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.strConnection = strConnection
        self.connection = pyodbc.connect(strConnection)
        self.cursor = self.connection.cursor()
    def create(self, data:datetime, id_:str, grupo:str, canal:str, evento:str, codEvento:int, duracao:float , site:int):
        sql = f"INSERT INTO ----- VALUES ({data},{id_},{grupo},{canal},{evento},{codEvento},{duracao},{site})"


# In[15]:


for call in events.items():
    if "Duracao" in call[1]:
        calls.append(call[1])


# In[38]:


#sqlClient = SQLConnect(...)


# In[39]:


for event in events.values():
    #(event['Data'],event['ID'],event['Grupo'],event['Evento'],event['CodEvento'],event['Canal'],event['site'],event['Duracao']) 


# In[16]:


pd.DataFrame(events).T


# In[ ]:


print(f"{datetime.now()} - Execução finalizada")

