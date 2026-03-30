//go:build docs
// +build docs

package main

import (
	"fmt"
	"os"

	"github.com/oakestra/oak-go-cli/cmd"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <output_dir>\n", os.Args[0])
		os.Exit(1)
	}
	cmd.GenerateDocs(os.Args[1])
	fmt.Printf("Documentation generated in: %s\n", os.Args[1])
}
