@echo off
REM GitHub Repository Setup Script for Windows
REM This script prepares the repository for pushing to GitHub

setlocal enabledelayedexpansion

echo.
echo 🚀 GitHub Repository Setup
echo ==================================
echo.

REM Check if git is installed
where git >nul 2>nul
if errorlevel 1 (
    echo ❌ Git is not installed. Please install Git for Windows first.
    echo Download: https://git-scm.com/download/win
    exit /b 1
)

REM Check if GitHub CLI is installed
where gh >nul 2>nul
set GH_INSTALLED=0
if errorlevel 0 set GH_INSTALLED=1

if %GH_INSTALLED% equ 0 (
    echo ⚠️  GitHub CLI not installed. You can still push using git commands.
    echo.
    echo Option 1: Install GitHub CLI (recommended)
    echo   Download: https://cli.github.com/
    echo.
)

REM Initialize git repo
if not exist ".git" (
    echo Initializing git repository...
    call git init
    call git branch -M main
    echo ✓ Git repository initialized
)

REM Add all files
echo Adding files to git...
call git add .
echo ✓ Files added

REM Create initial commit
echo Creating initial commit...
call git commit -m "feat: Real-time fraud detection with Kafka and Spark Streaming - Complete production-ready system with rules engine, streaming, tests, docs, and CI/CD"
echo ✓ Initial commit created
echo.

REM Setup remote
echo.
echo Setting up GitHub repository...
set /p GITHUB_USER="Enter your GitHub username: "

set REPO_URL=https://github.com/%GITHUB_USER%/real-time-fraud-detection-streaming.git

REM Check if remote already exists
for /f %%i in ('git remote get-url origin 2^>nul') do set EXISTING_REMOTE=%%i

if not "!EXISTING_REMOTE!"=="" (
    echo Remote already configured: !EXISTING_REMOTE!
) else (
    call git remote add origin %REPO_URL%
    echo ✓ Remote added: %REPO_URL%
)

REM Push to GitHub
echo.
echo Pushing to GitHub...
call git push -u origin main
if errorlevel 1 (
    echo.
    echo ⚠️  Push failed. Make sure:
    echo  1. Repository exists on GitHub
    echo  2. GitHub credentials are configured
    echo.
    echo To create the repository on GitHub:
    echo  1. Go to https://github.com/new
    echo  2. Name it: real-time-fraud-detection-streaming
    echo  3. Make it public
    echo  4. Do NOT initialize with README
    echo.
    echo Then retry: git push -u origin main
) else (
    echo ✓ Repository pushed!
    echo.
    echo ✅ Repository setup complete!
    echo.
    echo Next steps:
    echo 1. Go to: https://github.com/%GITHUB_USER%/real-time-fraud-detection-streaming
    echo 2. Add topics: kafka, spark, fraud-detection, streaming, python, kubernetes
    echo 3. Update your CV with the link
    echo.
)

pause
