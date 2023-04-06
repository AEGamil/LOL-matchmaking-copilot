from utils import *
import time

# clientProps = getcluprops()
# print(type(CHAMPS))

res = req(type='GET',link='/lol-summoner/v1/current-summoner')
sname = res.json().get('displayName','Summoner')


print(f'Hi{PURPLE.format(sname)} i hope you have a nice game without trollers ;)')
ban_input = input(f'\nEnter the name of the champion/s you want to{RED.format("ban")} (leave a dash "-" between them):\n')
banList = validate(inputParser(ban_input))
pick_input = input(f'\n\nEnter the name of the champion/s you want to{GREEN.format("pick")} (leave a dash "-" between them):\n')
pickList = validate(inputParser(pick_input))
print(RED.format('Your ban'),f'list consists of {len(banList)} : ',RED.format(banList))
print(GREEN.format('Your pick') ,f'list consists of {len(pickList)} : ',GREEN.format(pickList),end='\n')
print('\n\nHere we gooooooooo...')

# sys.exit()
banLock,pickLock = None, None
cellId = None
while True:

# updating the session so we can keep track of the games phase
    # response =  requests.get(url=f'https://127.0.0.1:{port}/lol-gameflow/v1/gameflow-phase',auth=auth,data={},verify=False)
    response = req(type='GET',link='/lol-gameflow/v1/gameflow-phase')
    status = response.json()
    print(status)
    
# while the matchmaking phase to auto press ready
    if status == 'ReadyCheck':
        response = req(type='POST',link='/lol-matchmaking/v1/ready-check/accept')
        # response =  requests.post(url=f'https://127.0.0.1:{port}/lol-matchmaking/v1/ready-check/accept',auth=auth,data={},verify=False)
        print(f'accept:{response.status_code}')
        banId,pickId,cellId,banLock,pickLock = None, None, None, None, None
        # time.sleep(6)

# just entered the champselect phase as u still didnt get ur ids
    elif status == 'ChampSelect' and (len(banList) or len(pickList)):
        response = req(type='GET',link='/lol-champ-select/v1/session')
        champ_select_props = response.json()
        # print(champ_select_props)
        if not cellId:     
            cellId, banId, pickId, banIndex, pickIndex = extractid(champ_select_props)
            select(actorId=pickId,champ=pickList[0])
        if champ_select_props.get('actions')[0][banIndex].get('isInProgress') and len(banList) and not banLock:
            # ban a champ
            print('u r in ban phase')
            banLock = pick(actorId=banId,pick_list=banList)
            if banLock:
                select(actorId=pickId,champ=pickList[0])
        elif champ_select_props.get('actions')[pickIndex[0]][pickIndex[1]].get('isInProgress') and len(pickList) and not pickLock:
            # pick a champ
            print('u r in pick phase')
            pickLock = pick(actorId=pickId,pick_list=pickList)
            print()
        # else:
        #     select(actorId=pickId,champ=pickList[0])
        # time.sleep(6)
    elif status == 'InProgress':
        sys.exit()

    time.sleep(6)

# in champ select after we invoked the ids
    # elif banId is not None:
    #     response =  requests.post(url=f'https://127.0.0.1:{port}/lol-champ-select/v1/session/actions/18/complete',auth=auth,json= {'championId': 142},verify=False)
    #     print(response.json())
    #     time.sleep(4)
        # response =  requests.post(url=f'https://127.0.0.1:{port}/lol-champ-select/v1/session/actions/{22}/complete',auth=auth,data={},verify=False)
        # print(response.status_code)
        # time.sleep(2)


    # response =  requests.get(url=f'https://127.0.0.1:{port}/lol-gameflow/v1/gameflow-phase',auth=auth,data={},verify=False)
    # x = response.json()
    # print(x)
    # time.sleep(1)

# /lol-gameflow/v1/gameflow-phase  :get
# /lol-champ-select/v1/session/actions/{id}    :patch
# /lol-champ-select/v1/session/actions/{id}/complete   : post
# https://www.mingweisamuel.com/lcu-schema/tool/#/
# plugin lol-matchmaking
# /lol-matchmaking/v1/ready-check/accept

# Lobby : if u didnt start finding a match
# Matchmaking
# ReadyCheck
# ChampSelect


# status_code 500 for ban failure