<pre>
                      ███████╗███████╗██╗  ██╗██╗   ██╗ █████╗ ██╗   ██╗██╗  ████████╗
                      ██╔════╝██╔════╝██║  ██║██║   ██║██╔══██╗██║   ██║██║  ╚══██╔══╝
                      ███████╗███████╗███████║██║   ██║███████║██║   ██║██║     ██║ 
                      ╚════██║╚════██║██╔══██║██║   ██║██╔══██║██║   ██║██║     ██║
                      ███████║███████║██║  ██║╚██████╔╝██║  ██║╚██████╔╝███████╗██║
                      ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝
</pre>

<p align="center">
<img src="https://img.shields.io/badge/Encryption-AES--GCM-2ea44f?style=for-the-badge">
<img src="https://img.shields.io/badge/KDF-Argon2id-6f42c1?style=for-the-badge"> 
<img src="https://img.shields.io/badge/SSH-Paramiko-1f6feb?style=for-the-badge"> 
<img src="https://img.shields.io/badge/Storage-Local_Vault-d73a49?style=for-the-badge"> 
</p>

## Overview

**SSHVAULT** — это консольная утилита для безопасного хранения и управления SSH-доступами с локальным шифрованием и интерактивным shell-режимом. Проект ориентирован на персональное использование, лабораторные окружения и серверы, где требуется централизованное управление SSH-учётками без передачи секретов третьим сторонам.

## Key Features
- Client-side encryption (master password)
- Encrypted local vault
- Interactive shell mode (unlock once per session)
- SSH connections via Paramiko
- Add / edit / delete SSH credentials

## Installation
```bash
pipx install git+https://github.com/ratmist/sshvault.git
```

## Usage
### Initialize vault

```bash
sshvault init
```

### Add new service

```bash
sshvault add
```
You will be prompted for the following fields:
- service name
- host
- port
- username
- password
### Connect to service

```bash
sshvault connect <service_name>
```
Establishes an SSH connection using stored credentials.
### Edit service

```bash
sshvault edit <service_name>
```
Allows updating the username and/or password for an existing service.
### Interactive shell mode

```bash
sshvault shell
```
Unlocks the vault once and allows executing multiple commands within a single session.

## Security model

SSHVAULT is built around a **zero-knowledge** architecture:

- The master password is never stored
- Encryption keys are derived at runtime only
- Vault data is decrypted in memory only for the lifetime of the process
- Losing the master password results in permanent data loss (by design)

This behavior is intentional and explicitly documented.


## Cryptography

The following cryptographic primitives and libraries are used:

### Argon2id
Used for key derivation from the master password to resist brute-force and GPU-based attacks.

### AES-GCM
Used for encrypting the vault file, providing both confidentiality and integrity.

### Paramiko
Used for establishing SSH connections and interactive shell access from Python.

## Vault architecture
- Vault is stored locally in the user home directory:
```bash
~/.sshvault/
```
- Vault data is stored in encrypted binary form
- A unique salt is generated during initialization
- All cryptographic operations are performed locally
