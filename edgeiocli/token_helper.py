import json
import os
from datetime import datetime

import jwt
import requests

# from edgeIoCLI import api_ip
import typer

api_ip = "http://127.0.0.1:10000"


def get_header():
    return {"Authorization": "Bearer " + get_raw_token()}


def send_auth_get_request(url):
    return requests.get(api_ip + url, headers=get_header())


def send_auth_post_request(url, data):
    return requests.post(api_ip + url, headers=get_header(), json=data)


def send_auth_post_file_request(url, file):
    return requests.post(api_ip + url, headers=get_header(), files=file)


def send_auth_put_request(url, data):
    return requests.put(api_ip + url, headers=get_header(), json=data)


def send_auth_del_request(url):
    return requests.delete(api_ip + url, headers=get_header())


def decode_token():
    token = get_raw_token()
    return jwt.decode(token, options={"verify_signature": False})


def get_raw_token():
    f = open('edgeio.json')
    data = json.load(f)
    return data['token']


def get_storage():
    f = open('edgeio.json')
    return json.load(f)


def get_username():
    return decode_token()['sub']


def delete_token():
    if token_exists():
        os.remove("edgeio.json")


# true if the user is logged in
def is_logged_in():
    val = False
    if token_exists():
        val = not isTokenExpired()

    if not val:
        msg = typer.style("You must be logged in to execute commands", fg=typer.colors.RED, bold=True)
        typer.echo(msg)
        return False
    return True


def token_exists():
    return os.path.exists("edgeio.json")


# stores the token in the file
def set_token(token):
    with open('edgeio.json', 'w') as outfile:
        json.dump(token, outfile)


# stores the token in the file
def set_user_id(id):
    obj = get_storage()
    obj['id'] = id
    with open('edgeio.json', 'w') as outfile:
        json.dump(obj, outfile)


def get_user_id():
    obj = get_storage()
    return obj['id']


def getTokenExpirationDate():
    decoded = decode_token()
    if decoded['exp'] == None:
        return None
    return datetime.fromtimestamp(decoded['exp'])


def isTokenExpired():
    d = getTokenExpirationDate();
    if d == None:
        return False
    # Token expired?
    return d < datetime.today()
