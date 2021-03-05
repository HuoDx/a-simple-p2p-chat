from snuf_release.snuf import SNUF
from snuf_release.utils.networking import send_dict

from event_distributor import EventDistributor
# build configuration
user_config = {
    'username': None, # must be unique
    'nickname': None, # a displayed nickname
}
from uuid import uuid4

user_config['username'] = str(uuid4())

address_booth = {}
username_nickname_booth = {}

server = SNUF()
distributor = EventDistributor()

import socket
self_ip = socket.gethostbyname(socket.gethostname())
print('self ip is: %s' %self_ip)

def scan_net():
    from progress.bar import Bar
    # scan for 256 * 256 = 65536 ip addresses before any peer is found.
    
    counter = 0
    ip_frontpart = '.'.join(socket.gethostbyname(socket.gethostname()).split('.')[:2])
    print('Scanning your network to find peers.')
    while not peers_found and counter < 65536:
        D = counter % 256
        C = counter // 256
        ip = ip_frontpart + '.%s.%s'%(C,D)
        send_dict(ip, 5000, {
            'action': 'ack',
            'payload': {
                'username': user_config['username'],
                'nickname': user_config['nickname']
            }
        })
        counter += 1
        
    if not peers_found:
        print('Scanned; No peers found.')



def broadcast(datapacks: dict):
    global address_booth
    
    for address, username in address_booth.items():
        send_dict(address, 5000, datapacks)

peers_found = False

@distributor.on('sync-booths')
def on_sync_booths(payload: dict):
    global address_booth, username_nickname_booth, peers_found
    address_booth.update(payload.get('ip-booth', {}))
    username_nickname_booth.update(payload.get('username-booth', {}))
    lifespan = payload.get('lifespan', None)
    if lifespan is not None:
        payload['lifespan'] -= 1
    else:
        payload.update({'lifespan': -1})
    if lifespan > 0:
        message = {'action': 'sync-booths', 'payload': payload}
        broadcast(message)
        
    if self_ip != payload.get('from', ''):
        peers_found = True
    else:
        print('Working just fine: scanned yourself.')
    
@distributor.on('ack')
def on_ack(payload: dict):
    global address_booth, username_nickname_booth
    
    sender_ip = payload.get('from', '')
    sender_username = payload.get('username', 'unknown')
    sender_nickname = payload.get('nickname', 'Anonymous')
    address_booth.update({sender_ip: sender_username})
    username_nickname_booth.update({sender_username: sender_nickname})

    import pprint
    pprint.pprint(payload)
    
    
    # broadcast to the known network.
    broadcast({
        'action': 'sync-booths', 
        'payload': {
            'ip-booth': address_booth,
            'username-booth': username_nickname_booth,
            'lifespan': 4
            },
    })
    
chat_history = []
chats = []
@distributor.on('chat-msg')
def on_chat_msg(payload: dict):
    global chat_history, chats
    
    sender_ip = payload.get('from', '')
    username = address_booth.get(sender_ip, 'Unknown')
    nickname = username_nickname_booth.get(username, 'Anonymous')
    timestamp = payload.get('timestamp', '')
    chat_message = '[%s] %s'%(nickname, payload.get('msg', ''))
    if hash((username, timestamp, chat_message)) in chat_history:
        return None #ignore
    else:
        chats.append(chat_message)
        chat_history.append(hash((username, timestamp, chat_message)))
    refresh_chats()
import os
import sys
def refresh_chats():
    if sys.platform != 'win32':
        os.system('clear')
    else:
        os.system('cls')
    for msg in chats:
        print(msg)
    print('>_', end='\t')
    
@server.on_message
def process_message(msg):
    sender_ipv4 = msg.get('from', '')
    action:str = msg.get('action', None)
    payload:dict = msg.get('payload', {})
    if action is None:
        return None
    
    payload.update({'from': sender_ipv4})
    distributor.distrbute(action, payload)
    
if __name__ == '__main__':
    import time
    user_config['nickname']=input('Input your nickname: ')
    server.run()
    scan_net()
    msg = ''
    
    while True:
        refresh_chats()
        msg = input()
        if msg == '\\q':
            server.stop()
            break
        broadcast({
            'action': 'chat-msg',
            'payload': {
                'timestamp': time.time(),
                'msg': msg,
            }
        })
    exit()
        
    
    
