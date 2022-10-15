import requests
import argparse
from time import sleep
import dateutil.parser


class VRC:
    def __init__(self, api_key, auth_token):
        self.headers = {
            "accept": "application/json",
            "cookie": f"apiKey={api_key}; auth={auth_token}; ",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0'
        }

    def get_current_user(self):
        return requests.get("https://vrchat.com/api/1/auth/user", headers=self.headers).json()


    def get_friends(self, offline=False, page=0, size=50):
        offset = page * size

        return requests.get("https://vrchat.com/api/1/auth/user/friends", params={"offline": "false", "n": size, "offset": offset}, headers=self.headers).json()

status_map = {
    'private': ':red_circle:',
    'ask me': ':orange_circle:',
    'active': ':green_circle:',
    'join me': ':blue_circle:'
}

status_colour = {
    'online': 0x00AA00,
    'active': 0x113311,
    'offline': 0xAA0000
}

def build_embed(friend, active):
    colour =  status_colour[friend['status_type']]
    
    if friend['status_type'] == 'active':
        present = ':desktop:'
    elif friend['status_type'] == 'offline':
        present = ":black_circle:"
    elif friend['status'] in status_map:
        present = status_map[friend['status']]
    else:
        present = friend['status']
    
    location = friend['location']
    if 'nonce' in location:
        parts = location.split(':')
        location = f"https://vrchat.com/home/launch?worldId={parts[0]}&instanceId={parts[1]}"
    elif friend['status_type'] == 'active':
        location = 'website'

    thumbnail = None if friend['currentAvatarImageUrl'] == '' else f"{friend['currentAvatarImageUrl']}"

    return {
        "title": f"{friend['displayName']}",
        "description": friend['bio'] if 'bio' in friend else "No bio",
        "url": f"https://vrchat.com/home/user/{friend['id']}",
        "color": colour,
        "thumbnail": {
            "url": thumbnail
        },
        "fields": [
            { "name": "Status", "value": present, 'inline': True},
            { "name": "Status Text", "value": friend['statusDescription'] if len(friend['statusDescription']) > 0 else '<none>', 'inline': True},
            { "name": "Location", "value": location},
            { "name": "Last Login", "value": f"<t:{int(dateutil.parser.isoparse(friend['last_login']).timestamp())}:f>" }
        ]
    }

def ping_discord(url, embeds):
    index = 0
    page_size = 10
    while len(embeds[index: index+page_size]) > 0:
        payload = {
            "username": "VRC Status",
            "embeds": embeds[index: index+10]
        }
        # print(embeds)
        print(requests.post(url, json=payload).content)
        index = index + page_size
        


known_friends = {}

def main():
    parser = argparse.ArgumentParser("Attempts to watch the VRC friends API for updates")
    parser.add_argument('-a', help='API Key retrieved from website session cookies', required=True, type=str, dest='api_key')
    parser.add_argument('-A', help='API auth token retrieved from website session cookies', required=True, type=str, dest='auth_token') 
    parser.add_argument('-w', help='Don\'t exit after first run, keep checking every 1 minute only producing changes between runs', required=False, default=False, action='store_true', dest='watch') 
    parser.add_argument('-D', help='Discord webhook URL for sharing updates', required=False, type=str, default=None, dest='webhook')

    args = parser.parse_args()

    vrc = VRC(args.api_key, args.auth_token)

    while True:
        current_user = vrc.get_current_user()
        active_friends = current_user['activeFriends']
        online_friends = current_user['onlineFriends']
        offline_friends = current_user['offlineFriends']
        
        embeds = []

        friends = vrc.get_friends()
        for f in friends:
            f['status_type'] = 'offline'
            if f['id'] in online_friends:
                f['status_type'] = 'online'
            elif f['id'] in active_friends:
                f['status_type'] = 'active'
            
            if f['id'] not in known_friends or (known_friends[f['id']]['status_type'] != f['status_type']):
                embeds.append(build_embed(f, True))

            known_friends[f['id']] = f                

        known_friends_online = [k for k in known_friends.keys()]
        for friendKey in known_friends_online:
            if friendKey in offline_friends:
                friend = known_friends.pop(friendKey)
                friend['status_type'] = 'offline'
                print(f"User went offline: {friend['username']}")
                embeds.append(build_embed(friend, False))
        
        if args.webhook is not None and len(embeds) > 0:
            ping_discord(args.webhook, embeds)

        if not args.watch:
            break
        else:
            sleep(60)
                
                


if __name__ == "__main__":
    main()