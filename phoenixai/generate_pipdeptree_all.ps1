###############################################################################
# generate_pipdeptree_all.ps1
###############################################################################
param(
    [string]$BaseDir,
    [string]$SingleProject
)

Write-Host "BaseDir: $BaseDir"

# Decide if we process a single project or all subfolders
if ($SingleProject) {
    $target = Join-Path $BaseDir $SingleProject
    if (!(Test-Path $target)) {
        Write-Host "Error: $SingleProject not found under $BaseDir"
        exit 1
    }
    $projects = @(Get-Item -Path $target)
    Write-Host "Processing single project folder: $target"
} 
else {
    $projects = Get-ChildItem -Path $BaseDir -Directory
    Write-Host "Processing all projects in $BaseDir..."
}

function Ensure-Packages {
    param(
        [string]$pipPath,
        [string[]]$packages
    )
    foreach ($pkg in $packages) {
        # Attempt 'pip show <package>' to see if installed
        $null = & $pipPath show $pkg 2>$null
        if (-not $?) {
            Write-Host "Installing package '$pkg'..."
            & $pipPath install $pkg
        }
    }
}

foreach ($project in $projects) {
    $projectPath = $project.FullName
    Write-Host "`n---------------------------------------------------------------"
    Write-Host "Processing project: $projectPath"

    # Paths to .venv python & pip
    $pipPath    = Join-Path $projectPath '.venv\Scripts\pip.exe'
    $pythonPath = Join-Path $projectPath '.venv\Scripts\python.exe'

    # 1. Ensure local venv packages
    if (Test-Path $pipPath) {
        Write-Host "Ensuring pipdeptree, pytest, and coverage are installed..."
        Ensure-Packages -pipPath $pipPath -packages @('pipdeptree','pytest','coverage')
    }
    else {
        Write-Host "[WARNING] No local .venv found at: $pipPath. Skipping package checks."
    }

    # 2. Check for tests
    $testSh   = Join-Path $projectPath 'test.sh'
    $makeFile = Join-Path $projectPath 'Makefile'

    if (Test-Path $testSh) {
        Write-Host "[INFO] Running test.sh..."
        Push-Location $projectPath
        bash .\test.sh
        Pop-Location
    }
    elseif ((Test-Path $makeFile) -and 
            (Select-String -Path $makeFile -Pattern '^test:' -Quiet)) {
        Write-Host "[INFO] Found Makefile with 'test' target → Running make test..."
        Push-Location $projectPath
        make test
        Pop-Location
    }
    else {
        # Check for test_*.py
        $pytestFiles = Get-ChildItem $projectPath -File -Include 'test_*.py','tests_*.py', '*_test.py','*_tests.py','Tests.py', 'Test.py' -ErrorAction SilentlyContinue
        if ($pytestFiles) {
            if (Test-Path $pythonPath) {
                Write-Host "[INFO] Found Python test files → Running coverage+pytest..."
                Push-Location $projectPath
                & $pythonPath -m coverage run -m pytest
                & $pythonPath -m coverage report
                Pop-Location
            }
            else {
                Write-Host "[WARNING] No .venv python.exe found to run tests. Skipping..."
            }
        }
        else {
            Write-Host "[INFO] No recognized test system. Skipping tests."
        }
    }

    # 3. Ensure requirements.txt
    $requirementsPath = Join-Path $projectPath 'requirements.txt'
    if (-not (Test-Path $requirementsPath)) {
        if (Test-Path $pipPath) {
            Write-Host "[INFO] Creating requirements.txt via 'pip list'..."
            Push-Location $projectPath
            & $pipPath list --format=freeze > requirements.txt
            Pop-Location
        }
        else {
            Write-Host "[WARNING] No .venv pip found. Cannot create requirements.txt."
        }
    }

    # 4. Generate dependencies.svg with pipdeptree
    if (Test-Path $pythonPath) {
        Write-Host "[INFO] Generating pipdeptree → dependencies.svg..."
        Push-Location $projectPath
        & $pythonPath -m pipdeptree --graph-output svg > dependencies.svg
        Pop-Location
        Write-Host "[INFO] dependencies.svg created in $projectPath."
    }
    else {
        Write-Host "[WARNING] No .venv python.exe found. Skipping pipdeptree generation."
    }
} # end foreach
