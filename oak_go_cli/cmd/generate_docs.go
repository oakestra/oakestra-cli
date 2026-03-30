//go:build docs
// +build docs

package cmd

import (
	"log"

	"github.com/spf13/cobra/doc"
)

func GenerateDocs(path string) {
	err := doc.GenMarkdownTree(rootCmd, path)
	if err != nil {
		log.Fatal(err)
	}
}
