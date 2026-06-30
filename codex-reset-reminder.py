#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


API_URL = "https://chatgpt.com/backend-api/wham/rate-limit-reset-credits"
STATE_PATH = Path.home() / ".codex" / "reset-credit-reminder-state.json"
AUTH_PATH = Path.home() / ".codex" / "auth.json"
THRESHOLDS = [
    ("3d", timedelta(days=3), "3 天内"),
    ("1d", timedelta(days=1), "24 小时内"),
    ("6h", timedelta(hours=6), "6 小时内"),
]


def local_tz():
    name = os.environ.get("TZ")
    if name:
        try:
            return ZoneInfo(name)
        except Exception:
            pass
    return datetime.now().astimezone().tzinfo


def parse_time(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        seconds = value / 1000 if value > 10_000_000_000 else value
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    if isinstance(value, str):
        raw = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return None


def load_access_token():
    try:
        data = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RuntimeError("找不到 ~/.codex/auth.json，请先登录 Codex。")
    except json.JSONDecodeError:
        raise RuntimeError("~/.codex/auth.json 不是有效 JSON。")

    token = data.get("tokens", {}).get("access_token")
    if not token:
        raise RuntimeError("~/.codex/auth.json 中没有 tokens.access_token，请重新登录 Codex。")
    return token


def fetch_credits(token):
    config = "\n".join(
        [
            "silent",
            "show-error",
            "location",
            "connect-timeout = 10",
            "max-time = 45",
            f'url = "{API_URL}"',
            'header = "Accept: application/json"',
            'header = "User-Agent: codex-reset-reminder"',
            f'header = "Authorization: Bearer {token}"',
            "write-out = \"\\n%{http_code}\"",
        ]
    )
    result = subprocess.run(
        ["curl", "--config", "-"],
        input=config,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"请求失败：curl exit {result.returncode}")

    body, _, status_text = result.stdout.rpartition("\n")
    status_code = int(status_text) if status_text.isdigit() else 0
    if status_code == 401:
        raise RuntimeError("401：凭证失效或没有带 Authorization header。")
    if status_code < 200 or status_code >= 300:
        raise RuntimeError(f"接口返回 HTTP {status_code}。")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise RuntimeError("接口返回内容不是 JSON。")

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("credits", "rate_limit_reset_credits", "items", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return []


def load_state():
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"notified": {}}
    except json.JSONDecodeError:
        return {"notified": {}}


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATE_PATH)


def notify(title, message, dry_run=False):
    if dry_run:
        print(f"[通知预览] {title}: {message}")
        return
    title = title.replace("\\", "\\\\").replace('"', '\\"')
    message = message.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(
        ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
        check=False,
    )


def alert(title, message, dry_run=False):
    if dry_run:
        print(f"[弹窗预览] {title}: {message}")
        return
    title = title.replace("\\", "\\\\").replace('"', '\\"')
    message = message.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(
        ["osascript", "-e", f'display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK"'],
        check=False,
    )


def credit_key(credit, expires_at):
    title = credit.get("title") or "Untitled"
    status = credit.get("status") or "unknown"
    return f"{status}|{title}|{expires_at.isoformat()}"


def run(args):
    if args.test_notification:
        message = "示例提醒：你当前有 3 次 Codex reset 机会，其中 1 次将在 24 小时内到期。"
        notify(
            "Codex Reset Credit",
            message,
            dry_run=args.dry_run,
        )
        alert("Codex Reset Credit", message, dry_run=args.dry_run)
        return

    token = load_access_token()
    credits = fetch_credits(token)
    now = datetime.now(timezone.utc)
    tz = local_tz()
    state = load_state()
    notified = state.setdefault("notified", {})
    available = [c for c in credits if isinstance(c, dict) and c.get("status") == "available"]

    if args.print_summary:
        print(f"available_count: {len(available)}")

    for credit in available:
        expires_at = parse_time(credit.get("expires_at"))
        if not expires_at:
            continue

        remaining = expires_at - now
        key = credit_key(credit, expires_at)
        sent = set(notified.get(key, []))
        local_expiry = expires_at.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")

        if args.print_summary:
            print(f"- {credit.get('title')}: {local_expiry}")

        if remaining <= timedelta(0):
            continue

        for threshold_key, threshold_delta, label in THRESHOLDS:
            if remaining <= threshold_delta and threshold_key not in sent:
                notify(
                    "Codex Reset Credit",
                    f"你当前有 {len(available)} 次 Codex reset 机会，其中 1 次将在{label}到期：{local_expiry}。",
                    dry_run=args.dry_run,
                )
                sent.add(threshold_key)

        if sent:
            notified[key] = sorted(sent)

    if not args.dry_run:
        save_state(state)


def main():
    parser = argparse.ArgumentParser(description="Codex reset credit 到期提醒")
    parser.add_argument("--dry-run", action="store_true", help="只预览通知，不写入状态文件")
    parser.add_argument("--print-summary", action="store_true", help="打印可用数量和到期时间")
    parser.add_argument("--test-notification", action="store_true", help="立刻发送一条测试通知")
    args = parser.parse_args()

    try:
        run(args)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
