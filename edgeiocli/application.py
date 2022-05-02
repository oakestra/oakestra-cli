from tabulate import tabulate
from edgeiocli.token_helper import *

app = typer.Typer()


@app.command()
def create(name=typer.Option(..., prompt="What's the name of the application?"),
           namespace=typer.Option(..., prompt="What's the application namespace?"),
           description=typer.Option(..., prompt="Description of the application?")
           ):
    obj = {
        'name': name,
        'namespace': namespace,
        'description': description,
        'userId': get_user_id()
    }
    resp = send_auth_post_request("/api/application", obj)
    if resp.status_code == 200:
        msg = typer.style("Application created successful", fg=typer.colors.GREEN, bold=True)
    else:
        msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
        print(resp.text)
    typer.echo(msg)


@app.command()
def delete(id: str):
    if is_logged_in():
        resp = send_auth_del_request("/api/application/" + id)
        if resp.status_code == 200:
            msg = typer.style("Application deleted successful", fg=typer.colors.GREEN, bold=True)
        else:
            msg = typer.style("Error occurred", fg=typer.colors.RED, bold=True)
            print(resp.text)
        typer.echo(msg)


@app.command()
def list():
    if is_logged_in():
        response = send_auth_get_request("/api/applications/" + get_user_id())
        apps = json.loads(response.text)
        table = []
        for a in apps:
            table.append([a['name'], (a['_id'])['$oid']])
        print(tabulate(table, headers=['Name', 'ID']))


@app.command()
def list_jobs(application_id: str):
    if is_logged_in():
        response = send_auth_get_request("/api/services/" + application_id)
        apps = json.loads(response.text)
        table = []
        for a in apps:
            if 'usage' in a:
                usage = a['usage']
                table.append([a['job_name'], (a['_id'])['$oid'], a['status'], (usage['currentCPU'])[-1], (usage['currentMemory'])[-1]])
            else:
                table.append([a['job_name'], (a['_id'])['$oid'], a['status'], "-", "-"])
        print(tabulate(table, headers=['Name', 'ID', 'Status', 'CPU', 'Memory']))
