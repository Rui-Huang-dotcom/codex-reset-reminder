#!/usr/bin/env bash
set -euo pipefail

PLIST="$HOME/Library/LaunchAgents/com.codex-reset-reminder.plist"

launchctl unload "$PLIST" >/dev/null 2>&1 || true
rm -f "$PLIST"
rm -f "$HOME/.local/bin/codex-reset-reminder"
rm -rf "$HOME/.local/share/codex-reset-reminder"

echo "Uninstalled codex-reset-reminder."
