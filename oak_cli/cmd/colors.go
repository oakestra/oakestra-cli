package cmd

import (
	"fmt"
	"os"
	"regexp"
	"strings"

	"golang.org/x/term"
)

// colorsEnabled is true when stdout is an interactive terminal and NO_COLOR is unset.
var colorsEnabled = term.IsTerminal(int(os.Stdout.Fd())) && os.Getenv("NO_COLOR") == ""

func ansi(code, s string) string {
	if !colorsEnabled {
		return s
	}
	return "\033[" + code + "m" + s + "\033[0m"
}

// Formatting
func bold(s string) string   { return ansi("1", s) }
func italic(s string) string { return ansi("3", s) }
func dim(s string) string    { return ansi("2", s) }

// Colors
func green(s string) string  { return ansi("32", s) }
func yellow(s string) string { return ansi("33", s) }
func cyan(s string) string   { return ansi("36", s) }
func blue(s string) string   { return ansi("34", s) }
func red(s string) string    { return ansi("31", s) }
func grey(s string) string   { return ansi("90", s) }

// Semantic helpers used across commands.
func colorID(s string) string     { return grey(s) }
func colorName(s string) string   { return cyan(s) }
func colorHeader(s string) string { return bold(s) }

func colorStatus(status string) string {
	switch status {
	case "RUNNING", "running":
		return green(status)
	case "no instances":
		return dim(status)
	case "":
		return dim("—")
	default:
		return yellow(status)
	}
}

// ------------------------------------------------------------------
// ANSI-aware table printing
//
// tabwriter uses byte lengths for column widths, which breaks when cells
// contain ANSI escape codes (invisible bytes that inflate the width).
// printTable computes column widths from *visible* character counts instead.
// ------------------------------------------------------------------

// visLen returns the printable (non-ANSI) length of s.
func visLen(s string) int {
	inEsc := false
	n := 0
	for _, r := range s {
		switch {
		case r == '\033':
			inEsc = true
		case inEsc && ((r >= 'A' && r <= 'Z') || (r >= 'a' && r <= 'z')):
			inEsc = false
		case !inEsc:
			n++
		}
	}
	return n
}

// padRight appends spaces until the visible length of s equals width.
func padRight(s string, width int) string {
	vl := visLen(s)
	if vl >= width {
		return s
	}
	return s + strings.Repeat(" ", width-vl)
}

// printTable renders a table with correct column alignment even when cells
// contain ANSI color codes. Headers are automatically bolded.
//
// Example:
//
//	printTable(
//	    []string{"ID", "NAME", "STATUS"},
//	    [][]string{
//	        {colorID("abc"), colorName("nginx"), green("RUNNING")},
//	    },
//	)
func printTable(headers []string, rows [][]string) {
	const gap = 3
	ncols := len(headers)

	// Calculate column widths from visible lengths.
	widths := make([]int, ncols)
	for i, h := range headers {
		widths[i] = visLen(h)
	}
	for _, row := range rows {
		for i, cell := range row {
			if i < ncols {
				if vl := visLen(cell); vl > widths[i] {
					widths[i] = vl
				}
			}
		}
	}

	printRow := func(cells []string, transform func(string) string) {
		for i, cell := range cells {
			if i >= ncols {
				break
			}
			s := cell
			if transform != nil {
				s = transform(s)
			}
			if i < ncols-1 {
				fmt.Print(padRight(s, widths[i]) + strings.Repeat(" ", gap))
			} else {
				fmt.Print(s)
			}
		}
		fmt.Println()
	}

	// Header row.
	printRow(headers, colorHeader)

	// Separator row.
	sep := make([]string, ncols)
	for i, w := range widths {
		sep[i] = dim(strings.Repeat("─", w))
	}
	printRow(sep, nil)

	// Data rows.
	for _, row := range rows {
		printRow(row, nil)
	}
}

// printKV prints a two-column key→value table (key bolded, value plain).
func printKV(pairs [][2]string) {
	maxKey := 0
	for _, p := range pairs {
		if l := visLen(p[0]); l > maxKey {
			maxKey = l
		}
	}
	for _, p := range pairs {
		fmt.Printf("%s  %s\n", padRight(colorHeader(p[0]), maxKey+len(colorHeader(""))-len("")), p[1])
	}
}

// ------------------------------------------------------------------
// Log stripping
// ------------------------------------------------------------------

// ansiEscRe matches ANSI/VT100 escape sequences.
var ansiEscRe = regexp.MustCompile(`\x1b(?:\[[0-9;?]*[a-zA-Z]|[()][0-9A-Za-z]|[^[]?)`)

// StripANSI removes ANSI escape sequences from s, making it safe to display
// in contexts that don't support them (e.g. piped output or log files).
func StripANSI(s string) string {
	return ansiEscRe.ReplaceAllString(s, "")
}
