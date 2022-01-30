# EdgeIO CLI

**edgeiocli** is a simple command line tool for controlling the EdgeIO framework.

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
- `job [COMMAND]`
    - `delete [JOB_ID]` deletes the job
    - `deploy [PATH]` tries to deploy the file in EdgeIO
- `user  [COMMAND]`
    - `create --role [Admin | Application_Provider | Infrastructure_Provider]` creates a new user
    - `delete [USERNAME] deletes the user`
    - `list` displays all user of the system
    - `set-roles [USERNAME] --role [Admin | Application_Provider | Infrastructure_Provider]`

## Contributing

Pull requests are welcome. This is the first version of **edgeiocli** and does not yet offer all features, also there
might be some bugs, if you find one please report it 