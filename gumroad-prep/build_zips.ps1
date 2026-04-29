<#
.SYNOPSIS
    Build the Gumroad-ready zip files from the marketing-skills-store source tree.

.DESCRIPTION
    PowerShell port of build_zips.sh. Run from any directory; paths resolve from
    the script location. Produces the same dist/ tree the bash version produces.

    Output: marketing-skills-store/gumroad-prep/dist/
      - bundle-01-paid-search-operator.zip
      - bundle-02-real-estate-lending.zip
      - bundle-03-hubspot-operator.zip
      - bundle-04-seo-authority-builder.zip
      - bundle-05-multi-market-paid-social.zip
      - bundle-06-conversion-analytics.zip
      - mega-pack-all-30-skills.zip
      - individual/<skill-name>.zip   (30 individual skill zips)

    Each zip contains the skill folder(s), INSTALL.md, ABOUT-THE-AUTHOR.md,
    LICENSE.md, and the matching sales page as README.md.

.NOTES
    Requires PowerShell 5.1+ (Compress-Archive is built in). No external tools.
#>

$ErrorActionPreference = "Stop"

$Root   = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Dist   = Join-Path $Root "gumroad-prep\dist"
$Skills = Join-Path $Root "skills"
$Shared = Join-Path $Root "shared"
$Sales  = Join-Path $Root "sales-pages"

if (Test-Path $Dist) { Remove-Item $Dist -Recurse -Force }
New-Item -ItemType Directory -Path (Join-Path $Dist "individual") -Force | Out-Null

function Copy-SharedDocs($Target) {
    Copy-Item (Join-Path $Shared "INSTALL.md")          (Join-Path $Target "INSTALL.md")          -Force
    Copy-Item (Join-Path $Shared "ABOUT-THE-AUTHOR.md") (Join-Path $Target "ABOUT-THE-AUTHOR.md") -Force
    Copy-Item (Join-Path $Shared "LICENSE.md")          (Join-Path $Target "LICENSE.md")          -Force
}

# --- Bundle zips ---
Get-ChildItem -Path $Skills -Directory -Filter "bundle-*" | ForEach-Object {
    $BundleDir = $_.FullName
    $BundleId  = $_.Name
    $SalesPage = Join-Path $Sales "$BundleId.md"
    if (-not (Test-Path $SalesPage)) {
        Write-Host "SKIP: missing sales page for $BundleId" -ForegroundColor Yellow
        return
    }
    Write-Host "Building zip for $BundleId..."
    $Staging = Join-Path $Dist $BundleId
    New-Item -ItemType Directory -Path (Join-Path $Staging "skills") -Force | Out-Null
    Copy-Item (Join-Path $BundleDir "*") (Join-Path $Staging "skills") -Recurse -Force
    Copy-SharedDocs $Staging
    Copy-Item $SalesPage (Join-Path $Staging "README.md") -Force
    Compress-Archive -Path $Staging -DestinationPath (Join-Path $Dist "$BundleId.zip") -Force
    Remove-Item $Staging -Recurse -Force
}

# --- Mega-pack zip (all 30) ---
Write-Host "Building mega-pack zip..."
$Mega = Join-Path $Dist "mega-pack-all-30-skills"
New-Item -ItemType Directory -Path (Join-Path $Mega "skills") -Force | Out-Null
Get-ChildItem -Path $Skills -Directory -Filter "bundle-*" | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $Mega "skills") -Recurse -Force
}
Copy-SharedDocs $Mega
Copy-Item (Join-Path $Sales "mega-pack.md") (Join-Path $Mega "README.md") -Force
Compress-Archive -Path $Mega -DestinationPath (Join-Path $Dist "mega-pack-all-30-skills.zip") -Force
Remove-Item $Mega -Recurse -Force

# --- Individual skill zips (30) ---
Write-Host "Building 30 individual skill zips..."
Get-ChildItem -Path $Skills -Directory -Filter "bundle-*" | ForEach-Object {
    Get-ChildItem -Path $_.FullName -Directory | ForEach-Object {
        $SkillDir  = $_.FullName
        $SkillName = $_.Name
        $Staging   = Join-Path $Dist "individual\$SkillName"
        New-Item -ItemType Directory -Path $Staging -Force | Out-Null
        Copy-Item (Join-Path $SkillDir "*") $Staging -Recurse -Force
        Copy-SharedDocs $Staging
        Compress-Archive -Path $Staging -DestinationPath (Join-Path $Dist "individual\$SkillName.zip") -Force
        Remove-Item $Staging -Recurse -Force
    }
}

# --- Summary ---
Write-Host ""
Write-Host "Done. Output:"
Get-ChildItem -Path $Dist -Filter "*.zip" -File | ForEach-Object {
    $sizeKb = [math]::Round($_.Length / 1KB, 1)
    Write-Host ("  {0} ({1} KB)" -f $_.Name, $sizeKb)
}
$IndividualCount = (Get-ChildItem -Path (Join-Path $Dist "individual") -Filter "*.zip" -File).Count
Write-Host ""
Write-Host "Individual skill zips: $IndividualCount files in $Dist\individual\"
$Total = (Get-ChildItem -Path $Dist -Recurse -Filter "*.zip" -File).Count
Write-Host ""
Write-Host "Total zips ready for Gumroad: $Total" -ForegroundColor Green
