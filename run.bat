@echo off
title F-SOCIETY MEDIA CENTER - LAUNCHER
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*