//go:build docs
// +build docs

package cmd

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/spf13/cobra/doc"
)

const fmTemplate = `---
date: %s
lastmod: %s
title: "%s"
description: "Documentation for the Oakestra CLI command: %s"
summary: ""
draft: false
toc: true
sidebar:
  collapsed: false
seo:
  title: "%s" # custom title (optional)
---
`

func GenerateDocs(outputDir string) {
	filePrepender := func(filename string) string {
		now := time.Now().Format(time.RFC3339)
		name := filepath.Base(filename)
		base := strings.TrimSuffix(name, filepath.Ext(name))
		return fmt.Sprintf(fmTemplate, now, now, strings.Replace(base, "_", " ", -1), strings.Replace(base, "_", " ", -1), strings.Replace(base, "_", " ", -1))
	}
	linkHandler := func(name string) string {
		base := strings.TrimSuffix(name, filepath.Ext(name))
		return "../" + strings.ToLower(base)
	}
	err := doc.GenMarkdownTreeCustom(rootCmd, outputDir, filePrepender, linkHandler)
	if err != nil {
		log.Fatal(err)
	}

	err = removeSynopsisSections(outputDir)
	if err != nil {
		log.Fatal(err)
	}
}

func removeSynopsisSections(docsPath string) error {
	entries, err := os.ReadDir(docsPath)
	if err != nil {
		return err
	}

	for _, entry := range entries {
		if entry.IsDir() || filepath.Ext(entry.Name()) != ".md" {
			continue
		}

		filePath := filepath.Join(docsPath, entry.Name())
		content, err := os.ReadFile(filePath)
		if err != nil {
			return err
		}

		cleaned := stripSynopsis(string(content))
		if cleaned == string(content) {
			continue
		}

		if err := os.WriteFile(filePath, []byte(cleaned), 0644); err != nil {
			return err
		}
	}

	return nil
}

func stripSynopsis(markdown string) string {
	lines := strings.Split(markdown, "\n")
	result := make([]string, 0, len(lines))
	insideSynopsis := false

	for _, line := range lines {
		if line == "### Synopsis" {
			insideSynopsis = true
			continue
		}

		if insideSynopsis {
			if strings.HasPrefix(line, "### ") {
				insideSynopsis = false
			} else {
				continue
			}
		}

		result = append(result, line)
	}

	return strings.Join(result, "\n")
}
