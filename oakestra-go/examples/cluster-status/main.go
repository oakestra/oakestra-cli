// Command cluster-status prints a utilisation table for the clusters
// attached to an Oakestra Root Orchestrator.
package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
	"text/tabwriter"

	"github.com/oakestra/oakestra-cli/oakestra-go"
)

func main() {
	host := flag.String("host", "127.0.0.1", "Oakestra System Manager host")
	username := flag.String("username", "Admin", "login username")
	password := flag.String("password", "Admin", "login password")
	all := flag.Bool("all", false, "include inactive clusters")
	flag.Parse()

	client, err := oakestra.NewClient(
		oakestra.WithBaseURL(oakestra.BaseURLForHost(*host)),
		oakestra.WithBasicLogin(*username, *password),
	)
	if err != nil {
		log.Fatalf("creating client: %v", err)
	}

	clusters, _, err := client.Clusters.List(context.Background(), &oakestra.ClusterListOptions{ActiveOnly: !*all})
	if err != nil {
		log.Fatalf("listing clusters: %v", err)
	}
	if len(clusters) == 0 {
		fmt.Println("no clusters found")
		return
	}

	w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	_, _ = fmt.Fprintln(w, "NAME\tADDRESS\tACTIVE\tNODES\tCPU\tMEMORY\tRUNTIMES")
	for _, c := range clusters {
		_, _ = fmt.Fprintf(w, "%s\t%s:%s\t%t\t%d\t%.0f%% of %d cores\t%.0f%% of %d MB\t%s\n",
			c.ClusterName, c.ClusterIP, c.Port, c.Active, c.ActiveNodes,
			c.CPUPercent, c.TotalCPUCores, c.MemoryPercent, c.MemoryInMB,
			strings.Join(c.Virtualization, ","))
	}
	_ = w.Flush()
}
