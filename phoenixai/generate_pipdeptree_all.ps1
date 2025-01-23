param(
    [string]$BaseDir
)

$projects = Get-ChildItem -Path $BaseDir -Directory

foreach ($project in $projects) {
    $projectPath = $project.FullName
    Write-Host "Processing project: $projectPath..."

    $requirementsPath = Join-Path $projectPath 'requirements.txt'
    $pipPath = Join-Path $projectPath '.venv\Scripts\pip.exe'
    $pythonPath = Join-Path $projectPath '.venv\Scripts\python.exe'

    if (-not (Test-Path $requirementsPath)) {
        Write-Host "No requirements.txt found in $projectPath. Generating it with pip list..."
        Set-Location -Path $projectPath
        & "$pipPath" list --format=freeze > requirements.txt
        Write-Host "requirements.txt generated for $projectPath."
    }

    Write-Host "Generating pip dependency tree for $projectPath..."
    Set-Location -Path $projectPath
    & "$pythonPath" -m pipdeptree --graph-output svg > dependencies.svg
    Write-Host "Dependency tree generated for $projectPath as dependencies.svg."
}
