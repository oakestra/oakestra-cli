from pathlib import Path

import typer

from edgeiocli.token_helper import send_auth_del_request, \
    is_logged_in, send_auth_post_file_request

app = typer.Typer()


@app.command()
def deploy(file: Path):
    if is_logged_in():
        files = {'file': open(file, 'rb')}
        print(files.values())
        resp = send_auth_post_file_request("/api/deploy", files)
        if resp.status_code == 200:
            msg = typer.style("Job deleted successful", fg=typer.colors.GREEN, bold=True)
        else:
            msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
            print(resp.text)
        typer.echo(msg)
    # obj = {
    #     'name': name,
    #     'namespace': namespace,
    #     'description': description,
    #     'userId': get_user_id()
    # }
    # resp = send_auth_post_request("/frontend/application", obj)
    # if (resp.status_code == 200):
    #     msg = typer.style("Application created successful", fg=typer.colors.GREEN, bold=True)
    # else:
    #     msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
    #     print(resp.text)
    # typer.echo(msg)


@app.command()
def delete(id: str):
    if is_logged_in():
        resp = send_auth_del_request("/frontend/job/" + id)
        if (resp.status_code == 200):
            msg = typer.style("Job deleted successful", fg=typer.colors.GREEN, bold=True)
        else:
            msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
            print(resp.text)
        typer.echo(msg)
