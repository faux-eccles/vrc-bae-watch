# vrc-bae-watch
Meme project to track VRC friend activity.  Effectively provides no real functionality over just using the website. 
* Only tracks if they're online
* Doesn't track status change or world changes 

![Screen shot of discord images display and online user, website active user, and offline user](/img/vrc-bae-watch-example-1.png)

## Disclaimer 
This program violates VRC TOS, and probably shouldn't be used with any account you value.
If you're going to run it, it's recommended to create a new throw away account, though there is no guarantee it'll protect your primary account.  
A separate account will also address privacy issues by effectively making it an opt in system.

## Running the app 
In order to call the API and query for freinds we needs to authenticate our requests, using the same auth methods used by the website, this means extracting `auth_token` and `api_key` values, which are required by the script

### Retrieving the auth requirements
1. Open developer tools in your browser, and log into the VRC website 
2. Search for the call to `/api/1/auth` 
3. In the response body the `token` value will be your `auth_token` 
4. In the response cookies search for the `apiKey` cookie this will be your `api_key`  

### Running the script directly
The script makes use of the argparse module so includes a `--help` flag to provide detailed argument definitions. 
-- --
Run the script continuously checking every minute for changes and posting updates to discord
```bash
python3 vrc-watch.py -a "<api_key>" -A "<auth_token>" -D "<discord webhoook url>" -w
```
-- --
To gather a onetime list online users
```bash 
python3 vrc-watch.py -a "<api_key>" -A "<auth_token>"
```
-- --