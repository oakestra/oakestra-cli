// Package cmd wires up all Cobra sub-commands for oak-go-cli.
package cmd

import (
	"fmt"
	"os"
	"strings"
	"text/template"

	"github.com/spf13/cobra"
)

const banner = `
   ____        _     _____ _      _____
  / __ \      | |   / ____| |    |_   _|
 | |  | | __ _| | _| |    | |      | |
 | |  | |/ _` + "`" + ` | |/ / |    | |      | |
 | |__| | (_| |   <| |____| |____ _| |_
  \____/ \__,_|_|\_\\_____|______|_____|

`

// rootCmd is the top-level command. All sub-commands are added in Execute().
var rootCmd = &cobra.Command{
	Use:   "oak",
	Short: "oak — Oakestra CLI (Go edition)",
	Long:  banner + "A fast, portable CLI for managing Oakestra deployments.",
	// Show help when called with no arguments.
	RunE: func(cmd *cobra.Command, args []string) error {
		return cmd.Help()
	},
}

// Execute is the single entry-point called from main.go.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func init() {
	rootCmd.AddCommand(versionCmd)
	rootCmd.AddCommand(apiDocsCmd)
	rootCmd.AddCommand(dashboardCmd)
	rootCmd.AddCommand(applicationCmd)
	rootCmd.AddCommand(serviceCmd)
	rootCmd.AddCommand(clusterCmd)
	rootCmd.AddCommand(configCmd)

	// Register the template helper that shows "name (alias1, alias2)" in the
	// "Available Commands" section.
	cobra.AddTemplateFuncs(template.FuncMap{
		"nameWithAliases": func(cmd *cobra.Command) string {
			if len(cmd.Aliases) == 0 {
				return cmd.Name()
			}
			return cmd.Name() + " " + dim("("+strings.Join(cmd.Aliases, ", ")+")")
		},
		// visibleLen returns the printable (non-ANSI) length of s, used for padding.
		"visibleLen": func(s string) int {
			// Strip ANSI escape sequences for length calculation.
			inEscape := false
			n := 0
			for _, r := range s {
				switch {
				case r == '\033':
					inEscape = true
				case inEscape && r == 'm':
					inEscape = false
				case !inEscape:
					n++
				}
			}
			return n
		},
	})

	// Override the help template to use nameWithAliases in the command listing
	// and to colorise section headers.
	rootCmd.SetHelpTemplate(helpTemplate())
	// Propagate to all sub-commands.
	cobra.AddTemplateFunc("nameWithAliases", func(cmd *cobra.Command) string {
		if len(cmd.Aliases) == 0 {
			return cmd.Name()
		}
		return cmd.Name() + " " + dim("("+strings.Join(cmd.Aliases, ", ")+")")
	})
}

// helpTemplate returns a Cobra help template that:
//   - shows "(alias, …)" next to every command name
//   - bolds section headers when colors are enabled
func helpTemplate() string {
	h := func(s string) string { return bold(s) }
	return `{{with .Long}}{{. | trimRightSpace}}

{{end}}` + h("Usage:") + `{{if .Runnable}}
  {{.UseLine}}{{end}}{{if .HasAvailableSubCommands}}
  {{.CommandPath}} [command]{{end}}{{if gt (len .Aliases) 0}}

` + h("Aliases:") + `
  {{.NameAndAliases}}{{end}}{{if .HasExample}}

` + h("Examples:") + `
{{.Example}}{{end}}{{if .HasAvailableSubCommands}}

` + h("Available Commands:") + `{{range .Commands}}{{if (or .IsAvailableCommand (eq .Name "help"))}}
  {{nameWithAliases . | printf "%-38s"}} {{.Short}}{{end}}{{end}}{{end}}{{if .HasAvailableLocalFlags}}

` + h("Flags:") + `
{{.LocalFlags.FlagUsages | trimRightSpace}}{{end}}{{if .HasAvailableInheritedFlags}}

` + h("Global Flags:") + `
{{.InheritedFlags.FlagUsages | trimRightSpace}}{{end}}{{if .HasHelpSubCommands}}

` + h("Additional help topics:") + `{{range .Commands}}{{if .IsAdditionalHelpTopicCommand}}
  {{rpad .Name .NamePadding}} {{.Short}}{{end}}{{end}}{{end}}{{if .HasAvailableSubCommands}}

Use "{{.CommandPath}} [command] --help" for more information about a command.
{{end}}`
}
