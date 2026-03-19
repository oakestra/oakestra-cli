# install.ps1 — oak CLI installer for Windows
# Run with:
#   irm https://raw.githubusercontent.com/oakestra/oakestra-cli/main/oak_go_cli/install.ps1 | iex

$ErrorActionPreference = 'Stop'

$Repo    = "oakestra/oakestra-cli"
$BaseUrl = "https://github.com/$Repo/releases/download"

# Detect architecture.
$Arch = switch ($env:PROCESSOR_ARCHITECTURE) {
    'ARM64'  { 'arm64' }
    'AMD64'  { 'amd64' }
    default  { Write-Error "Unsupported architecture: $env:PROCESSOR_ARCHITECTURE"; exit 1 }
}

# Fetch the latest release tag.
$ApiUrl    = "https://api.github.com/repos/$Repo/releases/latest"
$Release   = Invoke-RestMethod -Uri $ApiUrl -Headers @{ 'User-Agent' = 'oak-installer' }
$LatestTag = $Release.tag_name
if (-not $LatestTag) {
    Write-Error "Could not determine the latest release version."
    exit 1
}

$Filename    = "oak_cli_windows_$Arch.zip"
$DownloadUrl = "$BaseUrl/$LatestTag/$Filename"

# Create a temporary working directory.
$TmpDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
New-Item -ItemType Directory -Path $TmpDir | Out-Null

try {
    $ZipPath = Join-Path $TmpDir $Filename

    Write-Host "Downloading oak CLI $LatestTag for windows/$Arch ..."
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ZipPath -UseBasicParsing

    Write-Host "Extracting ..."
    Expand-Archive -Path $ZipPath -DestinationPath $TmpDir -Force

    # Install to %LOCALAPPDATA%\Programs\oak
    $InstallDir = Join-Path $env:LOCALAPPDATA "Programs\oak"
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Copy-Item (Join-Path $TmpDir "oak.exe") (Join-Path $InstallDir "oak.exe") -Force

    # Install bundled SLA templates to ~/oak_cli/SLAs/ (will not overwrite existing files).
    $SlaDir = Join-Path $env:USERPROFILE "oak_cli\SLAs"
    New-Item -ItemType Directory -Path $SlaDir -Force | Out-Null
    $ExtractedSlas = Join-Path $TmpDir "SLAs"
    if (Test-Path $ExtractedSlas) {
        Get-ChildItem $ExtractedSlas | ForEach-Object {
            $Dest = Join-Path $SlaDir $_.Name
            if (-not (Test-Path $Dest)) {
                Copy-Item $_.FullName $Dest -Recurse
            }
        }
        Write-Host "SLA templates installed to $SlaDir"
    }

    # Add install directory to the user PATH if not already present.
    $UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($UserPath -notlike "*$InstallDir*") {
        [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$InstallDir", "User")
        Write-Host "Added $InstallDir to your PATH."
        Write-Host "Restart your terminal (or open a new one) for 'oak' to be available."
    }

    # Shell completions for PowerShell — best-effort.
    try {
        $CompletionDir = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "PowerShell"
        New-Item -ItemType Directory -Path $CompletionDir -Force | Out-Null
        $ProfilePath = Join-Path $CompletionDir "Microsoft.PowerShell_profile.ps1"
        $CompletionLine = 'if (Get-Command oak -ErrorAction SilentlyContinue) { oak completion powershell | Out-String | Invoke-Expression }'
        if (-not (Test-Path $ProfilePath) -or -not (Select-String -Path $ProfilePath -Pattern 'oak completion' -Quiet)) {
            Add-Content -Path $ProfilePath -Value "`n$CompletionLine"
            Write-Host "PowerShell tab completion enabled (added to $ProfilePath)."
        }
    } catch {
        Write-Host "Note: could not configure PowerShell completions automatically — run 'oak completion powershell' manually."
    }

    Write-Host ""
    Write-Host "oak CLI $LatestTag installed successfully to $InstallDir\oak.exe"
    Write-Host "Run 'oak --help' to get started."

} finally {
    Remove-Item $TmpDir -Recurse -Force -ErrorAction SilentlyContinue
}
