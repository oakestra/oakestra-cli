package cmd

import (
	"fmt"

	"github.com/spf13/cobra"

	"github.com/oakestra/oak-go-cli/internal/config"
)

// nolint:unused
var Version = "None"

var versionCmd = &cobra.Command{
	Use:     "version",
	Aliases: []string{"v"},
	Short:   "Show the CLI version",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("oak-go-cli version %s\n", Version)
		cfg, err := config.Load()
		if err == nil && cfg.SystemManagerIP != "" {
			fmt.Printf("System Manager: http://%s:10000\n", cfg.SystemManagerIP)
		}
	},
}

var apiDocsCmd = &cobra.Command{
	Use:   "api-docs",
	Short: "Show the Swagger API docs link",
	Run: func(cmd *cobra.Command, args []string) {
		cfg, err := config.Load()
		if err != nil || cfg.SystemManagerIP == "" {
			fmt.Println("System Manager IP not configured. Run: oak config set system_manager_ip <IP>")
			return
		}
		fmt.Printf("Swagger UI: http://%s:10000/api/docs\n", cfg.SystemManagerIP)
	},
}

var dashboardCmd = &cobra.Command{
	Use:   "dashboard-link",
	Short: "Show the Oakestra dashboard link",
	Run: func(cmd *cobra.Command, args []string) {
		cfg, err := config.Load()
		if err != nil || cfg.SystemManagerIP == "" {
			fmt.Println("System Manager IP not configured. Run: oak config set system_manager_ip <IP>")
			return
		}
		fmt.Printf("Dashboard: http://%s:80\n", cfg.SystemManagerIP)
	},
}
