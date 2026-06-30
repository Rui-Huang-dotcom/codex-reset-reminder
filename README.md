# codex-reset-reminder

本地运行的 Codex reset credit 到期提醒工具。它会读取本机 Codex 登录状态，查询 reset credits，并在快到期前通过 macOS 通知提醒你。

Local macOS reminder for Codex reset credits. It reads your local Codex auth state, checks reset credit expiry dates, and notifies you before they expire.

## 中文说明

### 安全边界

- 不上传 token。
- 不收集账号信息。
- 不打印 `access_token`、`refresh_token`、cookie 或完整唯一 ID。
- 请求只从用户本机发往 `https://chatgpt.com/backend-api/wham/rate-limit-reset-credits`。
- 状态文件只保存在本机 `~/.codex/reset-credit-reminder-state.json`。

### 安装

一条命令安装：

```bash
curl -fsSL https://raw.githubusercontent.com/Rui-Huang-dotcom/codex-reset-reminder/main/install.sh | bash
```

或者先 clone 再安装：

```bash
git clone https://github.com/Rui-Huang-dotcom/codex-reset-reminder.git
cd codex-reset-reminder
./install.sh
```

安装后会创建 macOS `launchd` 定时任务，每天检查一次。

安装时 macOS 可能会提示 `Background Items Added`，这是正常现象，因为工具需要在本机后台每天检查一次。

### 手动查看

```bash
codex-reset-reminder --print-summary
```

如果提示找不到命令，可以使用完整路径：

```bash
~/.local/bin/codex-reset-reminder --print-summary
```

输出只包含可用数量和到期时间。

### 测试通知

想截图展示通知效果，可以立刻发送一条测试通知：

```bash
codex-reset-reminder --test-notification
```

如果提示找不到命令，可以使用完整路径：

```bash
~/.local/bin/codex-reset-reminder --test-notification
```

测试命令会同时触发系统通知和一个 macOS 对话框，方便确认安装成功和截图展示。

### 提醒规则

每个可用 reset credit 到期前会提醒：

- 3 天内
- 24 小时内
- 6 小时内

同一个 reset credit 的同一个阈值只提醒一次。

### 卸载

```bash
./uninstall.sh
```

### 要求

- macOS
- 已登录 Codex，本机存在 `~/.codex/auth.json`
- 系统可访问 `chatgpt.com`
- 系统有 `python3` 和 `curl`

## English

### What It Does

`codex-reset-reminder` is a small local macOS utility for Codex reset credits.

It checks your reset credit expiry dates from your own local Codex auth state and sends a macOS reminder before available credits expire.

### Security

- Tokens are never uploaded.
- Account data is not collected.
- `access_token`, `refresh_token`, cookies, and full unique IDs are never printed.
- Requests are sent only from your machine to `https://chatgpt.com/backend-api/wham/rate-limit-reset-credits`.
- Reminder state is stored locally at `~/.codex/reset-credit-reminder-state.json`.

### Install

One-line install:

```bash
curl -fsSL https://raw.githubusercontent.com/Rui-Huang-dotcom/codex-reset-reminder/main/install.sh | bash
```

Or clone and install:

```bash
git clone https://github.com/Rui-Huang-dotcom/codex-reset-reminder.git
cd codex-reset-reminder
./install.sh
```

The installer creates a macOS `launchd` job that checks once per day.

macOS may show a `Background Items Added` notification during installation. This is expected because the tool runs a local daily background check.

### Manual Check

```bash
codex-reset-reminder --print-summary
```

If the command is not found, use the full path:

```bash
~/.local/bin/codex-reset-reminder --print-summary
```

The output only includes the available count and expiry times.

### Test Notification

```bash
codex-reset-reminder --test-notification
```

If the command is not found, use the full path:

```bash
~/.local/bin/codex-reset-reminder --test-notification
```

The test command sends a system notification and opens a macOS dialog so you can confirm the install worked.

### Reminder Rules

Each available reset credit is checked against these thresholds:

- Within 3 days
- Within 24 hours
- Within 6 hours

Each threshold is notified only once per reset credit.

### Uninstall

```bash
./uninstall.sh
```

### Requirements

- macOS
- Codex already logged in, with `~/.codex/auth.json` available
- Network access to `chatgpt.com`
- `python3` and `curl`
