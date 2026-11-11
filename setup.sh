#!/usr/bin/env bash
# Universal installer: Kali / Debian / Ubuntu, Termux (Android), other Linux.
# For Docker, use the Dockerfile instead (see README).
set -u
cd "$(dirname "$0")"
mkdir -p bin

PY_TOOLS="holehe sherlock-project maigret h8mail"
ok()   { printf "\033[32m[+]\033[0m %s\n" "$*"; }
warn() { printf "\033[33m[!]\033[0m %s\n" "$*"; }

# ---------- detect environment ----------
if [ -n "${PREFIX:-}" ] && [ -d "${PREFIX:-}/bin" ] && echo "$PREFIX" | grep -q "com.termux"; then
  ENV="termux"
elif command -v apt-get >/dev/null 2>&1; then
  ENV="debian"      # Kali, Debian, Ubuntu, Parrot
else
  ENV="other"
fi
ok "Detected environment: $ENV"

# ---------- system packages ----------
if [ "$ENV" = "termux" ]; then
  pkg update -y
  pkg install -y python git curl golang clang make libxml2 libxslt libffi openssl rust binutils
elif [ "$ENV" = "debian" ]; then
  SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
  $SUDO apt-get update -y
  $SUDO apt-get install -y python3 python3-venv python3-pip git curl \
      build-essential libxml2-dev libxslt1-dev libffi-dev libssl-dev
else
  warn "Unknown system: make sure python3, pip, git and curl are installed."
fi

# ---------- python virtual environment ----------
if [ "$ENV" = "termux" ]; then
  # lxml etc. compile slowly on Termux; build flags help
  export CFLAGS="-Wno-error=incompatible-function-pointer-types -O0"
fi
python3 -m venv venv || { warn "venv failed"; exit 1; }
# shellcheck disable=SC1091
. venv/bin/activate
pip install --upgrade pip wheel setuptools

for t in $PY_TOOLS; do
  if pip install "$t"; then ok "installed $t"; else warn "FAILED to install $t (continuing)"; fi
done

# ---------- PhoneInfoga (Go binary) ----------
install_phoneinfoga() {
  if command -v phoneinfoga >/dev/null 2>&1 || [ -x bin/phoneinfoga ]; then
    ok "phoneinfoga already present"; return
  fi
  ARCH="$(uname -m)"
  case "$ARCH" in
    x86_64|amd64)  PI_ARCH="x86_64" ;;
    aarch64|arm64) PI_ARCH="arm64" ;;
    armv7l|armv8l) PI_ARCH="armv7" ;;
    *) PI_ARCH="" ;;
  esac
  if [ "$ENV" != "termux" ] && [ -n "$PI_ARCH" ]; then
    URL="https://github.com/sundowndev/phoneinfoga/releases/latest/download/phoneinfoga_Linux_${PI_ARCH}.tar.gz"
    if curl -fsSL "$URL" | tar -xz -C bin phoneinfoga 2>/dev/null; then
      chmod +x bin/phoneinfoga; ok "phoneinfoga installed to ./bin"; return
    fi
    warn "release download failed, trying go install"
  fi
  if command -v go >/dev/null 2>&1; then
    GOBIN="$(pwd)/bin" go install github.com/sundowndev/phoneinfoga/v2/cmd/phoneinfoga@latest \
      && ok "phoneinfoga built with go" && return
  fi
  warn "phoneinfoga NOT installed. Phone scans will be skipped."
  warn "Manual: https://github.com/sundowndev/phoneinfoga"
}
install_phoneinfoga

echo
ok "Done. Run with:  ./run.sh --authorized --email you@example.com"
