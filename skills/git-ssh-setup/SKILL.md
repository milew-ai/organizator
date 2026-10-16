---
name: git-ssh-setup
description: Set up GitHub authentication over SSH. Use when configuring an SSH key, fixing "permission denied" on git push, or switching a remote from HTTPS to SSH.
---

# Git SSH Setup

Manual checklist for GitHub over SSH. Do the steps in order. Skip a step only when its check already passes.

## 1. Check for an existing key

Look in the user profile (`~/.ssh/` on Linux and macOS, `%USERPROFILE%\.ssh\` on Windows) for:

- `id_ed25519` and `id_ed25519.pub` (preferred)
- `id_rsa` and `id_rsa.pub`

If a key pair is already there, do not generate another one. Continue from step 3 with that private key.

## 2. Generate a key

Only when no key exists. Default path is `~/.ssh/id_ed25519` (`%USERPROFILE%\.ssh\id_ed25519` on Windows).

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Press Enter to accept the default path. A passphrase is optional.

## 3. Load the key into ssh-agent

Linux, macOS, or Git Bash:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Windows PowerShell. Starting the OpenSSH Authentication Agent service needs an elevated shell:

```powershell
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

Use the private key path from step 1 or 2 if it is not `id_ed25519`.

## 4. Add the public key to GitHub

Print the public key and copy the whole line:

```bash
# Linux / macOS / Git Bash
cat ~/.ssh/id_ed25519.pub
```

```powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
```

In GitHub: Settings → SSH and GPG keys → New SSH key. Paste the `.pub` contents. Never upload the private key.

## 5. Test the connection

```bash
ssh -T git@github.com
```

On the first connection, confirm the host key with `yes` only after it matches GitHub's published fingerprint. Success looks like `Hi <username>! You've successfully authenticated`.

## 6. Point the remote at SSH

From the repository, only if `origin` is still HTTPS:

```bash
git remote set-url origin git@github.com:<username>/<repository>.git
git remote -v
```
