# [Oakestra CLI](https://github.com/oakestra/oakestra-cli)

**oakestra-cli** is a very basic command line tool for controlling your [Oakestra](https://github.com/oakestra/oakestra) setup. 

It is intended to be an interface for the API as well as a development tool.

The CLI supports command (tab) autocompletion.

## Usage
The package can be called via `oak`.

Currently, it supports the creation, deletion, inspection, and (un)deployment of applications and services.

E.g. To deploy a default application with two services:
```
oak applications create default_app_with_services --deploy
```
Note: The CLI supports short command aliases. The command above can be shortened like this:
```
oak a c default_app_with_services -d
```

You should see a similar output if the command was successful:
```bash
Success: Create new application based on 'default_app_with_services'
Success: Deploy a new instance for the service '66040243c7723114bb83b914'
Success: Deploy a new instance for the service '66040243c7723114bb83b919'
```
You can inspect the services like this:
```bash
oak services status
```
Or like this: `oak s s`

Service status output:
```yaml
All current services: '2'
 Service '0':
   - microservice -
   id: '66040243c7723114bb83b914'
   name: 'curl'
   ns: 'test'
   parent app: 'clientsrvr: 660402439df62d60bb95452b'
   - resources -
   memory: '100'
   vcpus: '1'
   - container -
   image: 'docker.io/curlimages/curl:7.82.0'
   - networking -
   port: '9080'
   - instances -
   instances: '1'
 Service '1':
   - microservice -
   id: '66040243c7723114bb83b919'
   name: 'nginx'
   ns: 'test'
   parent app: 'clientsrvr: 660402439df62d60bb95452b'
   - resources -
   memory: '100'
   vcpus: '1'
   - container -
   image: 'docker.io/library/nginx:latest'
   - networking -
   port: '6080:60/tcp'
   - instances -
   instances: '1'
```

For a more detailed explanation try out the CLI and use the `-h` flag.

## [Installation](https://pypi.org/project/oak-cli/)
```
pip install oak-cli
```

# For CLI Contributors/Developers
For local development with "hot-reload" functionality simply install the package via poetry.

## Useful commands

```bash
poetry install
```
```bash
poetry build
```
```
twine upload dist/*
```
