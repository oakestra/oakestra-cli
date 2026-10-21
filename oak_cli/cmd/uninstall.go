package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var uninstallSudo bool

// ─── top-level uninstall command ──────────────────────────────────────────────

var uninstallCmd = &cobra.Command{
	Use:   "uninstall <root|cluster|worker|cleanup>",
	Short: "Uninstall Oakestra components from this machine",
	RunE:  func(cmd *cobra.Command, args []string) error { return cmd.Help() },
}

func init() {
	uninstallCmd.AddCommand(uninstallRootCmd)
	uninstallCmd.AddCommand(uninstallClusterCmd)
	uninstallCmd.AddCommand(uninstallWorkerCmd)
	uninstallCmd.AddCommand(uninstallCleanupCmd)

	// --root is inherited by all uninstall subcommands.
	uninstallCmd.PersistentFlags().BoolVar(&uninstallSudo, "root", false,
		"Run docker compose commands with sudo")
}

// ─── uninstall root ───────────────────────────────────────────────────────────

var uninstallRootCmd = &cobra.Command{
	Use:   "root",
	Short: "Stop and remove the root orchestrator",
	RunE: func(cmd *cobra.Command, args []string) error {
		yml, err := findDoctorComposeYML("root")
		if err != nil {
			return err
		}
		fmt.Println("Stopping root orchestrator…")
		return shellRun(uninstallSudo, "docker compose -f "+yml+" down")
	},
}

// ─── uninstall cluster ────────────────────────────────────────────────────────

var uninstallClusterCmd = &cobra.Command{
	Use:   "cluster",
	Short: "Stop and remove the cluster orchestrator",
	RunE: func(cmd *cobra.Command, args []string) error {
		yml, err := findDoctorComposeYML("cluster")
		if err != nil {
			return err
		}
		fmt.Println("Stopping cluster orchestrator…")
		return shellRun(uninstallSudo, "docker compose -f "+yml+" down")
	},
}

// ─── uninstall worker ─────────────────────────────────────────────────────────

var uninstallWorkerCmd = &cobra.Command{
	Use:   "worker",
	Short: "Stop and remove the NodeEngine worker node",
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("Stopping NodeEngine…")
		// Stop the daemon first; ignore error if it wasn't running.
		_ = runInteractive("sudo", "NodeEngine", "stop")

		fmt.Println("Removing NodeEngine binaries…")
		errs := 0
		for _, bin := range []string{"/usr/bin/NodeEngine", "/usr/bin/nodeengined", "/usr/bin/NetManager"} {
			if err := runInteractive("sudo", "rm", "-f", bin); err != nil {
				fmt.Printf("  warning: could not remove %s: %v\n", bin, err)
				errs++
			}
		}
		if errs == 0 {
			fmt.Println(green("✓ Worker node uninstalled."))
		}
		return nil
	},
}

// ─── uninstall cleanup ────────────────────────────────────────────────────────

var uninstallCleanupCmd = &cobra.Command{
	Use:   "cleanup",
	Short: "Bruteforce removal of all Oakestra containers, volumes, images, and worker binaries",
	Long: `Remove all Oakestra artifacts from this machine:
  - All containers matching Oakestra service name patterns
  - All Docker volumes whose names start with cluster_orchestrator, oakestra_, or root_orchestrator
  - All Docker images on this machine
  - NodeEngine and NetManager binaries (via oak uninstall worker)

Each Docker command is attempted without sudo first; if it fails, it is retried with sudo.
All errors are ignored — this is a best-effort cleanup.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println(bold("Removing Oakestra containers…"))
		tryBestEffort(
			`docker ps -a --format "{{.Names}}"` +
				` | grep -E "system_manager|mongo|root_|cluster_|jwt_|grafana|loki|promtail|mqtt|addons|marketplace|oakestra"` +
				` | xargs -r docker rm -f`,
		)

		fmt.Println(bold("Removing Oakestra volumes…"))
		tryBestEffort(
			`docker volume ls --format "{{.Name}}"` +
				` | grep -E "^(cluster_orchestrator|oakestra_|root_orchestrator)"` +
				` | xargs -r docker volume rm`,
		)

		fmt.Println(bold("Removing all Docker images…"))
		tryBestEffort(`docker image rm -f $(docker image ls -q)`)

		fmt.Println(bold("Removing worker node…"))
		_ = uninstallWorkerCmd.RunE(cmd, args)

		fmt.Printf("\n%s Cleanup complete.\n", green("✓"))
		return nil
	},
}

// tryBestEffort runs a shell command without sudo; on failure it retries with sudo.
// All errors are silently ignored.
func tryBestEffort(command string) {
	if runInteractive("sh", "-c", command) != nil {
		_ = runInteractive("sudo", "sh", "-c", command)
	}
}
