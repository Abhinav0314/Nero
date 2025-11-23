# Start all services for the Coffee Shop Barista Voice Agent
# Run this script from the project root directory

Write-Host "🚀 Starting Coffee Shop Barista Voice Agent..." -ForegroundColor Cyan
Write-Host ""

# Check if livekit-server is installed
if (-not (Get-Command livekit-server -ErrorAction SilentlyContinue)) {
    Write-Host "❌ livekit-server not found!" -ForegroundColor Red
    Write-Host "Please install it first:" -ForegroundColor Yellow
    Write-Host "  - macOS: brew install livekit" -ForegroundColor Yellow
    Write-Host "  - Windows: Download from https://github.com/livekit/livekit/releases" -ForegroundColor Yellow
    exit 1
}

# Check if API keys are configured
$envFile = "backend\.env.local"
if (-not (Test-Path $envFile)) {
    Write-Host "❌ Backend .env.local not found!" -ForegroundColor Red
    Write-Host "Please run setup first or configure API keys manually." -ForegroundColor Yellow
    exit 1
}

$content = Get-Content $envFile -Raw
if ($content -match "your_murf_api_key_here" -or $content -match "your_google_api_key_here") {
    Write-Host "⚠️  WARNING: API keys not configured!" -ForegroundColor Yellow
    Write-Host "Please edit backend\.env.local and add your real API keys:" -ForegroundColor Yellow
    Write-Host "  - MURF_API_KEY" -ForegroundColor Yellow
    Write-Host "  - GOOGLE_API_KEY" -ForegroundColor Yellow
    Write-Host "  - DEEPGRAM_API_KEY" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 0
    }
}

Write-Host "📦 Starting LiveKit Server..." -ForegroundColor Green
$livekitJob = Start-Process -FilePath "livekit-server" -ArgumentList "--dev" -PassThru -NoNewWindow

Start-Sleep -Seconds 2

Write-Host "🤖 Starting Backend Agent..." -ForegroundColor Green
$backendJob = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd backend; uv run python src/agent.py dev" -PassThru

Start-Sleep -Seconds 2

Write-Host "🌐 Starting Frontend..." -ForegroundColor Green
$frontendJob = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd frontend; pnpm dev" -PassThru

Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Wait for frontend to start (about 10-20 seconds)" -ForegroundColor White
Write-Host "  2. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "  3. Click 'Start ordering' and talk to the barista!" -ForegroundColor White
Write-Host "  4. Orders will be saved to backend\orders\" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services..." -ForegroundColor Gray

# Wait for user to stop
try {
    Wait-Process -Id $livekitJob.Id, $backendJob.Id, $frontendJob.Id
} finally {
    Write-Host ""
    Write-Host "🛑 Stopping all services..." -ForegroundColor Red
    Stop-Process -Id $livekitJob.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $backendJob.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendJob.Id -ErrorAction SilentlyContinue
    Write-Host "✅ All services stopped." -ForegroundColor Green
}
