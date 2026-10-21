// Command deploy-app creates the applications described in an SLA file,
// deploys one instance of every service they contain, and waits until each
// of those instances reports RUNNING.
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/oakestra/oakestra-cli/oakestra-go"
)

func main() {
	host := flag.String("host", "127.0.0.1", "Oakestra System Manager host")
	username := flag.String("username", "Admin", "login username")
	password := flag.String("password", "Admin", "login password")
	slaPath := flag.String("sla", "../oak_cli/SLAs/default_app_with_services.json", "path to the SLA file")
	timeout := flag.Duration("timeout", 5*time.Minute, "how long to wait for every instance to be running")
	flag.Parse()

	raw, err := os.ReadFile(*slaPath)
	if err != nil {
		log.Fatalf("reading SLA: %v", err)
	}
	wanted, err := appNames(raw)
	if err != nil {
		log.Fatalf("parsing SLA: %v", err)
	}

	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost(*host)),
		oakestra.WithBasicLogin(*username, *password),
	)
	if err != nil {
		log.Fatalf("creating client: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), *timeout)
	defer cancel()

	all, _, err := client.Applications.Create(ctx, json.RawMessage(raw))
	if err != nil {
		log.Fatalf("creating applications: %v", err)
	}

	// Create answers with every application the user owns, so pick out the
	// ones this SLA declared. Matching by name is what the oak CLI does too,
	// since the SLA has no IDs yet at this point.
	var serviceIDs []string
	for _, app := range all {
		if wanted[app.ApplicationName] {
			fmt.Printf("created %s (%s)\n", app.ApplicationName, app.ApplicationID)
			serviceIDs = append(serviceIDs, app.Microservices...)
		}
	}
	if len(serviceIDs) == 0 {
		log.Fatal("no services to deploy")
	}

	for _, id := range serviceIDs {
		if _, err := client.Services.DeployInstance(ctx, id); err != nil {
			log.Fatalf("deploying %s: %v", id, err)
		}
	}

	for _, id := range serviceIDs {
		svc, err := waitRunning(ctx, client, id)
		if err != nil {
			log.Fatalf("waiting for %s: %v", id, err)
		}
		inst := svc.InstanceList[0]
		fmt.Printf("%s running on %s (cluster %s)\n", svc.MicroserviceName, inst.PublicIP, inst.ClusterID)
	}
}

// appNames returns the application names declared in an SLA document.
func appNames(sla []byte) (map[string]bool, error) {
	var doc struct {
		Applications []struct {
			Name string `json:"application_name"`
		} `json:"applications"`
	}
	if err := json.Unmarshal(sla, &doc); err != nil {
		return nil, err
	}
	names := make(map[string]bool, len(doc.Applications))
	for _, a := range doc.Applications {
		names[a.Name] = true
	}
	return names, nil
}

// waitRunning polls a service until at least one of its instances is
// running, or ctx is done. Deploying is asynchronous: DeployInstance returns
// as soon as the System Manager has accepted the request, long before a
// worker has pulled the image.
func waitRunning(ctx context.Context, client *oakestra.Client, serviceID string) (*oakestra.Service, error) {
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()
	for {
		svc, _, err := client.Services.Get(ctx, serviceID)
		if err != nil {
			return nil, err
		}
		for _, inst := range svc.InstanceList {
			// Older Oakestra versions report the status in lowercase.
			if strings.EqualFold(inst.Status, "RUNNING") {
				return svc, nil
			}
		}
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case <-ticker.C:
		}
	}
}
