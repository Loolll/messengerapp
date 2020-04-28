import requests
import json


def create_user_token(username: str, password: str, server: str):
    """ Sends POST request to server to create UserToken """

    url = '{server}/api/newtoken'.format(server=server) if 'http://' in server else \
        'http://{server}/api/newtoken'.format(server=server)

    response = requests.post(url, headers={'USERNAME': username, 'PASSWORD': password})
    if response.status_code == 200:
        dictionary = json.loads(response.content)
        if dictionary['Status'] == 'OK':
            return dictionary['Status'], dictionary['UserToken']
        else:
            return dictionary['Status'], ''

    return str(str(response.status_code) + ' Maybe you entered wrong username or password in settings.ini'), ''


def get_info(server: str):
    """ Sends GET request to server and returns time delete info (time about data cleaning) """
    url = '{server}/api/getinfo'.format(server=server) if 'http://' in server else \
        'http://{server}/api/getinfo'.format(server=server)

    response = requests.get(url)
    if response.status_code == 200:
        dictionary = json.loads(response.content)
        if dictionary['Status'] == "OK":
            return dictionary['Status'], dictionary['TimeToDeleteSeconds']
        else:
            return dictionary['Status'], -1

    return str(str(response.status_code) + 'Unexpected error'), -1
