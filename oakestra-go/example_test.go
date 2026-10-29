package oakestra_test

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	oakestra "github.com/oakestra/oakestra-cli/oakestra-go"
)

func Example() {
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
		fmt.Println(app.ApplicationName)
	}
}

// If you already have a token, WithToken skips the login request.
func ExampleWithToken() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL("http://10.0.0.5:10000"),
		oakestra.WithToken(os.Getenv("OAKESTRA_TOKEN")),
	)
	if err != nil {
		log.Fatal(err)
	}
	_ = client
}

// The default HTTP client times out after 30 seconds.
func ExampleWithHTTPClient() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
		oakestra.WithBasicLogin("Admin", "Admin"),
		oakestra.WithHTTPClient(&http.Client{Timeout: 2 * time.Minute}),
		oakestra.WithUserAgent("my-deploy-bot/1.0"),
	)
	if err != nil {
		log.Fatal(err)
	}
	_ = client
}

// envToken re-reads the token from the environment on every request, so a
// rotated token works without building a new client.
type envToken string

func (e envToken) Token(context.Context) (string, error) {
	t := os.Getenv(string(e))
	if t == "" {
		return "", fmt.Errorf("%s is not set", string(e))
	}
	return t, nil
}

func ExampleWithAuth() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
		oakestra.WithAuth(envToken("OAKESTRA_TOKEN")),
	)
	if err != nil {
		log.Fatal(err)
	}
	_ = client
}

func ExampleApplicationsService_Create() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
		oakestra.WithBasicLogin("Admin", "Admin"),
	)
	if err != nil {
		log.Fatal(err)
	}

	// Create accepts any JSON-marshallable SLA, so an SLA file can be passed
	// through untouched as a json.RawMessage.
	sla, err := os.ReadFile("default_app_with_services.json")
	if err != nil {
		log.Fatal(err)
	}

	// The System Manager answers with every application the user owns, not
	// just the ones created by this call.
	apps, _, err := client.Applications.Create(context.Background(), json.RawMessage(sla))
	if err != nil {
		log.Fatal(err)
	}
	for _, app := range apps {
		fmt.Println(app.ApplicationID, app.ApplicationName, len(app.Microservices))
	}
}

func ExampleApplicationsService_ResolveByNameOrID() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
		oakestra.WithBasicLogin("Admin", "Admin"),
	)
	if err != nil {
		log.Fatal(err)
	}
	ctx := context.Background()

	app, _, err := client.Applications.ResolveByNameOrID(ctx, "clientsrvr")
	if err != nil {
		log.Fatal(err)
	}
	if _, err := client.Applications.Delete(ctx, app.ApplicationID); err != nil {
		log.Fatal(err)
	}
}

func ExampleServicesService_List() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
		oakestra.WithBasicLogin("Admin", "Admin"),
	)
	if err != nil {
		log.Fatal(err)
	}

	// Pass nil to list every service, or narrow it down to one application.
	svcs, _, err := client.Services.List(context.Background(), &oakestra.ServiceListOptions{
		ApplicationID: "64f1c0ffee0123456789abcd",
	})
	if err != nil {
		log.Fatal(err)
	}
	for _, svc := range svcs {
		fmt.Printf("%s.%s: %d instance(s)\n", svc.GetApplicationName(), svc.MicroserviceName, len(svc.InstanceList))
	}
}

func ExampleServicesService_DeployInstance() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
		oakestra.WithBasicLogin("Admin", "Admin"),
	)
	if err != nil {
		log.Fatal(err)
	}
	ctx := context.Background()

	svc, _, err := client.Services.ResolveByNameOrID(ctx, "nginx")
	if err != nil {
		log.Fatal(err)
	}

	// Each call schedules one more instance; call it N times to scale up.
	for range 3 {
		if _, err := client.Services.DeployInstance(ctx, svc.MicroserviceID); err != nil {
			log.Fatal(err)
		}
	}
}

func ExampleServicesService_UndeployInstance() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
		oakestra.WithBasicLogin("Admin", "Admin"),
	)
	if err != nil {
		log.Fatal(err)
	}
	ctx := context.Background()

	svc, _, err := client.Services.Get(ctx, "64f1c0ffee0123456789abcd")
	if err != nil {
		log.Fatal(err)
	}
	for _, inst := range svc.InstanceList {
		if _, err := client.Services.UndeployInstance(ctx, svc.MicroserviceID, inst.InstanceNumber); err != nil {
			log.Fatal(err)
		}
	}
}

func ExampleClustersService_List() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
		oakestra.WithBasicLogin("Admin", "Admin"),
	)
	if err != nil {
		log.Fatal(err)
	}

	clusters, _, err := client.Clusters.List(context.Background(), &oakestra.ClusterListOptions{ActiveOnly: true})
	if err != nil {
		log.Fatal(err)
	}
	for _, c := range clusters {
		fmt.Printf("%s (%s): %d node(s), cpu %.0f%%, mem %.0f%%\n",
			c.ClusterName, c.ClusterLocation, c.ActiveNodes, c.CPUPercent, c.MemoryPercent)
	}
}

// Use errors.As to check which kind of error you got.
func Example_errorHandling() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
		oakestra.WithBasicLogin("Admin", "Admin"),
	)
	if err != nil {
		log.Fatal(err)
	}

	_, _, err = client.Services.ResolveByNameOrID(context.Background(), "nginx")

	var (
		connErr   *oakestra.ConnectionError
		authErr   *oakestra.AuthError
		notFound  *oakestra.NotFoundError
		ambiguous *oakestra.MultipleMatchesError
		apiErr    *oakestra.ErrorResponse
	)
	switch {
	case err == nil:
		fmt.Println("found it")
	case errors.As(err, &connErr):
		fmt.Println("System Manager unreachable at", connErr.BaseURL)
	case errors.As(err, &authErr):
		fmt.Println("credentials rejected, HTTP", authErr.StatusCode)
	case errors.As(err, &notFound):
		fmt.Println("no such", notFound.Kind)
	case errors.As(err, &ambiguous):
		for _, m := range ambiguous.Matches {
			fmt.Println("candidate:", m.ID, m.Detail)
		}
	case errors.As(err, &apiErr):
		fmt.Println("API error:", apiErr.StatusCode, apiErr.Body)
	default:
		log.Fatal(err)
	}
}

// For endpoints without a typed method, build the request yourself. Do still
// adds the token and decodes the response.
func ExampleClient_Do() {
	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost("127.0.0.1")),
		oakestra.WithBasicLogin("Admin", "Admin"),
	)
	if err != nil {
		log.Fatal(err)
	}
	ctx := context.Background()

	req, err := client.NewRequest(ctx, http.MethodGet, "api/clusters/", nil)
	if err != nil {
		log.Fatal(err)
	}
	var raw []map[string]any
	if _, err := client.Do(ctx, req, &raw); err != nil {
		log.Fatal(err)
	}
	fmt.Println(len(raw), "cluster(s)")
}
