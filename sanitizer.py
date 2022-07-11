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


def get_call_id(call_column: str, sequence_column: str) -> str:
    call_id = call_column.split('=')[-1].replace(' ', '')
    if "(" in call_id:
        call_id = call_id.split("(")[0]
    sequence = sequence_column.split('=')[-1].replace(' ', '')
    if "(" in sequence:
        sequence = sequence.split("(")[0]
    return f"{call_id}_{sequence}"


def get_site(site_column: str) -> str:
    site = site_column.split('=')[-1].replace(' ', '')
    if "(" in site:
        site = site.split("(")[0]
    return int(site)


def get_params_pos(line: str) -> tuple:
    for i, param in enumerate(line.split(';')):
        if('REQUESTER {Individual = ' in param):
            id_ = i
        if('TARGET {Secondary ID = ' in param):
            channel = i
            talk_group = i
    return id_, channel, talk_group


def get_id_channel_talk_group(column: list) -> tuple:
    id_ = re.search(r'Individual =(.*?)\(', column[ID_POS]).group(1).replace(' ', '')
    channel = re.search(r'\"(.*?)\"', column[CHANNEL_POS]).group(1).replace(' ', '')
    talk_group = re.search(r'Secondary ID =(.*?)\(', column[TALK_GROUP_POS]).group(1).replace(' ', '')
    return id_, channel, talk_group


def start_of_call_event(events: dict, column: list, line: str) -> None:
    call_id = get_call_id(column[0], column[1])
    start_time = datetime.strptime(re.search(r'\[(.*?)\]', column[0]).group(1), "%m/%d/%y %H:%M:%S")
    id_, channel, talk_group = get_id_channel_talk_group(column)
    if call_id not in events:
        events[call_id] = {}
        events[call_id]["Data"] = start_time
        events[call_id]["ID"] = id_
        events[call_id]["Grupo"] = talk_group
        events[call_id]["Evento"] = line.replace(';', ',').replace('\n', '').replace("\"", "'").replace("'", "")
        events[call_id]["CodEvento"] = CALL_EVENT_CODE
        events[call_id]["Canal"] = channel
    return events


def start_of_call_update_event(events: dict, column: list) -> None:
    call_id = get_call_id(column[0], column[1])
    if call_id in events:
        if events[call_id]["CodEvento"] == CALL_EVENT_CODE:
            site_id = get_site(column[7])
            events[call_id]["site"] = site_id
    return events


def ptt_event(events: dict, column: list, line: str) -> None:
    call_id = get_call_id(column[0], column[1]).split("_")[0]
    sequence = int(get_call_id(column[0], column[1]).split("_")[1])
    call_id_sequence = f"{call_id}_{str(sequence)}"
    start_time = datetime.strptime(re.search(r'\[(.*?)\]', column[0]).group(1), "%m/%d/%y %H:%M:%S")
    id_, channel, talk_group = get_id_channel_talk_group(column)
    if (sequence > 1):
        try:
            previous_call = f"{call_id}_{str(sequence-1)}"
            events[previous_call]["Duracao"] = int((start_time - events[previous_call]["Data"]).total_seconds())
        except KeyError:
            try:
                previous_call = [event for event in events.keys() if call_id in event][-1]
                events[previous_call]["Duracao"] = int((start_time - events[previous_call]["Data"]).total_seconds())
            except IndexError:  # Eventos Anteriores
                return events
    if call_id_sequence not in events:
        events[call_id_sequence] = {}
        events[call_id_sequence]["Data"] = start_time
        events[call_id_sequence]["ID"] = id_
        events[call_id_sequence]["Grupo"] = talk_group
        events[call_id_sequence]["Evento"] = line.replace(';', ',').replace('\n', '').replace("\"", "'").replace("'", "")
        events[call_id_sequence]["CodEvento"] = PTT_EVENT_CODE
        events[call_id_sequence]["Canal"] = channel
    return events


def ptt_update_event(events: dict, column: list) -> None:
    call_id = get_call_id(column[0], column[1])
    if call_id in events:
        if events[call_id]["CodEvento"] == PTT_EVENT_CODE:
            site_id = get_site(column[6])
            events[call_id]["site"] = site_id
    return events


def call_information_event(events: dict, column: list, line: str) -> None:
    call_id = get_call_id(column[0], column[1])
    site_id = column[6].split('=')[-1].replace(' ', '')
    start_time = datetime.strptime(re.search(r'\[(.*?)\]', column[0]).group(1), "%m/%d/%y %H:%M:%S")
    if call_id in events:
        events[call_id]["site"] = site_id
        events[call_id]["Evento"] = line.replace(';', ',').replace('\n', '').replace("\"", "'").replace("'", "")
        events[call_id]["Data"] = start_time
        events[call_id]["CodEvento"] = CALL_INFORMATION_EVENT_CODE
    return events


