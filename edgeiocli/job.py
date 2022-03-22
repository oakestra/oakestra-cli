import json
import os
from pathlib import Path

import typer

from edgeiocli.token_helper import send_auth_del_request, \
    is_logged_in, send_auth_post_file_request, send_auth_get_request, get_user_id

app = typer.Typer()


@app.command()
def deploy(file: Path, application_id: str):
    if is_logged_in():

        response = send_auth_get_request("/frontend/application/" + application_id)
        app = json.loads(response.text)
        if response.status_code != 200:
            msg = typer.style("Application does not exist", fg=typer.colors.RED, bold=True)
            typer.echo(msg)
        else:
            f = open(file)
            data = json.load(f)
            data['applicationID'] = application_id

            sla = {
                "api_version": "v0.3.0",
                "customerID": get_user_id(),
                "applications": [
                    {
                        "applicationID": application_id,
                        "application_name": app['name'],
                        "application_namespace": app['namespace'],
                        "application_desc": app['description'],
                        "microservices": [data]
                    }]
            }
            with open('tmp.json', 'w') as outfile:
                json.dump(sla, outfile)
            files = {'file': open('tmp.json', 'rb')}
            resp = send_auth_post_file_request("/api/deploy", files)
            if resp.status_code == 200:
                msg = typer.style("Job registered successfully, trying to deploy it ", fg=typer.colors.GREEN,
                                  bold=True)
            else:
                msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
                print(resp.text)
            os.remove("tmp.json")
            typer.echo(msg)


@app.command()
def delete(id: str):
    if is_logged_in():
        resp = send_auth_del_request("/frontend/job/" + id)
        if resp.status_code == 200:
            msg = typer.style("Job deleted successful", fg=typer.colors.GREEN, bold=True)
        else:
            msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
            print(resp.text)
        typer.echo(msg)
