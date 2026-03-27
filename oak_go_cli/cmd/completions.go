package cmd

import (
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/spf13/cobra"

	"github.com/oakestra/oak-go-cli/internal/api"
	"github.com/oakestra/oak-go-cli/internal/config"
)

// completeApplications returns shell completions for application names and IDs.
// Each entry is formatted as "value\tdescription" so the shell shows context.
func completeApplications(_ *cobra.Command, _ []string, _ string) ([]string, cobra.ShellCompDirective) {
	client, err := api.New()
	if err != nil {
		return nil, cobra.ShellCompDirectiveNoFileComp
	}
	apps, err := client.GetApplications()
	if err != nil {
		return nil, cobra.ShellCompDirectiveNoFileComp
	}
	var out []string
	for _, a := range apps {
		out = append(out,
			fmt.Sprintf("%s\t%s | %s", a.ApplicationName, a.ApplicationNamespace, a.ApplicationID),
			fmt.Sprintf("%s\t%s | %s", a.ApplicationID, a.ApplicationName, a.ApplicationNamespace),
		)
	}
	return out, cobra.ShellCompDirectiveNoFileComp
}

// completeServices returns shell completions for service names and IDs.
func completeServices(_ *cobra.Command, _ []string, _ string) ([]string, cobra.ShellCompDirective) {
	client, err := api.New()
	if err != nil {
		return nil, cobra.ShellCompDirectiveNoFileComp
	}
	svcs, err := client.GetAllServices("")
	if err != nil {
		return nil, cobra.ShellCompDirectiveNoFileComp
	}
	var out []string
	for _, s := range svcs {
		appName := s.GetApplicationName()
		out = append(out,
			fmt.Sprintf("%s\t%s | %s", s.MicroserviceName, appName, s.MicroserviceID),
			fmt.Sprintf("%s\t%s | %s", s.MicroserviceID, s.MicroserviceName, appName),
		)
	}
	return out, cobra.ShellCompDirectiveNoFileComp
}

// completeServiceThenInstances completes the first arg as a service name/ID and
// the second arg as an instance number of that service.
func completeServiceThenInstances(_ *cobra.Command, args []string, _ string) ([]string, cobra.ShellCompDirective) {
	if len(args) == 0 {
		return completeServices(nil, nil, "")
	}
	if len(args) == 1 {
		return instanceCompletions(args[0])
	}
	return nil, cobra.ShellCompDirectiveNoFileComp
}

// instanceCompletions fetches running instances for a given service arg.
func instanceCompletions(serviceArg string) ([]string, cobra.ShellCompDirective) {
	client, err := api.New()
	if err != nil {
		return nil, cobra.ShellCompDirectiveNoFileComp
	}
	svc, err := client.ResolveServiceID(serviceArg)
	if err != nil {
		return nil, cobra.ShellCompDirectiveNoFileComp
	}
	var out []string
	for _, inst := range svc.InstanceList {
		out = append(out, fmt.Sprintf("%s\t%s | %s",
			strconv.Itoa(inst.InstanceNumber), inst.Status, inst.HostIP))
	}
	return out, cobra.ShellCompDirectiveNoFileComp
}

// completeScale handles the three positional args of `oak s scale`:
//
//	arg 0 → "up" or "down"
//	arg 1 → service name / ID
//	arg 2 → count (no completion)
func completeScale(_ *cobra.Command, args []string, _ string) ([]string, cobra.ShellCompDirective) {
	switch len(args) {
	case 0:
		return []string{
			"up\tDeploy new instances",
			"down\tUndeploy existing instances",
		}, cobra.ShellCompDirectiveNoFileComp
	case 1:
		return completeServices(nil, nil, "")
	default:
		return nil, cobra.ShellCompDirectiveNoFileComp
	}
}

// completeSLAFiles returns SLA file names (without .json) from ~/oak_cli/SLAs/,
// and also enables file-completion so local .json files in the CWD are offered too.
func completeSLAFiles(_ *cobra.Command, _ []string, _ string) ([]string, cobra.ShellCompDirective) {
	slaDir := config.SLAFolder()
	entries, err := os.ReadDir(slaDir)
	if err != nil {
		return nil, cobra.ShellCompDirectiveDefault
	}
	var out []string
	for _, e := range entries {
		if !e.IsDir() && strings.HasSuffix(e.Name(), ".json") {
			name := strings.TrimSuffix(e.Name(), ".json")
			out = append(out, fmt.Sprintf("%s\t%s", name, slaDir))
		}
	}
	// ShellCompDirectiveDefault keeps file completion active for local paths.
	return out, cobra.ShellCompDirectiveDefault
}

// completeClusters returns shell completions for cluster names and IDs.
func completeClusters(_ *cobra.Command, _ []string, _ string) ([]string, cobra.ShellCompDirective) {
	client, err := api.New()
	if err != nil {
		return nil, cobra.ShellCompDirectiveNoFileComp
	}
	clusters, err := client.GetClusters(true)
	if err != nil {
		return nil, cobra.ShellCompDirectiveNoFileComp
	}
	var out []string
	for _, c := range clusters {
		out = append(out,
			fmt.Sprintf("%s\t%s", c.ClusterName, c.ClusterID),
			fmt.Sprintf("%s\t%s", c.ClusterID, c.ClusterName),
		)
	}
	return out, cobra.ShellCompDirectiveNoFileComp
}

// completeConfigKeys completes the first arg of `oak config set` with known key names.
func completeConfigKeys(_ *cobra.Command, args []string, _ string) ([]string, cobra.ShellCompDirective) {
	if len(args) == 0 {
		return []string{
			"system_manager_ip\tIP of the Oakestra root orchestrator",
			"root_orchestrator_address\tAlias for system_manager_ip",
			"cluster_manager_ip\tIP of the Cluster Orchestrator",
			"cluster_name\tName of the local cluster",
			"cluster_location\tLocation of the local cluster",
			"main_oak_repo_path\tPath to the main Oakestra repository",
			"flops_repo_path\tPath to the FLOps addon repository",
		}, cobra.ShellCompDirectiveNoFileComp
	}
	return nil, cobra.ShellCompDirectiveNoFileComp
}
