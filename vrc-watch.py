from ast import arg
import re
import requests
import argparse


def get_friends(api_key, auth_token):

    headers = {
        "accept": "application/json",
        "cookie": f"apiKey={api_key}; auth={auth_token}; "
    }

    resp = requests.get("https://vrchat.com/api/1/auth/user/friends", params={"offline": "false", "n": 50, "offset": 0}, headers=headers)
    print(resp.content)
    return resp.json()




def main():
    parser = argparse.ArgumentParser("Attempts to watch the VRC friends API for updates")
    parser.add_argument('-a', help='API Key retrieved from website session cookies', required=True, type=str, dest='api_key')
    parser.add_argument('-A', help='API auth token retrieved from website session cookies', required=True, type=str, dest='auth_token') 
    parser.add_argument('-w', help='Discord webhook URL for sharing updates', required=False, type=str, default=None, dest='webhook')

    args = parser.parse_args()

    friends = get_friends(args.api_key, args.auth_token)
    print(friends)


if __name__ == "__main__":
    main()