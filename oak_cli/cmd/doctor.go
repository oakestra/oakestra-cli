package cmd

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/spf13/cobra"

	"github.com/oakestra/oak-go-cli/internal/config"
)

// ─── top-level doctor command ─────────────────────────────────────────────────

var aiTroubleshoot bool

var doctorCmd = &cobra.Command{
	Use:   "doctor",
	Short: "Check the health of Oakestra components",
	Long: `Check the health of Oakestra components.

Run without arguments for an interactive menu, or specify a component directly:

  oak doctor root     — root orchestrator containers
  oak doctor cluster  — cluster orchestrator containers
  oak doctor worker   — NodeEngine / NetManager services
  oak doctor all      — all of the above

Add --ai-troubleshoot to any subcommand to get AI-powered diagnostics via Claude.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		target := promptDoctorTarget()
		if aiTroubleshoot {
			return runAITroubleshoot(target)
		}
		return runDoctor(target)
	},
}

func init() {
	doctorCmd.PersistentFlags().BoolVar(&aiTroubleshoot, "ai-troubleshoot", false,
		"Use Claude AI for intelligent troubleshooting")
	doctorCmd.AddCommand(doctorRootCmd)
	doctorCmd.AddCommand(doctorClusterCmd)
	doctorCmd.AddCommand(doctorWorkerCmd)
	doctorCmd.AddCommand(doctorAllCmd)
}

var doctorRootCmd = &cobra.Command{
	Use:   "root",
	Short: "Check root orchestrator containers",
	RunE: func(cmd *cobra.Command, args []string) error {
		if aiTroubleshoot {
			return runAITroubleshoot("root")
		}
		return doctorCompose("root")
	},
}

var doctorClusterCmd = &cobra.Command{
	Use:   "cluster",
	Short: "Check cluster orchestrator containers",
	RunE: func(cmd *cobra.Command, args []string) error {
		if aiTroubleshoot {
			return runAITroubleshoot("cluster")
		}
		return doctorCompose("cluster")
	},
}

var doctorWorkerCmd = &cobra.Command{
	Use:   "worker",
	Short: "Check NodeEngine worker status",
	RunE: func(cmd *cobra.Command, args []string) error {
		if aiTroubleshoot {
			return runAITroubleshoot("worker")
		}
		return doctorWorker()
	},
}

var doctorAllCmd = &cobra.Command{
	Use:   "all",
	Short: "Check all Oakestra components",
	RunE: func(cmd *cobra.Command, args []string) error {
		if aiTroubleshoot {
			return runAITroubleshoot("all")
		}
		return doctorAll()
	},
}

// ─── interactive prompt ───────────────────────────────────────────────────────

func promptDoctorTarget() string {
	fmt.Println(bold("What would you like to check?"))
	fmt.Println("  [1] root     — root orchestrator containers")
	fmt.Println("  [2] cluster  — cluster orchestrator containers")
	fmt.Println("  [3] worker   — NodeEngine / NetManager")
	fmt.Println("  [4] all      — everything")
	fmt.Print("Selection [1-4]: ")

	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
	switch strings.TrimSpace(scanner.Text()) {
	case "1", "root":
		return "root"
	case "2", "cluster":
		return "cluster"
	case "3", "worker":
		return "worker"
	default:
		return "all"
	}
}

func runDoctor(target string) error {
	switch target {
	case "root":
		return doctorCompose("root")
	case "cluster":
		return doctorCompose("cluster")
	case "worker":
		return doctorWorker()
	default:
		return doctorAll()
	}
}

// ─── compose checks (root + cluster) ─────────────────────────────────────────

func doctorCompose(component string) error {
	fmt.Printf("%s Checking %s orchestrator…\n", bold("→"), component)

	ymlPath, err := findDoctorComposeYML(component)
	if err != nil {
		return err
	}
	fmt.Printf("  Compose file: %s\n\n", dim(ymlPath))

	services := composeServices(ymlPath)
	if len(services) == 0 {
		fmt.Println(yellow("  Warning: could not determine service list — showing global status."))
		printComposePS(ymlPath)
		return nil
	}

	checkContainerStatus(ymlPath, services)
	checkContainerLogs(ymlPath, services)
	return nil
}

// findDoctorComposeYML returns the compose file path for a component,
// falling back to ~/.oakestra/1-DOC.yaml if the canonical path is absent.
func findDoctorComposeYML(component string) (string, error) {
	home, _ := os.UserHomeDir()
	var primary string
	switch component {
	case "root":
		primary = filepath.Join(home, ".oakestra", "root_orchestrator", "root-orchestrator.yml")
	case "cluster":
		primary = filepath.Join(home, ".oakestra", "cluster_orchestrator", "cluster-orchestrator.yml")
	}
	if fileExists(primary) {
		return primary, nil
	}
	fallback := filepath.Join(home, ".oakestra", "1-DOC.yaml")
	if fileExists(fallback) {
		fmt.Printf("  %s Primary compose file not found, using fallback: %s\n",
			yellow("Note:"), fallback)
		return fallback, nil
	}
	return "", fmt.Errorf(
		"compose file not found:\n  tried: %s\n  tried: %s\n"+
			"Install with: oak install %s", primary, fallback, component)
}

// dockerCompose runs a docker compose command, trying without sudo first,
// then with sudo if the first attempt fails. Returns combined output.
func dockerCompose(ymlPath string, args ...string) ([]byte, error) {
	base := append([]string{"compose", "-f", ymlPath}, args...)
	if out, err := exec.Command("docker", base...).CombinedOutput(); err == nil {
		return out, nil
	}
	// Retry with sudo.
	return exec.Command("sudo", append([]string{"docker", "compose", "-f", ymlPath}, args...)...).CombinedOutput()
}

// composeServices returns the service names declared in a compose file.
// Tries docker compose v2 (with/without sudo), then docker-compose v1.
func composeServices(ymlPath string) []string {
	candidates := [][]string{
		{"docker", "compose", "-f", ymlPath, "config", "--services"},
		{"sudo", "docker", "compose", "-f", ymlPath, "config", "--services"},
		{"docker-compose", "-f", ymlPath, "config", "--services"},
		{"sudo", "docker-compose", "-f", ymlPath, "config", "--services"},
	}
	for _, cmd := range candidates {
		if out, err := exec.Command(cmd[0], cmd[1:]...).Output(); err == nil {
			return splitLines(out)
		}
	}
	return nil
}

// checkContainerStatus prints a ✓/✗ line per service.
func checkContainerStatus(ymlPath string, services []string) {
	fmt.Printf("%s\n", bold("Container Status:"))
	allOK := true
	for _, svc := range services {
		out, err := dockerCompose(ymlPath, "ps", svc)
		text := string(out)
		if err != nil {
			fmt.Printf("  %s %s  (could not query: %v)\n", red("✗"), colorName(svc), err)
			allOK = false
			continue
		}
		if strings.Contains(text, "Up") || strings.Contains(text, "running") {
			fmt.Printf("  %s %s\n", green("✓"), colorName(svc))
		} else {
			fmt.Printf("  %s %s  %s\n", red("✗"), colorName(svc), dim("(not running)"))
			allOK = false
		}
	}
	if allOK {
		fmt.Printf("  %s All containers running.\n", green("✓"))
	}
	fmt.Println()
}

// checkContainerLogs scans the last 1000 log lines per service for errors.
var logErrorRe = regexp.MustCompile(`(?i)\b(error|timeout|fatal|panic|exception)\b`)

func checkContainerLogs(ymlPath string, services []string) {
	fmt.Printf("%s\n", bold("Log Analysis (last 1000 lines per service):"))
	for _, svc := range services {
		out, err := dockerCompose(ymlPath, "logs", "--tail", "1000", svc)
		if err != nil {
			fmt.Printf("  %s %s  (could not read logs: %v)\n", yellow("!"), colorName(svc), err)
			continue
		}

		var hits []string
		for _, line := range strings.Split(string(out), "\n") {
			if logErrorRe.MatchString(line) {
				hits = append(hits, strings.TrimSpace(line))
			}
		}

		if len(hits) == 0 {
			fmt.Printf("  %s %s  no errors found\n", green("✓"), colorName(svc))
		} else {
			fmt.Printf("  %s %s  %s error/warning line(s) in last 1000\n",
				yellow("!"), colorName(svc), bold(fmt.Sprintf("%d", len(hits))))
			// Show the last 5 matching lines.
			shown := hits
			if len(shown) > 5 {
				shown = shown[len(shown)-5:]
			}
			for _, l := range shown {
				if len(l) > 120 {
					l = l[:117] + "…"
				}
				fmt.Printf("    %s %s\n", dim("↳"), l)
			}
		}
	}
	fmt.Println()
}

// printComposePS is the fallback when no service list is available.
func printComposePS(ymlPath string) {
	out, err := dockerCompose(ymlPath, "ps")
	if err != nil {
		fmt.Printf("  %s docker compose ps failed: %v\n", red("✗"), err)
		return
	}
	fmt.Println(string(out))
}

// ─── worker check ─────────────────────────────────────────────────────────────

func doctorWorker() error {
	fmt.Printf("%s Checking worker node…\n\n", bold("→"))

	out, err := exec.Command("sudo", "NodeEngine", "status").CombinedOutput()
	outputStr := string(out)

	if err != nil {
		fmt.Printf("%s NodeEngine status check failed: %v\n", red("✗"), err)
		workerLogHint()
		return nil
	}

	// Print the raw status output.
	fmt.Println(outputStr)

	// Count "Active: active" occurrences — one per healthy service (NodeEngine + NetManager).
	activeCount := strings.Count(outputStr, "Active: active")
	switch {
	case activeCount >= 2:
		fmt.Printf("%s NodeEngine and NetManager are both active.\n", green("✓"))
	case activeCount == 1:
		fmt.Printf("%s Only 1 of 2 services is active.\n", yellow("!"))
		workerLogHint()
	default:
		fmt.Printf("%s Neither NodeEngine nor NetManager appears to be active.\n", red("✗"))
		workerLogHint()
	}
	return nil
}

func workerLogHint() {
	fmt.Println("Check the logs:")
	fmt.Printf("  %s\n", dim("/var/log/oakestra/nodeengine.log"))
	fmt.Printf("  %s\n", dim("/var/log/oakestra/netmanager.log"))
}

// ─── all ──────────────────────────────────────────────────────────────────────

func doctorAll() error {
	sep := strings.Repeat("─", 50)
	fmt.Println(sep)
	if err := doctorCompose("root"); err != nil {
		fmt.Printf("%s Root check failed: %v\n\n", red("✗"), err)
	}
	fmt.Println(sep)
	if err := doctorCompose("cluster"); err != nil {
		fmt.Printf("%s Cluster check failed: %v\n\n", red("✗"), err)
	}
	fmt.Println(sep)
	return doctorWorker()
}

// ─── AI troubleshooting ───────────────────────────────────────────────────────

func runAITroubleshoot(component string) error {
	// Verify claude is installed.
	if !isClaudeInstalled() {
		fmt.Printf("%s Claude CLI is not installed.\n", red("✗"))
		fmt.Printf("Run %s to set up Claude for AI troubleshooting.\n", bold("oak config claude"))
		return nil
	}

	// Verify the skill is installed.
	skillPath := claudeSkillPath()
	if !fileExists(skillPath) {
		fmt.Printf("%s Oakestra troubleshooting skill is not installed.\n", yellow("!"))
		fmt.Printf("Run %s to install it.\n", bold("oak config claude"))
		return nil
	}

	fmt.Printf("%s AI Troubleshooting — %s\n\n", bold("→"), bold(component))
	fmt.Println("  [1] General healthcheck  (check if components are installed and running)")
	fmt.Println("  [2] Specific issue       (describe your problem)")
	fmt.Print("Selection [1-2]: ")

	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
	choice := strings.TrimSpace(scanner.Text())

	var prompt string
	if choice == "2" {
		fmt.Println()
		fmt.Print("Describe the issue: ")
		scanner.Scan()
		issue := strings.TrimSpace(scanner.Text())
		if issue == "" {
			issue = "general troubleshooting"
		}
		prompt = aiSpecificPrompt(component, issue)
	} else {
		prompt = aiHealthcheckPrompt(component)
	}

	cfg, err := config.Load()
	if err != nil {
		return err
	}
	skillName := strings.TrimSuffix(filepath.Base(cfg.GetTroubleshootSkillURL()), ".md")

	fmt.Println()
	fmt.Println(dim("Starting Claude AI session…"))
	fmt.Println()
	return runInteractive("claude", fmt.Sprintf("/%s %s", skillName, prompt))
}

func aiHealthcheckPrompt(component string) string {
	descriptions := map[string]string{
		"root":    "root orchestrator — check if the root orchestrator containers are installed, running, and report any problems",
		"cluster": "cluster orchestrator — check if the cluster orchestrator containers are installed, running, and report any problems",
		"worker":  "worker node — check if NodeEngine and NetManager are installed, running, and report any problems",
		"all":     "full Oakestra stack (root orchestrator, cluster orchestrator, and worker node) — check if all components are installed, running, and report any problems",
	}
	desc, ok := descriptions[component]
	if !ok {
		desc = component + " — perform a general healthcheck"
	}
	return fmt.Sprintf("Please perform a general healthcheck of the Oakestra %s.", desc)
}

func aiSpecificPrompt(component string, issue string) string {
	labels := map[string]string{
		"root":    "root orchestrator",
		"cluster": "cluster orchestrator",
		"worker":  "worker node (NodeEngine / NetManager)",
		"all":     "Oakestra stack",
	}
	label, ok := labels[component]
	if !ok {
		label = component
	}
	return fmt.Sprintf("I have an issue with my Oakestra %s: %s. Please help me troubleshoot this.", label, issue)
}

// ─── helpers ──────────────────────────────────────────────────────────────────

func splitLines(data []byte) []string {
	var out []string
	for _, l := range strings.Split(strings.TrimSpace(string(data)), "\n") {
		if l = strings.TrimSpace(l); l != "" {
			out = append(out, l)
		}
	}
	return out
}
