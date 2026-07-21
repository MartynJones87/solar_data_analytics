# Data Pipeline Orchestration Script
# Purpose: Run data collection followed by dbt build
# Usage: .\run-pipeline.ps1

# Set error handling - stop on first error
$ErrorActionPreference = "Stop"

# Define workspace root
$workspaceRoot = $PSScriptRoot

# Variable to store appium job
$appiumJob = $null

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Data Pipeline Orchestration" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 0: Start appium in background
Write-Host "Step 0: Starting appium server in background..." -ForegroundColor Yellow
try {
    $appiumJob = Start-Job -ScriptBlock { appium }
    Write-Host "✓ Appium server started (Job ID: $($appiumJob.Id))" -ForegroundColor Green
    
    Write-Host "Waiting 30 seconds for appium to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    Write-Host "✓ Ready to proceed with pipeline" -ForegroundColor Green
}
catch {
    Write-Host "✗ Failed to start appium server" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 1: Activate virtual environment
Write-Host "Step 1: Activating virtual environment..." -ForegroundColor Yellow
& "$workspaceRoot\.venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

Write-Host ""

# Wrap remaining pipeline in try-finally to ensure appium cleanup
try {
    # Step 2: Run data collection
    Write-Host "Step 2: Running data collection (main.py collect-data)..." -ForegroundColor Yellow
    try {
        & python main.py collect-data
        $collectExitCode = $LASTEXITCODE
        
        if ($collectExitCode -ne 0) {
            Write-Host "✗ Data collection failed with exit code $collectExitCode" -ForegroundColor Red
            exit $collectExitCode
        }
        Write-Host "✓ Data collection completed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to run data collection" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }

    Write-Host ""

    # Step 3: Run dbt build
    Write-Host "Step 3: Running dbt build in data_warehouse..." -ForegroundColor Yellow
    try {
        Push-Location "$workspaceRoot\data_warehouse"
        & dbt build
        $dbtExitCode = $LASTEXITCODE
        Pop-Location
        
        if ($dbtExitCode -ne 0) {
            Write-Host "✗ dbt build failed with exit code $dbtExitCode" -ForegroundColor Red
            exit $dbtExitCode
        }
        Write-Host "✓ dbt build completed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to run dbt build" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Pop-Location
        exit 1
    }

    # Step 4: Copy .json and .png files to OneDrive target, skipping existing files
    Write-Host "" 
    Write-Host "Step 4: Syncing .json and .png files to OneDrive target..." -ForegroundColor Yellow
    try {
        $sourcePath = Join-Path $workspaceRoot 'data\solar_data'
        $targetPath = 'C:\Users\marty\OneDrive\Code\british_gas_usage\solar_data'

        if (-not (Test-Path $sourcePath)) {
            Write-Host "Source path not found: $sourcePath" -ForegroundColor Yellow
        }
        else {
            Get-ChildItem -Path $sourcePath -Recurse -Include *.json,*.png -File | ForEach-Object {
                $relative = $_.FullName.Substring($sourcePath.Length).TrimStart('\','/')
                $dest = Join-Path $targetPath $relative
                $destDir = Split-Path $dest -Parent

                if (-not (Test-Path $dest)) {
                    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Force -Path $destDir | Out-Null }
                    Copy-Item -Path $_.FullName -Destination $dest -Force
                    Write-Host "Copied: $relative" -ForegroundColor Green
                }
                else {
                    Write-Host "Skipping existing: $relative" -ForegroundColor DarkGray
                }
            }
        }
    }
    catch {
        Write-Host "✗ Failed during file sync" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "Pipeline execution completed successfully!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
}
finally {
    # Cleanup: Stop appium server
    if ($appiumJob) {
        Write-Host ""
        Write-Host "Stopping appium server..." -ForegroundColor Yellow
        Stop-Job -Job $appiumJob
        Remove-Job -Job $appiumJob
        Write-Host "✓ Appium server stopped" -ForegroundColor Green
    }
}
