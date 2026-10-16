---
name: git-ssh-setup
description: Automated setup of SSH keys, GitHub SSH configuration, remote URL updates, and connection testing. Use when configuring git authentication over SSH or resolving permission denied push errors.
---

# Git SSH Setup & Authentication

## Overview
This skill provides automated guidance and procedures for setting up and verifying SSH-based authentication with GitHub, replacing HTTPS/password prompts or token hassles.

## Workflow

### 1. Check Existing SSH Keys
Check if an SSH key already exists in the user profile (`~/.ssh/`):
- `id_ed25519` / `id_ed25519.pub` (Recommended)
- `id_rsa` / `id_rsa.pub`

### 2. Generate New SSH Key (if none exists)
Run:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```
*(Press Enter to accept default file path and optionally set a passphrase).*

### 3. Start SSH Agent & Add Key
Ensure ssh-agent is running and add the private key:

- **Linux / macOS / Git Bash (Windows):**
  ```bash
  eval "$(ssh-agent -s)"
  ssh-add ~/.ssh/id_ed25519
  ```

- **Windows PowerShell (Administrator - Windows Service):**
  If using native Windows PowerShell and the OpenSSH Authentication Agent service is disabled:
  ```powershell
  Get-Service ssh-agent | Set-Service -StartupType Automatic
  Start-Service ssh-agent
  ssh-add $HOME\.ssh\id_ed25519
  ```

### 4. Test SSH Connection to GitHub
Verify authentication:
```bash
ssh -T git@github.com
```
*(Confirm fingerprint acceptance with `yes`).*

### 5. Update Git Remote URL
Switch repository from HTTPS to SSH:
```bash
git remote set-url origin git@github.com:<username>/<repository>.git
```
