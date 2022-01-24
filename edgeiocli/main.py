import pyfiglet

import edgeiocli.job
from edgeiocli.token_helper import *

app = typer.Typer()
app.add_typer(edgeiocli.user.app, name="user")
app.add_typer(edgeiocli.job.app, name="job")
app.add_typer(edgeiocli.application.app, name="application")


@app.command()
def login(username: str,
          password: str = typer.Option(
              ..., prompt=True, hide_input=True)
          ):
    login_request = {
        'username': username,
        'password': password
    }
    response = requests.post(api_ip + "/frontend/auth/login", json=login_request)

    stud_obj = json.loads(response.text)
    set_token(stud_obj)

    if response.status_code == 200:

        res = send_auth_get_request("/frontend/user/" + username)
        user_obj = json.loads(res.text)
        id_obj = user_obj['_id']
        id = id_obj['$oid']
        set_user_id(id)

        f = pyfiglet.Figlet(font='slant')
        print(f.renderText('EdgeIO CLI !'))
        print(f"Hello {username} welcome to the EdgeIO CLI!")
        time = getTokenExpirationDate().strftime("%d/%m/%Y %H:%M")
        print("You are now logged in and can use the cli until your token expires (" + time + ")")
    else:
        print(response.text)


@app.command()
def logout():
    delete_token()
    print("Tokens are deleted, Goodbye")


@app.command()
def change_password(old=typer.Option(..., prompt="Old password: "),
                    new=typer.Option(..., prompt="New Password: ", confirmation_prompt=True),
                    ):
    obj = {
        'oldPassword': old,
        'newPassword': new
    }

    resp = send_auth_post_request("/frontend/changePassword/" + get_username(), obj)
    if resp.status_code == 200:
        msg = typer.style("Password changed successfully", fg=typer.colors.GREEN, bold=True)
    else:
        msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
        print(resp.text)
    typer.echo(msg)


if __name__ == '__main__':
    app()
