# PowerShell script to start all Nero AI Services
# Starts LiveKit Server, Backend Agent, and Frontend in parallel

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🎙️ Nero AI Services Platform" -ForegroundColor Cyan
Write-Host "  Starting All Services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if livekit-server is installed
if (-not (Get-Command livekit-server -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: livekit-server is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install it using one of the following methods:" -ForegroundColor Yellow
    Write-Host "  1. Using scoop: scoop install livekit-server" -ForegroundColor Yellow
    Write-Host "  2. Using chocolatey: choco install livekit" -ForegroundColor Yellow
    Write-Host "  3. Download from: https://github.com/livekit/livekit/releases" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if uv is available
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: uv is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install it using: winget install --id=astral-sh.uv -e" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if pnpm is available
if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: pnpm is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install it using: npm install -g pnpm" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if .env.local exists in backend
if (-not (Test-Path "backend\.env.local")) {
    Write-Host "❌ Error: backend\.env.local file not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create backend\.env.local with your API keys:" -ForegroundColor Yellow
    Write-Host "  MURF_API_KEY=your_murf_api_key" -ForegroundColor Yellow
    Write-Host "  GOOGLE_API_KEY=your_google_api_key" -ForegroundColor Yellow
    Write-Host "  DEEPGRAM_API_KEY=your_deepgram_api_key" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Create job tracking variables
$jobs = @()
$script:shouldStop = $false

# Handle Ctrl+C gracefully
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    $script:shouldStop = $true
}

try {
    Write-Host "🚀 Starting LiveKit Server..." -ForegroundColor Cyan
    $livekitJob = Start-Job -ScriptBlock {
        livekit-server --dev
    }
    $jobs += $livekitJob
    Write-Host "✅ LiveKit Server started (Job ID: $($livekitJob.Id))" -ForegroundColor Green

    # Give LiveKit server a moment to start
    Start-Sleep -Seconds 3

    Write-Host ""
    Write-Host "🤖 Starting Backend Agent (multi_agent.py)..." -ForegroundColor Cyan
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PSScriptRoot
        Set-Location "backend"
        uv run python src/multi_agent.py dev
    }
    $jobs += $backendJob
    Write-Host "✅ Backend Agent started (Job ID: $($backendJob.Id))" -ForegroundColor Green

    # Give backend a moment to start
    Start-Sleep -Seconds 3

    Write-Host ""
    Write-Host "🌐 Starting Frontend..." -ForegroundColor Cyan
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PSScriptRoot
        Set-Location "frontend"
        pnpm dev
    }
    $jobs += $frontendJob
    Write-Host "✅ Frontend started (Job ID: $($frontendJob.Id))" -ForegroundColor Green

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✨ All Services Running!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📡 LiveKit Server:  ws://127.0.0.1:7880" -ForegroundColor Yellow
    Write-Host "🤖 Backend Agent:   Connected and listening" -ForegroundColor Yellow
    Write-Host "🌐 Frontend:        http://localhost:3000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available Services:" -ForegroundColor Cyan
    Write-Host "  💬 General Chat" -ForegroundColor White
    Write-Host "  ☕ Coffee Ordering" -ForegroundColor White
    Write-Host "  🧘 Wellness Check-in" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Magenta
    Write-Host ""

    # Monitor jobs and display output
    $lastOutputCheck = Get-Date
    while (-not $script:shouldStop) {
        foreach ($job in $jobs) {
            # Check if any job failed
            if ($job.State -eq "Failed") {
                Write-Host ""
                Write-Host "❌ Job $($job.Id) failed!" -ForegroundColor Red
                $error = Receive-Job -Job $job -ErrorAction SilentlyContinue
                if ($error) {
                    Write-Host $error -ForegroundColor Red
                }
                throw "Service failed to start"
            }

            # Periodically check for output (every 2 seconds to avoid spam)
            if (((Get-Date) - $lastOutputCheck).TotalSeconds -gt 2) {
                $output = Receive-Job -Job $job -ErrorAction SilentlyContinue
                if ($output) {
                    Write-Host $output
                }
            }
        }
        
        if (((Get-Date) - $lastOutputCheck).TotalSeconds -gt 2) {
            $lastOutputCheck = Get-Date
        }
        
        Start-Sleep -Milliseconds 500
    }
}
catch {
    Write-Host ""
    Write-Host "⚠️  Shutting down services..." -ForegroundColor Yellow
}
finally {
    Write-Host ""
    # Clean up jobs
    foreach ($job in $jobs) {
        if ($job.State -eq "Running") {
            Write-Host "🛑 Stopping Job $($job.Id)..." -ForegroundColor Yellow
            Stop-Job -Job $job -Force
            Remove-Job -Job $job -Force
        }
    }
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  👋 All services stopped." -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}
