import json
import os
from pathlib import Path

import typer

from edgeiocli.token_helper import send_auth_del_request, \
    is_logged_in, send_auth_get_request, get_user_id, send_auth_post_request

app = typer.Typer()


@app.command()
def create(file: Path, application_id: str):
    if is_logged_in():

        response = send_auth_get_request("/api/application/" + application_id)
        tmp = json.loads(response.text)
        app = json.loads(tmp)
        if response.status_code != 200:
            msg = typer.style("Application does not exist", fg=typer.colors.RED, bold=True)
            typer.echo(msg)
        else:
            f = open(file)
            data = json.load(f)
            data['applicationID'] = application_id

            sla = {
                "sla_version": "v2.0",
                "customerID": get_user_id(),
                "applications": [
                    {
                        "applicationID": application_id,
                        "application_name": app['application_name'],
                        "application_namespace": app['application_namespace'],
                        "application_desc": app['application_desc'],
                        "microservices": [data]
                    }]
            }
            resp = send_auth_post_request("/api/service/", sla)
            if resp.status_code == 200:
                msg = typer.style("Service created successfully", fg=typer.colors.GREEN,
                                  bold=True)
            else:
                msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
                print(resp.text)
            f.close()
            typer.echo(msg)


@app.command()
def delete(id: str):
    if is_logged_in():
        resp = send_auth_del_request("/api/service/" + id)
        if resp.status_code == 200:
            msg = typer.style("Job deleted successful", fg=typer.colors.GREEN, bold=True)
        else:
            msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
            print(resp.text)
        typer.echo(msg)


@app.command()
def deploy(id: str):
    if is_logged_in():
        resp = send_auth_get_request("/api/service/" + id)
        if resp.status_code == 200:
            service = json.loads(resp.text)
            deployresp = send_auth_post_request("/api/service/" + id + "/instance", service)
            if deployresp.status_code == 200:
                msg = typer.style("Service deployed successfully", fg=typer.colors.GREEN, bold=True)
            else:
                msg = typer.style("Error occured: " + deployresp.text, fg=typer.colors.RED, bold=True)
        else:
            msg = typer.style("Service with this id does not exist", fg=typer.colors.RED, bold=True)
        typer.echo(msg)