def end_of_call_event(events: dict, column: list) -> None:
    call_id = get_call_id(column[0], column[1]).split("_")[0]
    sequence = int(get_call_id(column[0], column[1]).split("_")[1])
    end_time = datetime.strptime(re.search(r'\[(.*?)\]', column[0]).group(1), "%m/%d/%y %H:%M:%S")
    call_id_sequence = f"{call_id}_{str(sequence-1)}"
    if call_id_sequence in events:
        events[call_id_sequence]["Duracao"] = int((end_time - events[call_id_sequence]["Data"]).total_seconds())
        if events[call_id_sequence]["CodEvento"] is CALL_INFORMATION_EVENT_CODE:
            id_, channel, talk_group = get_id_channel_talk_group(column)
            events[call_id_sequence]["Grupo"] = talk_group
            events[call_id_sequence]["Canal"] = channel
            events[call_id_sequence]["ID"] = id_
    return events


def read_file(file_name: str) -> list:
    with open(file_name, 'r', encoding='utf-16') as file:
        file_lines = file.readlines()
        first_log_line = 0
        for line in file_lines:
            if ";" in line:
                first_log_line = file_lines.index(line)
                break
        log_lines = file_lines[first_log_line:]
    return log_lines


def att_events(events: dict, column: list, line: str) -> None:
    if START_OF_CALL_EVENT in column[0]:
        events = start_of_call_event(events, column, line)

    elif START_OF_CALL_UPDATE_EVENT in column[0]:
        events = start_of_call_update_event(events, column)

    elif PTT_EVENT in column[0]:
        events = ptt_event(events, column, line)

    elif PTT_UPDATE_EVENT in column[0]:
        events = ptt_update_event(events, column)

    elif CALL_INFORMATION_EVENT in column[0]:
        events = call_information_event(events, column, line)

    elif END_OF_CALL_EVENT in column[0]:
        events = end_of_call_event(events, column)


def get_next_file_name(dir_: str, file_name: str, ) -> str:
    try:
        year_index = 0
        month_index = 1
        day_index = 2
        hour_index = 3
        file_info = file_name.split('_')
        time_str = "_".join(file_name.split('.')[1].split('_')[:5])
        next_time = datetime.strptime(time_str, "%Y_%m_%d_%H_%M") + timedelta(hours=1)

        file_info[year_index] = f"log.{next_time.year}"
        file_info[month_index] = f"{(next_time.month):02d}"
        file_info[day_index] = f"{(next_time.day):02d}"
        file_info[hour_index] = f"{(next_time.hour):02d}"

        next_file_info = "_".join(file_info[:hour_index + 1])
        files_arr = np.asarray(os.listdir(dir_))
        position = np.flatnonzero(np.core.defchararray.find(files_arr, next_file_info) != -1)[0]
        return files_arr[position]
    except IndexError:
        print(f'Próximo arquivo:{next_file_info} não está presente!')
        return None


def get_events(dir_: str, file_name: str) -> dict:
    file_path = os.path.join(dir_, file_name)
    calls = []
    events = {}
    log_lines = read_file(file_path)
    print(f"{datetime.now()} - Arquivo {file_name} com {len(log_lines)} linhas")
    global ID_POS, CHANNEL_POS, TALK_GROUP_POS
    for line in log_lines:
        try:
            ID_POS, CHANNEL_POS, TALK_GROUP_POS = get_params_pos(line)
            print('Atributos encontrados!')
            break
        except UnboundLocalError:
            pass
    for line in log_lines:
        column = line.split(";")
        att_events(events, column, line)

    incomplete_events = [key for key, value in events.items() if list(value.keys()) != COMPLETE_EVENT]
    if(incomplete_events):
        print('Existem eventos incompletos.')
        try:
            next_file_name = get_next_file_name(dir_, file_name)
            next_file_path = os.path.join(dir_, next_file_name)
            next_log_lines = read_file(next_file_path)
            for event in incomplete_events:
                envent_id = event.split('_')[0]
                for line in [line for line in next_log_lines if envent_id in line]:
                    column = line.split(";")
                    att_events(events, column, line)
                print(f"Evento {envent_id} foi adicionado pela informação subsequente!")
        except FileNotFoundError:
            print(f'Próximo arquivo não está presente!\n\t{next_file_name}')
        except IndexError:
            print(f'Arquivo: {file_name} está fora do padrão!')

    for call in events.items():
        if "Duracao" in call[1]:
            calls.append(call[1])
    # print(f"{datetime.now()} - Execução finalizada")
    return events
