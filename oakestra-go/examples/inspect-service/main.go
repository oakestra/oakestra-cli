// Command inspect-service looks up a service by name or ID and prints where
// each of its instances is running.
package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/oakestra/oakestra-cli/oakestra-go"
)

func main() {
	host := flag.String("host", "127.0.0.1", "Oakestra System Manager host")
	username := flag.String("username", "Admin", "login username")
	password := flag.String("password", "Admin", "login password")
	flag.Usage = func() {
		_, _ = fmt.Fprintf(flag.CommandLine.Output(), "usage: %s [flags] <service-name-or-id>\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()
	if flag.NArg() != 1 {
		flag.Usage()
		os.Exit(2)
	}

	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost(*host)),
		oakestra.WithBasicLogin(*username, *password),
	)
	if err != nil {
		log.Fatalf("creating client: %v", err)
	}

	svc, _, err := client.Services.ResolveByNameOrID(context.Background(), flag.Arg(0))
	var ambiguous *oakestra.MultipleMatchesError
	var notFound *oakestra.NotFoundError
	switch {
	case errors.As(err, &ambiguous):
		fmt.Fprintf(os.Stderr, "%q matches several services, pass one of these IDs instead:\n", ambiguous.Query)
		for _, m := range ambiguous.Matches {
			fmt.Fprintf(os.Stderr, "  %s  (app %s)\n", m.ID, m.Detail)
		}
		os.Exit(1)
	case errors.As(err, &notFound):
		log.Fatalf("no service called %q", notFound.Query)
	case err != nil:
		log.Fatalf("looking up service: %v", err)
	}

	fmt.Printf("%s.%s (%s)\n", svc.GetApplicationName(), svc.MicroserviceName, svc.MicroserviceID)
	fmt.Printf("  image:  %s\n", svc.Code)
	fmt.Printf("  status: %s\n", svc.Status)
	if len(svc.InstanceList) == 0 {
		fmt.Println("  no instances deployed")
		return
	}
	for _, inst := range svc.InstanceList {
		fmt.Printf("  #%d %-10s worker %s in cluster %s, cpu %s%%, mem %s%%\n",
			inst.InstanceNumber, inst.Status, inst.WorkerID, inst.ClusterID, inst.CPUPercent, inst.MemoryPercent)
	}
}
