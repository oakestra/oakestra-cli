package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"syscall"

	"github.com/spf13/cobra"
	"golang.org/x/term"

	"github.com/oakestra/oak-go-cli/internal/config"
)

// configCmd is the top-level "config" / "c" command.
var configCmd = &cobra.Command{
	Use:     "config",
	Aliases: []string{"c", "configuration"},
	Short:   "Manage oak-go-cli configuration",
	RunE: func(cmd *cobra.Command, args []string) error {
		return cmd.Help()
	},
}

func init() {
	configCmd.AddCommand(configSetCmd)
	configCmd.AddCommand(configShowCmd)
	configCmd.AddCommand(configResetCmd)
	configCmd.AddCommand(configCredentialsCmd)
}

// ─── config set ──────────────────────────────────────────────────────────────

var configSetCmd = &cobra.Command{
	Use:   "set <key> <value>",
	Short: "Set a configuration key",
	Long: `Set a configuration key to the given value.

Available keys:
  system_manager_ip   IP of the Oakestra System Manager (root orchestrator)
  cluster_manager_ip  IP of the Cluster Manager
  cluster_name        Name of the local cluster
  cluster_location    Location of the local cluster
  main_oak_repo_path  Path to the main Oakestra repository

For login credentials use: oak config credentials`,
	Example: `  oak config set system_manager_ip 192.168.1.10
  oak config set cluster_name my-cluster`,
	Aliases: []string{"k", "key-vars"},
	Args:    cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		key, value := strings.ToLower(args[0]), args[1]
		if err := config.Set(key, value); err != nil {
			return err
		}
		fmt.Printf("✓ Set %s = %s\n", key, value)
		return nil
	},
}

// ─── config credentials ──────────────────────────────────────────────────────

var configCredentialsCmd = &cobra.Command{
	Use:   "credentials [username] [password]",
	Short: "Configure Oakestra login credentials",
	Long: `Set the username and password used to authenticate with the Oakestra API.

Defaults are "Admin" / "Admin" when not configured.

If password is omitted you will be prompted to enter it securely (no echo).

Examples:
  oak config credentials                      # prompted for both
  oak config credentials myuser               # prompted for password
  oak config credentials myuser mypassword    # set both inline`,
	Aliases: []string{"creds", "auth"},
	Args:    cobra.RangeArgs(0, 2),
	RunE: func(cmd *cobra.Command, args []string) error {
		var username, password string

		switch len(args) {
		case 0:
			// Prompt for both.
			username = promptPlain("Username")
			var err error
			password, err = promptPassword("Password")
			if err != nil {
				return err
			}
		case 1:
			username = args[0]
			var err error
			password, err = promptPassword("Password")
			if err != nil {
				return err
			}
		case 2:
			username = args[0]
			password = args[1]
		}

		if username == "" {
			return fmt.Errorf("username cannot be empty")
		}
		if err := config.SetCredentials(username, password); err != nil {
			return err
		}
		fmt.Printf("✓ Credentials set for user %s\n", colorName(username))
		return nil
	},
}

// ─── config show ─────────────────────────────────────────────────────────────

var configShowCmd = &cobra.Command{
	Use:     "show",
	Aliases: []string{"s", "show-config"},
	Short:   "Show the current configuration",
	RunE: func(cmd *cobra.Command, args []string) error {
		if _, err := os.Stat(config.Path()); os.IsNotExist(err) {
			fmt.Println("No config file found. Use 'oak config set <key> <value>' to configure.")
			return nil
		}
		cfg, err := config.Load()
		if err != nil {
			return err
		}

		// Mask password in output.
		display := struct {
			SystemManagerIP  string `json:"system_manager_ip"`
			ClusterManagerIP string `json:"cluster_manager_ip"`
			ClusterName      string `json:"cluster_name"`
			ClusterLocation  string `json:"cluster_location"`
			MainOakRepoPath  string `json:"main_oak_repo_path"`
			Username         string `json:"username"`
			Password         string `json:"password"`
		}{
			SystemManagerIP:  cfg.SystemManagerIP,
			ClusterManagerIP: cfg.ClusterManagerIP,
			ClusterName:      cfg.ClusterName,
			ClusterLocation:  cfg.ClusterLocation,
			MainOakRepoPath:  cfg.MainOakRepoPath,
			Username:         cfg.GetUsername(),
			Password:         maskPassword(cfg.Password),
		}
		data, err := json.MarshalIndent(display, "", "  ")
		if err != nil {
			return err
		}
		fmt.Println(string(data))
		fmt.Printf("\n%s %s\n", dim("Config file:"), config.Path())
		return nil
	},
}

// ─── config reset ────────────────────────────────────────────────────────────

var configResetCmd = &cobra.Command{
	Use:     "reset",
	Aliases: []string{"reset-config"},
	Short:   "Reset the configuration to its initial (empty) state",
	RunE: func(cmd *cobra.Command, args []string) error {
		if err := config.Save(&config.Config{}); err != nil {
			return err
		}
		fmt.Println("Configuration reset to initial state.")
		return nil
	},
}

// ─── helpers ──────────────────────────────────────────────────────────────────

func promptPlain(label string) string {
	fmt.Printf("%s: ", label)
	var s string
	fmt.Scanln(&s)
	return s
}

func promptPassword(label string) (string, error) {
	fmt.Printf("%s: ", label)
	raw, err := term.ReadPassword(int(syscall.Stdin))
	fmt.Println() // newline after the silent input
	if err != nil {
		return "", fmt.Errorf("reading password: %w", err)
	}
	return string(raw), nil
}

func maskPassword(p string) string {
	if p == "" {
		return "(default)"
	}
	return strings.Repeat("*", len(p))
}
