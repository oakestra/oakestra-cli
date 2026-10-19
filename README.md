[![Go check](https://github.com/oakestra/oakestra-cli/actions/workflows/go_check.yml/badge.svg)](https://github.com/oakestra/oakestra-cli/actions/workflows/go_check.yml)

The **Oak-CLI** is the command line interface for the [Oakestra](https://github.com/oakestra/oakestra) Edge Computing platform.

📚 Check out the [Oak-CLI Wiki](https://www.oakestra.io/docs/getting-started/deploy-app/with-the-cli/) to get started.

---

## Overview

The CLI is a single self-contained binary with no runtime dependencies. It runs on Linux, macOS, and Windows.

### Install latest release

**Linux / macOS**

```sh
curl -sSL https://raw.githubusercontent.com/oakestra/oakestra-cli/refs/heads/master/oak_cli/install.sh | bash
```

The script auto-detects your OS and architecture (amd64 / arm64), downloads the latest release binary, installs it to `/usr/local/bin/oak`, and registers shell completions for bash and zsh.

**Windows (PowerShell)**

```powershell
irm https://raw.githubusercontent.com/oakestra/oakestra-cli/master/oak_cli/install.ps1 | iex
```

This downloads the latest `oak_cli_windows_amd64.zip`, extracts `oak.exe`, and places it in `$Env:LOCALAPPDATA\Programs\oak\`, adding that directory to your `PATH`.

### Shell completions

Completions are set up automatically by the install script. To enable them manually:

```bash
# zsh - add to ~/.zshrc if not already present
echo 'eval "$(oak completion zsh)"' >> ~/.zshrc && source ~/.zshrc

# bash
echo 'eval "$(oak completion bash)"' >> ~/.bashrc && source ~/.bashrc

# fish
oak completion fish > ~/.config/fish/completions/oak.fish
```

### Build and install from source

Requires **Go 1.25+**.

```bash
# Clone the repository
git clone https://github.com/oakestra/oakestra-cli.git
cd oakestra-cli/oak_cli

# Run tests
go test ./...

# Build
go build -o oak .

# Install to $GOPATH/bin (must be on your PATH)
go install .
```

### Check the Documentation 
check `oak_cli/docs`

### Generate or update the documentation
Run
```
go run -tags docs . ./docs
```

### Quick start

```bash
# Point the CLI at your Oakestra root orchestrator
oak config set system_manager_ip <IP>

# Optional: set non-default credentials (default: Admin / Admin)
oak config credentials

# List applications
oak app show

# Create an application from an SLA file
oak app create my_app.json

# List services
oak service show

# Deploy a service instance
oak service deploy <service-id-or-name>

# Scale a service
oak service scale up <service-id-or-name> 3

# Inspect instances
oak service inspect <service-id-or-name>
```

Run `oak --help` or `oak <command> --help` for the full command reference.

