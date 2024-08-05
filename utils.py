import requests
import subprocess
import sys
import urllib3

RED = "\033[91m {}\033[00m"
GREEN = "\033[92m {}\033[00m"
YELLOW = "\033[93m {}\033[00m"
PURPLE = "\033[95m {}\033[00m"

# a function that creates a dict with the champion names as the keys and the champion ids as the values
def champ2idmap() -> dict:
    champ2id = {}
    with open("champids.txt") as f:
        for line in f:
            (key, val) = line.split(':')
            champ2id[val.replace('\n','').replace(' ','').lower()] = int(key)
    return champ2id

CHAMPS = champ2idmap()

# A function to extract the client process ID (PID) and the authentication token
def getcluprops() -> tuple:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # lcu api requires the port number that the client using on ur pc and its pw
    txt = subprocess.run('wmic PROCESS WHERE name=\'LeagueClientUx.exe\' GET commandline',
                        shell=True, capture_output=True, text=True)
    cmd_output = txt.stdout.replace('=','"').split('"')
    port = int(cmd_output[cmd_output.index('--app-port')+1])
    auth = cmd_output[cmd_output.index('--remoting-auth-token')+1]
    auth = requests.auth.HTTPBasicAuth('riot', auth)
    return (port,auth)

PORT, AUTH = getcluprops()

# a shorthand to make requests with the client
def req(type:str, link:str, data:dict = {}) -> requests.request:
    # https://stackoverflow.com/questions/68186451/what-is-the-proper-way-of-using-python-requests-requests-requestget-o
    return requests.request(method=type,auth=AUTH,url=f'https://127.0.0.1:{PORT}{link}',json=data,verify=False)


# takes a dict returns a tuple with ban and pick ids
def extractid(session) -> tuple:
    actions = session.get('actions')
    cell_id = session.get('localPlayerCellId')
    pick_id,pick_index,ban_id,ban_index=None,None,None,None
    # banId = cellId
    # i looped for the ban id cuz idk in the if the tourenaments have the same id for the cell and ban 
    for index,player in enumerate(actions[0]):
        if int(player.get('actorCellId')) == cell_id:
            ban_id = player.get('id')
            ban_index = index


    for index_0,scene in enumerate(actions[2:],start=2):
        for index_1,player in enumerate(scene):
            if int(player.get('actorCellId')) == cell_id:
                pick_id = player.get('id')
                pick_index = [index_0,index_1]

    # print(f'{cell_id},{ban_id},{pick_id},p_in={pick_index}')
    return (cell_id,ban_id,pick_id,ban_index,pick_index)

# select will make a POST request to the server with the player's actorID and the champ ID to hover over that champ
def select(actorId:int,champ:str):
    champId = CHAMPS.get(champ)
    print(f'u selected {champ}')
    req(type='PATCH',link=f'/lol-champ-select/v1/session/actions/{actorId}',data={'championId': champId})


# pick and ban got the same api endpoint so this works for the ban too
def pick(actorId:int,pick_list:list) -> bool:
    if len(pick_list) < 1: 
        # dont run the function if the list is empty as its pointless anyway (this will activate the lock of ban or pick)
        return True
    for champ in pick_list:
        print(f'attempting to ban {champ}')
        champid = CHAMPS.get(champ)
        res = req(type='PATCH',link=f'/lol-champ-select/v1/session/actions/{actorId}',data={'championId': champid})
        print(f'status for selecting {res.status_code}')
        res = req(type='POST',link=f'/lol-champ-select/v1/session/actions/{actorId}/complete',data={'championId': champid})
        print(f'status for locking {res.status_code}')
        if res.status_code == 204:
            print(f'u picked {champ}')
            return True
    return False
    
# this function will check for the champion names retrieved from the user's input and return a list with the only recognized champion names (from the text file)
def validate(pick_list:list) -> list:
    valid,nonvalid = [] , []
    for selection in pick_list :
        if CHAMPS.get(selection):
            valid.append(selection)
        else:
            nonvalid.append(selection)
    print()
    if len(nonvalid) > 0:
        print(YELLOW.format('ALERT:'),nonvalid,'isnt available')    
    return valid


# assuming that the input is splitted by hyphens
def inputParser(inp:str) -> list:
    return inp.replace(' ','').lower().split('-')
