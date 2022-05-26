# Oakestra CLI

> NM: Rename system commands to Oakestra

**oakestra-cli** is a very basic command line tool for controlling the EdgeIO framework.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) and the .whl file in the dist directory to install
edgeiocli.

```bash
pip install edgeiocli-0.1.0-py3-none-any.whl
```

## Build

Use the package [poetry](https://python-poetry.org/) to build the tool and create a new .whl file.

Updates the dependency's: 
```bash
poetry update
```

Installs the package:
```bash
poetry install
```

Creates the .whl file:
```bash
poetry build
```

## Usage

```bash
edgeiocli COMMAND [ARGS] [OPTIONS] 

# Try 'edgeiocli --help' for help.
```

## Available Commands

- `login [USERNAME]` logs the user into the system and creates access token
- `logout` logs out the user and deletes the token
- `change-password` changes the password of the user
- `application [COMMAND]`
    - `create` creates a new application
    - `delete [APPLICATION_ID]` deletes a application
    - `list-jobs [APPLICATION_ID]` displays all jobs in the application
    - `list` displays all applications of the user
- `service [COMMAND]`
    - `delete [SERVICE_ID]` deletes the job
    - `create [PATH]` creates a new service
    - `deploy [SERVICE_ID]` tries to deploy a service
- `user  [COMMAND]`
    - `create --role [Admin | Application_Provider | Infrastructure_Provider]` creates a new user
    - `delete [USERNAME] deletes the user`
    - `list` displays all user of the system
    - `set-roles [USERNAME] --role [Admin | Application_Provider | Infrastructure_Provider]`

## Deployment
The given json file should contain only a microservice configuration, as in the example, all the application and user information will be added automatically.  

```
{
      ...
      "microservice_name": "service",
      "microservice_namespace": "dev",
      "virtualization": "docker",
      "memory": 100,
      ...
}

```

## Contributing

This is the first version of **oakestra-cli** and does not yet offer all features, also there
might be some bugs, if you find one please report it or fix it. 

To add a new command create a function in the main.py file and add the `@app.command()` annotation to the function. If you want to create sub commands, create the command in the corresponding file. 
