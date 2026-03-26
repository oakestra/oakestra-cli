package cmd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/spf13/cobra"

	"github.com/oakestra/oak-go-cli/internal/config"
)

// addonFlopsCmd is the "oak addon flops" command.
var addonFlopsCmd = &cobra.Command{
	Use:     "flops",
	Aliases: []string{"fl"},
	Short:   "Manage the FLOps (Federated Learning Operations) addon",
	RunE: func(cmd *cobra.Command, args []string) error {
		return cmd.Help()
	},
}

func init() {
	addonFlopsCmd.AddCommand(flopsProjectCmd)
	addonFlopsCmd.AddCommand(flopsMockDataCmd)
	addonFlopsCmd.AddCommand(flopsTrackingCmd)
	addonFlopsCmd.AddCommand(flopsResetDatabaseCmd)
	addonFlopsCmd.AddCommand(flopsRestartManagementCmd)
	addonFlopsCmd.AddCommand(flopsClearRegistryCmd)

	flopsProjectCmd.Flags().BoolVar(&flopsProjectShow, "show", false, "Only display the SLA without submitting")
	flopsMockDataCmd.Flags().BoolVar(&flopsMockShow, "show", false, "Only display the SLA without submitting")
}

var (
	flopsProjectShow bool
	flopsMockShow    bool
)

// ─── flops project ────────────────────────────────────────────────────────────

var flopsProjectCmd = &cobra.Command{
	Use:     "project <sla-file>",
	Aliases: []string{"p"},
	Short:   "Start a new FLOps project from an SLA file",
	Args:    cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		slaPath := args[0]
		if flopsProjectShow {
			return printSLAFile(slaPath)
		}
		sla, err := loadSLA(slaPath)
		if err != nil {
			return err
		}
		return flopsPost("/api/flops/projects", sla,
			fmt.Sprintf("Init new FLOps project for SLA '%s'", slaPath))
	},
}

// ─── flops mock-data ──────────────────────────────────────────────────────────

var flopsMockDataCmd = &cobra.Command{
	Use:     "mock-data <sla-file>",
	Aliases: []string{"m", "mock"},
	Short:   "Deploy a mock-data-provider service from an SLA file",
	Args:    cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		slaPath := args[0]
		if flopsMockShow {
			return printSLAFile(slaPath)
		}
		sla, err := loadSLA(slaPath)
		if err != nil {
			return err
		}
		return flopsPost("/api/flops/mocks", sla,
			fmt.Sprintf("Init a new FLOps mock data service for SLA '%s'", slaPath))
	},
}

// ─── flops tracking ───────────────────────────────────────────────────────────

var flopsTrackingCmd = &cobra.Command{
	Use:     "tracking [customer-id]",
	Aliases: []string{"t"},
	Short:   "Deploy the Tracking Server and get its URL",
	Long: `Deploy the Tracking Server Service if it is not yet deployed.

Returns the URL of the tracking server for the specified customer (default: Admin).`,
	Args: cobra.MaximumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		customerID := "Admin"
		if len(args) == 1 {
			customerID = args[0]
		}
		return flopsGet("/api/flops/tracking", map[string]string{"customerID": customerID})
	},
}

// ─── flops reset-database ─────────────────────────────────────────────────────

var flopsResetDatabaseCmd = &cobra.Command{
	Use:     "reset-database [customer-id]",
	Aliases: []string{"redb"},
	Short:   "Reset the FLOps addon database (admin only)",
	Args:    cobra.MaximumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		customerID := "Admin"
		if len(args) == 1 {
			customerID = args[0]
		}
		return flopsDelete("/api/flops/database", map[string]string{"customerID": customerID})
	},
}

// ─── flops restart-management ─────────────────────────────────────────────────

var flopsRestartManagementCmd = &cobra.Command{
	Use:     "restart-management",
	Aliases: []string{"restart", "re"},
	Short:   "Restart FLOps Management via Docker Compose",
	RunE: func(cmd *cobra.Command, args []string) error {
		composePath, err := flopsComposePath()
		if err != nil {
			return err
		}
		fmt.Println("Restarting FLOps Management (Docker Compose)…")
		down := exec.Command("docker", "compose", "-f", composePath, "down")
		down.Stdout = os.Stdout
		down.Stderr = os.Stderr
		if err := down.Run(); err != nil {
			return fmt.Errorf("docker compose down: %w", err)
		}
		up := exec.Command("docker", "compose", "-f", composePath, "up", "--build", "-d")
		up.Stdout = os.Stdout
		up.Stderr = os.Stderr
		if err := up.Run(); err != nil {
			return fmt.Errorf("docker compose up: %w", err)
		}
		fmt.Printf("%s FLOps Management restarted.\n", green("✓"))
		return nil
	},
}

