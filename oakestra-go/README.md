# oakestra-go

A Go client library for the [Oakestra](https://oakestra.io) System Manager API, in the
style of [`google/go-github`](https://github.com/google/go-github): a `Client` with one
service per resource, `context.Context`-first methods, functional options, and typed
errors.

This library is config-agnostic - it never reads files or environment variables. The
caller supplies a base URL and credentials. The [Oakestra CLI](../oak_cli) is built on
top of it and is a good reference for a real consumer.

## Install

```sh
go get github.com/oakestra/oakestra-cli/oakestra-go
```

## Usage

```go
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/oakestra/oakestra-cli/oakestra-go"
)

func main() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
		oakestra.WithBasicLogin("Admin", "Admin"),
	)
	if err != nil {
		log.Fatal(err)
	}

	apps, _, err := client.Applications.List(context.Background())
	if err != nil {
		log.Fatal(err)
	}
	for _, app := range apps {
		fmt.Println(app.ApplicationName, app.ApplicationID)
	}
}
```

## Examples

There are a few small programs under [`examples/`](examples):

- [`list-apps`](examples/list-apps) lists your applications
- [`deploy-app`](examples/deploy-app) creates apps from an SLA file, deploys their
  services and waits until they're running
- [`inspect-service`](examples/inspect-service) looks up a service by name or ID and
  shows its instances
- [`cluster-status`](examples/cluster-status) prints CPU and memory usage per cluster

They all take `-host`, `-username` and `-password` (default `127.0.0.1`, `Admin`,
`Admin`). Run them from this directory:

```sh
go run ./examples/list-apps -host 192.168.1.10
go run ./examples/deploy-app -sla ../oak_cli/SLAs/edge_gaming.json
go run ./examples/inspect-service nginx
go run ./examples/cluster-status -all
```

For shorter snippets per method, see [`example_test.go`](example_test.go). Those also
show up on [pkg.go.dev](https://pkg.go.dev/github.com/oakestra/oakestra-cli/oakestra-go).

## Authentication

- `WithBasicLogin(username, password)` - logs in against `/api/auth/login` and caches
  the token (matching the Oakestra CLI's behaviour). Cache lifetime defaults to
  `DefaultTokenTTL` and can be overridden with `WithTokenTTL`.
- `WithToken(token)` - skips the login flow for a token you already hold.
- `WithAuth(provider)` - plug in any `AuthProvider` for custom schemes (OIDC, a token
  sourced from a file you manage, etc.).

## Errors

Failed calls return one of:

- `*oakestra.ErrorResponse` - a non-2xx response that isn't an auth failure
- `*oakestra.AuthError` - login rejected, or a request failed with 401/403
- `*oakestra.ConnectionError` - the base URL was unreachable (wraps the network error)
- `*oakestra.NotFoundError` / `*oakestra.MultipleMatchesError` - from the `ResolveByNameOrID`
  / `FindByNameOrID` helpers

Use `errors.As` to react to a specific case.

## Endpoints without a typed method

`Client.NewRequest` and `Client.Do` are exported, so you can reach any System Manager
endpoint this package doesn't wrap yet while still getting request signing, JSON
decoding (including Oakestra's occasional JSON-encoded-string bodies), and error
translation for free.

## Scope

v0.1 covers authentication, applications, services, and clusters - the System Manager
surface the Oakestra CLI uses today. Cluster-manager endpoints (port 10100), addon APIs
(e.g. FLOps), retries, and pagination are not covered; use the escape hatch above until
there's a typed method for them.

## References

- [pkg.go.dev](https://pkg.go.dev/github.com/oakestra/oakestra-cli/oakestra-go)
- [Oakestra docs](https://www.oakestra.io/docs/)
- [SLA format](https://www.oakestra.io/docs/reference/app-sla/) (what `Applications.Create` takes)
- [System Manager API reference](https://www.oakestra.io/docs/reference/api/)
- [Sample SLAs](../oak_cli/SLAs)
- [`oak_cli/internal/api`](../oak_cli/internal/api/api.go) for how the CLI wires this up
  with its own config file
