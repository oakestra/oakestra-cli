import datetime
from typing import Optional, List

from tabulate import tabulate

from edgeiocli.token_helper import *

app = typer.Typer()


def role_callback(roles: Optional[List[str]]):
    for value in roles:
        value = value.lower()
        if value != "admin" and value != "application_provider" and value != "infrastructure_provider":
            raise typer.BadParameter("Only admin, application_provider or infrastructure_provider are allowed roles")
    return roles


@app.command()
def create(name=typer.Option(..., prompt="What's the name of the new user?"),
           email=typer.Option(..., prompt="Email address of the new user"),
           password=typer.Option(..., prompt="Create password"),
           role: Optional[List[str]] = typer.Option(..., callback=role_callback),
           ):
    if is_logged_in():
        d = datetime.datetime.now()
        user_roles = []

        for r in role:
            if r.lower() == 'admin':
                user_roles.append({'name': 'Admin', 'description': 'This is the admin role'})
            if r.lower() == 'application_provider':
                user_roles.append({'name': 'Application_Provider', 'description': 'This is the app role'})
            if r.lower() == 'infrastructure_provider':
                user_roles.append({'name': 'Infrastructure_Provider', 'description': 'This is the infra role'})

        obj = {
            'name': name,
            'email': email,
            'password': password,
            'roles': user_roles,
            'created_at': d.strftime("%d/%m/%Y %H:%M")
        }

        resp = send_auth_post_request("/frontend/auth/register", obj)
        if resp.status_code == 200:
            msg = typer.style("User added successfully", fg=typer.colors.GREEN, bold=True)
        else:
            msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
            print(resp.text)
        typer.echo(msg)


@app.command()
def delete(username: str,
           force: bool = typer.Option(..., prompt="Are you sure you want to delete the user?"), ):
    if is_logged_in():
        if force:
            resp = send_auth_del_request("/frontend/user/" + username)
            if resp.status_code == 200:
                msg = typer.style("User deleted successfully", fg=typer.colors.GREEN, bold=True)
            else:
                msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
                print(resp.text)
            typer.echo(msg)


@app.command()
def list():
    if is_logged_in():
        response = send_auth_get_request("/frontend/users")
        users = json.loads(response.text)
        table = []

        for u in users:
            r = []
            for roles in u['roles']:
                r.append(roles['name'])

            table.append([u['name'], (u['_id'])['$oid'], u['email'], r])
        print(tabulate(table, headers=['Name', 'ID', 'Email', 'Roles']))


@app.command()
def set_roles(username: str,
              role: Optional[List[str]] = typer.Option(..., callback=role_callback),
              ):
    if is_logged_in():
        user_roles = []

        for r in role:
            if r.lower() == 'admin':
                user_roles.append({'name': 'Admin', 'description': 'This is the admin role'})
            if r.lower() == 'application_provider':
                user_roles.append({'name': 'Application_Provider', 'description': 'This is the app role'})
            if r.lower() == 'infrastructure_provider':
                user_roles.append({'name': 'Infrastructure_Provider', 'description': 'This is the infra role'})

        obj = {
            'roles': user_roles,
        }

        resp = send_auth_put_request("/frontend/user/" + username, obj)
        if resp.status_code == 200:
            msg = typer.style("Roles changed successfully", fg=typer.colors.GREEN, bold=True)
        else:
            msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
            print(resp.text)
        typer.echo(msg)


if __name__ == "__main__":
    app()
