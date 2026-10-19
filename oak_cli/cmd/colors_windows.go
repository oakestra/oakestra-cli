//go:build windows

package cmd

import (
	"syscall"
	"unsafe"
)

const enableVirtualTerminalProcessing uint32 = 0x0004

func init() {
	if !colorsEnabled {
		return // already disabled (piped output, NO_COLOR, etc.)
	}

	// Try to enable ANSI virtual terminal processing so that escape codes
	// render correctly in Windows Terminal, PowerShell, and modern cmd.exe.
	// If it fails (e.g. old conhost), fall back to plain text.
	kernel32 := syscall.NewLazyDLL("kernel32.dll")
	getConsoleMode := kernel32.NewProc("GetConsoleMode")
	setConsoleMode := kernel32.NewProc("SetConsoleMode")

	handle, err := syscall.GetStdHandle(syscall.STD_OUTPUT_HANDLE)
	if err != nil {
		colorsEnabled = false
		return
	}

	var mode uint32
	ret, _, _ := getConsoleMode.Call(uintptr(handle), uintptr(unsafe.Pointer(&mode)))
	if ret == 0 {
		colorsEnabled = false
		return
	}

	ret, _, _ = setConsoleMode.Call(uintptr(handle), uintptr(mode|enableVirtualTerminalProcessing))
	if ret == 0 {
		// SetConsoleMode failed — ANSI not supported on this console.
		colorsEnabled = false
	}
}
