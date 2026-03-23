package cmd

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/spf13/cobra"

	"github.com/oakestra/oak-go-cli/internal/api"
)

// ─── top-level install command ────────────────────────────────────────────────

var installCmd = &cobra.Command{
	Use:   "install <root|cluster|worker|full> [version]",
	Short: "Install Oakestra components on this machine",
	RunE:  func(cmd *cobra.Command, args []string) error { return cmd.Help() },
}

// ─── flags ────────────────────────────────────────────────────────────────────

var (
	installRootYes    bool
	installClusterYes bool
	installWorkerYes  bool
	installFullYes    bool
)

func init() {
	installCmd.AddCommand(installRootCmd)
	installCmd.AddCommand(installClusterCmd)
	installCmd.AddCommand(installWorkerCmd)
	installCmd.AddCommand(installFullCmd)

	installRootCmd.Flags().BoolVarP(&installRootYes, "yes", "y", false, "Skip confirmation prompt")
	installClusterCmd.Flags().BoolVarP(&installClusterYes, "yes", "y", false, "Skip confirmation prompt")
	installWorkerCmd.Flags().BoolVarP(&installWorkerYes, "yes", "y", false, "Skip confirmation prompt")
	installFullCmd.Flags().BoolVarP(&installFullYes, "yes", "y", false, "Skip all confirmation prompts")
}

// ─── install root ─────────────────────────────────────────────────────────────

var installRootCmd = &cobra.Command{
	Use:   "root [version]",
	Short: "Install the Oakestra root orchestrator",
	Long: `Install the Oakestra root orchestrator on this machine.

Requires Docker with Compose support.
Optionally specify a version tag (e.g. v0.4.400).`,
	Args: cobra.MaximumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		return doInstallRoot(firstArg(args), installRootYes)
	},
}

func doInstallRoot(version string, yes bool) error {
	if !confirmInstall("Oakestra root orchestrator", yes) {
		fmt.Println("Aborted.")
		return nil
	}
	if err := checkDockerCompose(); err != nil {
		return err
	}
	setVersion(version)
	fmt.Println("Installing root orchestrator…")
	return runInteractive("sh", "-c", "curl -sfL oakestra.io/install-root.sh | sh")
}

// ─── install cluster ──────────────────────────────────────────────────────────

var installClusterCmd = &cobra.Command{
	Use:   "cluster [version]",
	Short: "Install the Oakestra cluster orchestrator",
	Long: `Install the Oakestra cluster orchestrator on this machine.

Requires Docker with Compose support.
Optionally specify a version tag (e.g. v0.4.400).`,
	Args: cobra.MaximumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		return doInstallCluster(firstArg(args), installClusterYes)
	},
}

func doInstallCluster(version string, yes bool) error {
	if !confirmInstall("Oakestra cluster orchestrator", yes) {
		fmt.Println("Aborted.")
		return nil
	}
	if err := checkDockerCompose(); err != nil {
		return err
	}
	setVersion(version)
	fmt.Println("Installing cluster orchestrator…")
	return runInteractive("sh", "-c", "curl -sfL oakestra.io/install-cluster.sh | sh")
}

// ─── install worker ───────────────────────────────────────────────────────────

var installWorkerCmd = &cobra.Command{
	Use:   "worker [version]",
	Short: "Install a NodeEngine worker node",
	Long: `Install a NodeEngine worker node on this machine.

Prerequisites:
  - At least one cluster orchestrator must be running and registered
    with the root orchestrator.

After installation the CLI will let you pick which cluster this
worker should join and will configure NodeEngine automatically.`,
	Args: cobra.MaximumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		return doInstallWorker(firstArg(args), installWorkerYes)
	},
}

func doInstallWorker(version string, yes bool) error {
	// Step 0: best-effort cluster presence check.
	client, clientErr := api.New()
	if clientErr == nil {
		clusters, err := client.GetClusters(false)
		if err != nil || len(clusters) == 0 {
			fmt.Println(yellow("Warning: no active clusters found. Make sure a cluster orchestrator is registered with the root orchestrator before proceeding."))
		}
	} else {
		fmt.Println(dim("(Cluster pre-check skipped — root orchestrator address not configured)"))
	}

	// Step 1: Confirm.
	if !confirmInstall("NodeEngine worker node", yes) {
		fmt.Println("Aborted.")
		return nil
	}

	// Step 2: Export version.
	setVersion(version)

	// Step 3: Run install script.
	fmt.Println("Installing NodeEngine worker node…")
	if err := runInteractive("sh", "-c", "curl -sfL oakestra.io/install-worker.sh | sh -"); err != nil {
		return fmt.Errorf("worker installation failed: %w", err)
	}

	// Step 4: Cluster selection and NodeEngine config.
	if clientErr == nil {
		if err := configureWorkerCluster(client); err != nil {
			fmt.Fprintf(os.Stderr, "%s could not configure cluster automatically: %v\n", yellow("Warning:"), err)
			fmt.Println("Run manually: " + bold("sudo NodeEngine config cluster <IP>"))
		}
	}

	// Steps 5-6: Optionally start the worker now.
	fmt.Println()
	if confirmPromptYN("Start the worker node now?", yes) {
		fmt.Println("Starting NodeEngine…")
		if err := runInteractive("sudo", "NodeEngine", "-d"); err != nil {
			fmt.Fprintf(os.Stderr, "%s failed to start NodeEngine: %v\n", yellow("Warning:"), err)
		}
	}

	// Step 7: Completion hint.
	fmt.Printf("\n%s  Use %s to manage the worker node.\n",
		green("✓ Worker node installed."), bold("oak worker"))
	return nil
}