// ─── flops clear-registry ─────────────────────────────────────────────────────

var flopsClearRegistryCmd = &cobra.Command{
	Use:   "clear-registry",
	Short: "Clear the FLOps Docker image registry",
	RunE: func(cmd *cobra.Command, args []string) error {
		composePath, err := flopsComposePath()
		if err != nil {
			return err
		}
		c := exec.Command("docker", "compose", "-f", composePath,
			"exec", "flops_image_registry",
			"bash", "-c", "rm -rf /var/lib/registry/*")
		c.Stdout = os.Stdout
		c.Stderr = os.Stderr
		if err := c.Run(); err != nil {
			return fmt.Errorf("clearing registry: %w", err)
		}
		fmt.Printf("%s Registry cleared.\n", green("✓"))
		return nil
	},
}

// ─── helpers ──────────────────────────────────────────────────────────────────

// flopsBaseURL returns the Root FL Manager URL (system_manager_ip:5072).
func flopsBaseURL() (string, error) {
	cfg, err := config.Load()
	if err != nil {
		return "", err
	}
	ip := cfg.SystemManagerIP
	if ip == "" {
		ip = config.DefaultSystemManagerIP
	}
	return fmt.Sprintf("http://%s:5072", ip), nil
}

// flopsComposePath returns the path to the FLOps management docker-compose file.
func flopsComposePath() (string, error) {
	cfg, err := config.Load()
	if err != nil {
		return "", err
	}
	if cfg.FlopsRepoPath == "" {
		return "", fmt.Errorf(
			"flops_repo_path is not configured.\n" +
				"Set it with: oak config set flops_repo_path <path-to-flops-repo>")
	}
	return filepath.Join(cfg.FlopsRepoPath, "docker", "flops_management.docker_compose.yml"), nil
}

// loadSLA reads a JSON SLA file and returns it as a map.
func loadSLA(path string) (map[string]interface{}, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("reading SLA file %q: %w", path, err)
	}
	var sla map[string]interface{}
	if err := json.Unmarshal(data, &sla); err != nil {
		return nil, fmt.Errorf("parsing SLA file %q: %w", path, err)
	}
	return sla, nil
}

// printSLAFile pretty-prints a JSON SLA file to stdout.
func printSLAFile(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("reading SLA file %q: %w", path, err)
	}
	var v interface{}
	if err := json.Unmarshal(data, &v); err != nil {
		return fmt.Errorf("parsing SLA file %q: %w", path, err)
	}
	pretty, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return err
	}
	fmt.Println(string(pretty))
	return nil
}

// flopsHTTPClient is a simple HTTP client for the FLOps API (port 5072).
var flopsHTTPClient = &http.Client{Timeout: 30 * time.Second}

func flopsPost(endpoint string, body interface{}, action string) error {
	baseURL, err := flopsBaseURL()
	if err != nil {
		return err
	}
	data, err := json.Marshal(body)
	if err != nil {
		return err
	}
	resp, err := flopsHTTPClient.Post(baseURL+endpoint, "application/json", bytes.NewReader(data))
	if err != nil {
		return fmt.Errorf("%s: %w", action, err)
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		return fmt.Errorf("%s returned HTTP %d: %s", action, resp.StatusCode, string(raw))
	}
	fmt.Printf("%s %s\n", green("✓"), action)
	if len(raw) > 0 {
		fmt.Println(string(raw))
	}
	return nil
}

func flopsGet(endpoint string, params map[string]string) error {
	baseURL, err := flopsBaseURL()
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodGet, baseURL+endpoint, nil)
	if err != nil {
		return err
	}
	if len(params) > 0 {
		q := req.URL.Query()
		for k, v := range params {
			q.Set(k, v)
		}
		req.URL.RawQuery = q.Encode()
	}
	resp, err := flopsHTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("GET %s: %w", endpoint, err)
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("GET %s returned HTTP %d: %s", endpoint, resp.StatusCode, string(raw))
	}
	fmt.Println(string(raw))
	return nil
}

func flopsDelete(endpoint string, body map[string]string) error {
	baseURL, err := flopsBaseURL()
	if err != nil {
		return err
	}
	data, err := json.Marshal(body)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodDelete, baseURL+endpoint, bytes.NewReader(data))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := flopsHTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("DELETE %s: %w", endpoint, err)
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("DELETE %s returned HTTP %d: %s", endpoint, resp.StatusCode, string(raw))
	}
	fmt.Printf("%s FLOps database reset.\n", green("✓"))
	return nil
}
