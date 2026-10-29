[![Go check](https://github.com/oakestra/oakestra-cli/actions/workflows/go_check.yml/badge.svg)](https://github.com/oakestra/oakestra-cli/actions/workflows/go_check.yml)

The **Oak-CLI** is the command line interface for the [Oakestra](https://github.com/oakestra/oakestra) Edge Computing platform.

📚 Check out the [Oak-CLI Wiki](https://www.oakestra.io/docs/getting-started/deploy-app/with-the-cli/) to get started.

The repo has two Go modules: the CLI itself in [`oak_cli/`](oak_cli), and the
[Go client library](#go-client-library) it's built on in [`oakestra-go/`](oakestra-go).

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

### Command reference

The full command reference is generated from the Cobra command tree and lives in
[`oak_cli/docs`](oak_cli/docs/oak.md). To regenerate it after changing a command, run
this from `oak_cli/`:

```bash
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

---

## Go client library

If you want to talk to Oakestra from Go code instead of shelling out to `oak`, use
[`oakestra-go`](oakestra-go). It's the same client the CLI uses.

```sh
go get github.com/oakestra/oakestra-cli/oakestra-go
```

```go
client, err := oakestra.NewClient(
	oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
	oakestra.WithBasicLogin("Admin", "Admin"),
)
if err != nil {
	log.Fatal(err)
}
apps, _, err := client.Applications.List(ctx)
```

More in the [library README](oakestra-go/README.md), the [examples](oakestra-go/examples)
and on [pkg.go.dev](https://pkg.go.dev/github.com/oakestra/oakestra-cli/oakestra-go).

The root [`go.work`](go.work) points the CLI at the local copy of the library, so you can
change both and build them together:

```bash
go build ./oak_cli/... ./oakestra-go/...
go test ./oak_cli/... ./oakestra-go/...
```

---

## References

- [Oakestra](https://github.com/oakestra/oakestra)
- [Oakestra docs](https://www.oakestra.io/docs/)
- [Deploying with the CLI](https://www.oakestra.io/docs/getting-started/deploy-app/with-the-cli/)
- [SLA format](https://www.oakestra.io/docs/reference/app-sla/) (used by `oak app create` and [`oak_cli/SLAs`](oak_cli/SLAs))
- [API reference](https://www.oakestra.io/docs/reference/api/)
