#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/.local/share/codex-reset-reminder"
BIN_DIR="$HOME/.local/bin"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST="$LAUNCH_AGENTS_DIR/com.codex-reset-reminder.plist"
SCRIPT="$APP_DIR/codex-reset-reminder.py"
BASE_URL="${CODEX_RESET_REMINDER_BASE_URL:-https://raw.githubusercontent.com/Rui-Huang-dotcom/codex-reset-reminder/main}"

mkdir -p "$APP_DIR" "$BIN_DIR" "$LAUNCH_AGENTS_DIR"

SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SOURCE_DIR/codex-reset-reminder.py" ]; then
  cp "$SOURCE_DIR/codex-reset-reminder.py" "$SCRIPT"
else
  curl -fsSL "$BASE_URL/codex-reset-reminder.py" -o "$SCRIPT"
fi
chmod +x "$SCRIPT"

cat > "$BIN_DIR/codex-reset-reminder" <<EOF
#!/usr/bin/env bash
exec /usr/bin/env python3 "$SCRIPT" "\$@"
EOF
chmod +x "$BIN_DIR/codex-reset-reminder"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.codex-reset-reminder</string>
  <key>ProgramArguments</key>
  <array>
    <string>$BIN_DIR/codex-reset-reminder</string>
  </array>
  <key>StartInterval</key>
  <integer>86400</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>$HOME/Library/Logs/codex-reset-reminder.log</string>
  <key>StandardErrorPath</key>
  <string>$HOME/Library/Logs/codex-reset-reminder.err.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" >/dev/null 2>&1 || true
launchctl load "$PLIST"

"$BIN_DIR/codex-reset-reminder" --print-summary

echo
echo "Installed codex-reset-reminder."
echo "It checks once a day and sends macOS notifications before reset credits expire."
echo "Manual check: $BIN_DIR/codex-reset-reminder --print-summary"
echo "Test notification: $BIN_DIR/codex-reset-reminder --test-notification"
