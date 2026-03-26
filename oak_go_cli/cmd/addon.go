package cmd

import "github.com/spf13/cobra"

// addonCmd is the top-level "addon" command.
var addonCmd = &cobra.Command{
	Use:     "addon",
	Aliases: []string{"add"},
	Short:   "Manage Oakestra addons",
	RunE: func(cmd *cobra.Command, args []string) error {
		return cmd.Help()
	},
}

func init() {
	addonCmd.AddCommand(addonFlopsCmd)
}
