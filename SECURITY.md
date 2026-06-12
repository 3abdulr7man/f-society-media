# Security Policy

## Supported Versions

We actively support security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| v1.0.x  | :white_check_mark: |
| < v1.0  | :x:                |

---

## Reporting a Vulnerability

We take the security of this project seriously. If you discover a vulnerability or have a security concern, please do not disclose it publicly via GitHub issues. Instead, report it privately:

1. Email a detailed description of the issue to **vulnerability@f-society.org**.
2. Include steps to reproduce the vulnerability (or a proof of concept).
3. We will acknowledge receipt of your report within 48 hours and work with you to fix and release a patched version quickly.

---

## Safe Usage Guidelines

- **Always inspect URLs**: The tool runs standard downloads using `yt-dlp`. Running arbitrary unverified URLs might pose minor privacy/traffic risks depending on target platforms.
- **FFmpeg path integrity**: The tool relies on calling `ffmpeg` binaries. Always ensure the `ffmpeg` binary on your system is downloaded from official channels to avoid executable hijacks.
- **Cookies file safety**: If you provide cookie files (e.g. Chrome/Firefox cookies import), keep them safe! The cookies file contains active session tokens. Do not commit it to version control.
