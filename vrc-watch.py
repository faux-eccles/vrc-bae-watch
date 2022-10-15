import requests
import argparse
from time import sleep
import dateutil.parser

def get_friends(api_key, auth_token):

    headers = {
        "accept": "application/json",
        "cookie": f"apiKey={api_key}; auth={auth_token}; ",
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0'
    }

    resp = requests.get("https://vrchat.com/api/1/auth/user/friends", params={"offline": "false", "n": 50, "offset": 0}, headers=headers)
    return resp.json()

status_map = {
    'private': ':red_circle:',
    'ask me': ':orange_circle:',
    'active': ':green_circle:'
}

def build_embed(friend, online):
    status = "online" if online else "offline"
    colour = 0x00AA00 if online else 0xAA0000

    present = status_map[friend['status']] if friend['status'] in status_map else friend['status'] 

    location = friend['location']
    if 'nonce' in location:
        parts = location.split(':')
        location = f"https://vrchat.com/home/launch?worldId={parts[0]}&instanceId={parts[1]}"

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
            { "name": "Description", "value": friend['statusDescription'] if len(friend['statusDescription']) > 0 else '<none>', 'inline': True},
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
    parser.add_argument('-w', help='API auth token retrieved from website session cookies', required=False, default=False, action='store_true', dest='watch') 
    parser.add_argument('-D', help='Discord webhook URL for sharing updates', required=False, type=str, default=None, dest='webhook')

    args = parser.parse_args()

    while True:
        embeds = []

        friends = get_friends(args.api_key, args.auth_token)
        for f in friends:
            if f['friendKey'] not in known_friends:
                print(f"User online: {f['username']}")
                known_friends[f['friendKey']] = f
                if args.webhook is not None:
                    embeds.append(build_embed(f, True))

        online_friends = [f['friendKey'] for f in friends]
        known_friends_online = [k for k in known_friends.keys()]
        for friendKey in known_friends_online:
            if friendKey not in online_friends:
                friend = known_friends.pop(friendKey)
                print(f"User went offline: {friend['username']}")
                if args.webhook is not None:
                    embeds.append(build_embed(friend, False))
        
        if args.webhook is not None and len(embeds) > 0:
            ping_discord(args.webhook, embeds)

        if not args.watch:
            break
        else:
            sleep(60)
                
                


if __name__ == "__main__":
    main()