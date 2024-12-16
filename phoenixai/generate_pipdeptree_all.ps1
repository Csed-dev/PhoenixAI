param(
    [string]$BaseDir,
    [string]$PipPath,
    [string]$PythonPath
)

$projects = Get-ChildItem -Path $BaseDir -Directory

foreach ($project in $projects) {
    $projectPath = $project.FullName
    Write-Host "Processing project: $projectPath..."
    $requirementsPath = Join-Path $projectPath 'requirements.txt'

    if (-not (Test-Path $requirementsPath)) {
        Write-Host "No requirements.txt found in $projectPath. Generating it with pip list..."
        Set-Location -Path $projectPath
        & $PipPath list --format=freeze > requirements.txt
        Write-Host "requirements.txt generated for $projectPath."
    }

    Write-Host "Generating pip dependency tree for $projectPath..."
    Set-Location -Path $projectPath
    & $PythonPath -m pipdeptree --graph-output svg > dependencies.svg
    Write-Host "Dependency tree generated for $projectPath as dependencies.svg."
}