// configureWorkerCluster shows registered clusters and runs
// `sudo NodeEngine config cluster <IP>` for the selected one.
func configureWorkerCluster(client *api.Client) error {
	clusters, err := client.GetClusters(false)
	if err != nil {
		return err
	}
	if len(clusters) == 0 {
		return fmt.Errorf("no active clusters available")
	}

	fmt.Println("\nAvailable clusters:")
	for i, c := range clusters {
		fmt.Printf("  [%d] %s  %s  (%s)\n",
			i+1,
			colorName(c.ClusterName),
			green(c.ClusterIP),
			c.ActiveStatus(),
		)
	}

	var clusterIP string
	if len(clusters) == 1 {
		clusterIP = clusters[0].ClusterIP
		fmt.Printf("Using the only available cluster: %s (%s)\n",
			colorName(clusters[0].ClusterName), clusterIP)
	} else {
		fmt.Print("Select a cluster (number): ")
		scanner := bufio.NewScanner(os.Stdin)
		scanner.Scan()
		n, err := strconv.Atoi(strings.TrimSpace(scanner.Text()))
		if err != nil || n < 1 || n > len(clusters) {
			return fmt.Errorf("invalid selection")
		}
		clusterIP = clusters[n-1].ClusterIP
	}

	fmt.Printf("Configuring NodeEngine → cluster %s…\n", green(clusterIP))
	return runInteractive("sudo", "NodeEngine", "config", "cluster", clusterIP)
}

// ─── install full ─────────────────────────────────────────────────────────────

var installFullCmd = &cobra.Command{
	Use:   "full [version]",
	Short: "Install root orchestrator, cluster orchestrator, and worker node",
	Long: `Install the full Oakestra stack on this machine:
  1. Root orchestrator
  2. Cluster orchestrator
  3. NodeEngine worker node

Requires Docker with Compose support.`,
	Args: cobra.MaximumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		version := firstArg(args)
		yes := installFullYes

		if !confirmInstall("Oakestra root orchestrator, cluster orchestrator, and worker node", yes) {
			fmt.Println("Aborted.")
			return nil
		}
		// Individual confirmations are skipped — user already confirmed above.
		if err := doInstallRoot(version, true); err != nil {
			return fmt.Errorf("root install: %w", err)
		}
		if err := doInstallCluster(version, true); err != nil {
			return fmt.Errorf("cluster install: %w", err)
		}
		// Worker start prompt still respects the yes flag.
		if err := doInstallWorker(version, yes); err != nil {
			return fmt.Errorf("worker install: %w", err)
		}
		return nil
	},
}

// ─── shared helpers ───────────────────────────────────────────────────────────

// confirmInstall prints a prompt and returns true if the user agrees or yes==true.
func confirmInstall(component string, yes bool) bool {
	if yes {
		return true
	}
	fmt.Printf("This will install the %s on this machine. Continue? [y/N] ", bold(component))
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
	ans := strings.ToLower(strings.TrimSpace(scanner.Text()))
	return ans == "y" || ans == "yes"
}

// confirmPromptYN is a generic yes/no prompt.
func confirmPromptYN(prompt string, yes bool) bool {
	if yes {
		return true
	}
	fmt.Printf("%s [y/N] ", prompt)
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
	ans := strings.ToLower(strings.TrimSpace(scanner.Text()))
	return ans == "y" || ans == "yes"
}

// checkDockerCompose verifies that docker compose (v2) or docker-compose (v1) is available.
func checkDockerCompose() error {
	if exec.Command("docker", "compose", "version").Run() == nil {
		return nil
	}
	if exec.Command("docker-compose", "version").Run() == nil {
		return nil
	}
	return fmt.Errorf("docker compose is not installed\n" +
		"Install Docker Engine with Compose support: https://docs.docker.com/compose/install/")
}

// setVersion exports OAKESTRA_VERSION if a non-empty version is given.
func setVersion(version string) {
	if version != "" {
		os.Setenv("OAKESTRA_VERSION", version) //nolint:errcheck
		fmt.Printf("Using OAKESTRA_VERSION=%s\n", version)
	}
}

// runInteractive runs a command with stdin/stdout/stderr attached to the terminal.
func runInteractive(name string, args ...string) error {
	cmd := exec.Command(name, args...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}
