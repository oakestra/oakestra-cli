package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var uninstallSudo bool

// ─── top-level uninstall command ──────────────────────────────────────────────

var uninstallCmd = &cobra.Command{
	Use:   "uninstall <root|cluster|worker>",
	Short: "Uninstall Oakestra components from this machine",
	RunE:  func(cmd *cobra.Command, args []string) error { return cmd.Help() },
}

func init() {
	uninstallCmd.AddCommand(uninstallRootCmd)
	uninstallCmd.AddCommand(uninstallClusterCmd)
	uninstallCmd.AddCommand(uninstallWorkerCmd)

	// --root is inherited by all uninstall subcommands.
	uninstallCmd.PersistentFlags().BoolVar(&uninstallSudo, "root", false,
		"Run docker compose commands with sudo")
}

// ─── uninstall root ───────────────────────────────────────────────────────────

var uninstallRootCmd = &cobra.Command{
	Use:   "root",
	Short: "Stop and remove the root orchestrator",
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("Stopping root orchestrator…")
		return shellRun(uninstallSudo,
			"docker compose -f ~/.oakestra/root_orchestrator/root-orchestrator.yml down")
	},
}

// ─── uninstall cluster ────────────────────────────────────────────────────────

var uninstallClusterCmd = &cobra.Command{
	Use:   "cluster",
	Short: "Stop and remove the cluster orchestrator",
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("Stopping cluster orchestrator…")
		return shellRun(uninstallSudo,
			"docker compose -f ~/.oakestra/cluster_orchestrator/cluster-orchestrator.yml down")
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
