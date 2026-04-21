#!/usr/bin/env bash
# ReconAI - Tools Installer
# Arch Linux / CachyOS / Manjaro
# by @0xnhsec

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"
CYAN="\033[96m"; BOLD="\033[1m"; DIM="\033[2m"; RESET="\033[0m"

log_ok()   { echo -e "  ${GREEN}[+]${RESET} $1"; }
log_info() { echo -e "  ${CYAN}[*]${RESET} $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${RESET} $1"; }
log_err()  { echo -e "  ${RED}[x]${RESET} $1"; }
log_skip() { echo -e "  ${DIM}[-]${RESET} $1 — skipped (already installed)"; }

check_tool() { command -v "$1" &>/dev/null; }

SEP="────────────────────────────────────────────────────────────"

echo ""
echo -e "${CYAN} ███████╗███████╗ ██████╗ ██████╗ ███╗   ██╗ █████╗ ██╗${RESET}"
echo -e "${CYAN} ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║██╔══██╗██║${RESET}"
echo -e "${CYAN} ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║███████║██║${RESET}"
echo -e "${CYAN} ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║██╔══██║██║${RESET}"
echo -e "${CYAN} ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║██║  ██║██║${RESET}"
echo -e "${CYAN} ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝${RESET}"
echo -e "  Tools Installer For  Arch / CachyOS                @0xnhsec"
echo ""
echo $SEP

# ── Preflight ────────────────────────────────────────────────────────────────

log_info "Checking prerequisites..."

if ! check_tool go; then
    log_warn "Go not found — installing via pacman"
    sudo pacman -S --noconfirm go
fi

if ! check_tool pip; then
    log_warn "pip not found — installing python-pip"
    sudo pacman -S --noconfirm python-pip
fi

if ! check_tool git; then
    log_warn "git not found — installing"
    sudo pacman -S --noconfirm git
fi

if ! check_tool yay; then
    log_warn "yay not found — installing AUR helper"
    sudo pacman -S --noconfirm --needed base-devel
    git clone https://aur.archlinux.org/yay.git /tmp/yay
    cd /tmp/yay && makepkg -si --noconfirm
    cd -
fi

# Make sure GOPATH/bin is in PATH
export PATH="$PATH:$(go env GOPATH)/bin"
GOBIN="$(go env GOPATH)/bin"

echo ""
echo $SEP
log_info "Installing tools..."
echo ""

FAILED=()
INSTALLED=()
SKIPPED=()

# ── Helper functions ──────────────────────────────────────────────────────────

install_go() {
    local name=$1
    local pkg=$2
    if check_tool "$name"; then
        log_skip "$name"
        SKIPPED+=("$name")
    else
        log_info "Installing $name..."
        if go install "${pkg}@latest" 2>/dev/null; then
            log_ok "$name installed"
            INSTALLED+=("$name")
        else
            log_err "$name failed"
            FAILED+=("$name")
        fi
    fi
}

install_aur() {
    local name=$1
    local pkg=${2:-$1}
    if check_tool "$name"; then
        log_skip "$name"
        SKIPPED+=("$name")
    else
        log_info "Installing $name (AUR)..."
        if yay -S --noconfirm "$pkg" 2>/dev/null; then
            log_ok "$name installed"
            INSTALLED+=("$name")
        else
            log_err "$name failed"
            FAILED+=("$name")
        fi
    fi
}

install_pip() {
    local name=$1
    local pkg=$2
    log_info "Installing $name (pip)..."
    if pip install "$pkg" --break-system-packages -q 2>/dev/null; then
        log_ok "$name installed"
        INSTALLED+=("$name")
    else
        log_err "$name failed"
        FAILED+=("$name")
    fi
}

install_git() {
    local name=$1
    local repo=$2
    local install_cmd=$3
    local dir="/opt/reconai-tools/$name"
    if check_tool "$name"; then
        log_skip "$name"
        SKIPPED+=("$name")
        return
    fi
    log_info "Installing $name (git)..."
    sudo mkdir -p /opt/reconai-tools
    sudo git clone "$repo" "$dir" 2>/dev/null
    if [ -n "$install_cmd" ]; then
        cd "$dir" && eval "$install_cmd" 2>/dev/null && cd -
    fi
    log_ok "$name cloned → $dir"
    INSTALLED+=("$name")
}

# ── Phase 1 — Asset Discovery ─────────────────────────────────────────────────
echo -e "  ${BOLD}[ Phase 1 — Asset Discovery ]${RESET}"

install_go "assetfinder"  "github.com/tomnomnom/assetfinder"
install_go "waybackurls"  "github.com/tomnomnom/waybackurls"
install_pip "sublist3r"   "git+https://github.com/aboul3la/Sublist3r.git"
# crt.sh via requests (already in requirements)

echo ""

# ── Phase 2 — Live Validation ─────────────────────────────────────────────────
echo -e "  ${BOLD}[ Phase 2 — Live Validation ]${RESET}"

install_go "httprobe"  "github.com/tomnomnom/httprobe"
install_go "httpx"     "github.com/projectdiscovery/httpx/cmd/httpx"
install_go "naabu"     "github.com/projectdiscovery/naabu/v2/cmd/naabu"
install_aur "rustscan"

echo ""

# ── Phase 3 — Fingerprint & Crawl ────────────────────────────────────────────
echo -e "  ${BOLD}[ Phase 3 — Fingerprint & Crawl ]${RESET}"

install_go  "katana"      "github.com/projectdiscovery/katana/cmd/katana"
install_go  "nuclei"      "github.com/projectdiscovery/nuclei/v3/cmd/nuclei"
install_go  "subjs"       "github.com/lc/subjs"
install_aur "whatweb"
install_pip "paramspider" "git+https://github.com/devanshbatham/paramspider.git"
install_git "SecretFinder" \
    "https://github.com/m4ll0k/SecretFinder.git" \
    "pip install -r requirements.txt --break-system-packages -q"

echo ""

# ── Nuclei Templates ──────────────────────────────────────────────────────────
echo -e "  ${BOLD}[ Nuclei Templates ]${RESET}"
if check_tool "nuclei"; then
    log_info "Updating nuclei templates..."
    nuclei -update-templates 2>/dev/null && log_ok "Templates updated"
else
    log_warn "nuclei not found — skipping template update"
fi

echo ""

# ── Python Requirements ───────────────────────────────────────────────────────
echo -e "  ${BOLD}[ Python Requirements ]${RESET}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -r "$SCRIPT_DIR/requirements.txt" --break-system-packages -q
    log_ok "requirements.txt installed"
fi

echo ""
echo $SEP

# ── PATH reminder ─────────────────────────────────────────────────────────────
if [[ ":$PATH:" != *":$GOBIN:"* ]]; then
    echo ""
    log_warn "GOPATH/bin not in PATH. Add this to your ~/.zshrc or ~/.bashrc:"
    echo -e "  ${DIM}export PATH=\"\$PATH:$(go env GOPATH)/bin\"${RESET}"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${GREEN}[+] Installed : ${#INSTALLED[@]}${RESET}  → ${INSTALLED[*]}"
echo -e "  ${DIM}[-] Skipped   : ${#SKIPPED[@]}${RESET}   → ${SKIPPED[*]}"
if [ ${#FAILED[@]} -gt 0 ]; then
    echo -e "  ${RED}[x] Failed    : ${#FAILED[@]}${RESET}   → ${FAILED[*]}"
fi
echo ""
log_ok "Done! Run: python3 recon.py <target>"
echo ""
