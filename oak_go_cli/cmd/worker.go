package cmd

import (
	"os"
	"os/exec"

	"github.com/spf13/cobra"
)

// nodeEngineInstalled returns true if the NodeEngine binary is on the PATH.
func nodeEngineInstalled() bool {
	_, err := exec.LookPath("NodeEngine")
	return err == nil
}

// workerCmd is a transparent passthrough to `sudo NodeEngine`.
// All arguments (including flags) are forwarded verbatim.
// It is only registered in the root command when NodeEngine is present.
var workerCmd = &cobra.Command{
	Use:   "worker [NodeEngine args...]",
	Short: "Manage the local NodeEngine worker node",
	Long: `Manage the local NodeEngine worker node.

Every argument is passed directly to 'sudo NodeEngine'.

Examples:
  oak worker            → sudo NodeEngine
  oak worker -d         → sudo NodeEngine -d        (daemon mode)
  oak worker stop       → sudo NodeEngine stop
  oak worker --help     → sudo NodeEngine --help`,
	// DisableFlagParsing passes all args (including flags like -d) through
	// to NodeEngine without Cobra intercepting them.
	DisableFlagParsing: true,
	RunE: func(cmd *cobra.Command, args []string) error {
		c := exec.Command("sudo", append([]string{"NodeEngine"}, args...)...)
		c.Stdin = os.Stdin
		c.Stdout = os.Stdout
		c.Stderr = os.Stderr
		return c.Run()
	},
}
