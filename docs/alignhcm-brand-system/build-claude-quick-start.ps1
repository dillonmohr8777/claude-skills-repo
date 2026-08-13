param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot 'dist')
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$templatePath = Join-Path $repoRoot 'skills\alignhcm-brand-system\assets\templates\Align-HCM-Primary-Deck-Reference.pptx'
$pptxPath = Join-Path $OutputDirectory 'Align-HCM-Claude-Skill-Quick-Start.pptx'
$pdfPath = Join-Path $OutputDirectory 'Align-HCM-Claude-Skill-Quick-Start.pdf'
$renderDirectory = Join-Path $OutputDirectory 'rendered-slides'

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
New-Item -ItemType Directory -Force -Path $renderDirectory | Out-Null
Copy-Item -LiteralPath $templatePath -Destination $pptxPath -Force

function Get-ShapeByName {
    param($Slide, [string]$Name)
    foreach ($shape in $Slide.Shapes) {
        if ($shape.Name -eq $Name) { return $shape }
    }
    throw "Shape '$Name' was not found on slide $($Slide.SlideIndex)."
}

function Set-ShapeText {
    param(
        $Slide,
        [string]$Name,
        [string]$Text,
        [Nullable[double]]$FontSize = $null,
        [string]$FontName = $null
    )
    $shape = Get-ShapeByName -Slide $Slide -Name $Name
    $shape.TextFrame.TextRange.Text = $Text
    if ($null -ne $FontSize) { $shape.TextFrame.TextRange.Font.Size = [single]$FontSize }
    if ($FontName) { $shape.TextFrame.TextRange.Font.Name = $FontName }
    $shape.TextFrame.AutoSize = 0
    return $shape
}

function Set-Card {
    param(
        $Slide,
        [string]$HeadingShape,
        [string]$BodyShape,
        [string]$Heading,
        [string]$Body,
        [switch]$Code
    )
    Set-ShapeText -Slide $Slide -Name $HeadingShape -Text $Heading -FontSize 17 | Out-Null
    $font = if ($Code) { 'Consolas' } else { 'Calibri' }
    $size = if ($Code) { 12.5 } else { 13.5 }
    Set-ShapeText -Slide $Slide -Name $BodyShape -Text $Body -FontSize $size -FontName $font | Out-Null
}

function Set-Footer {
    param($Slide, [int]$Number)
    if ($Slide.SlideIndex -eq 1) {
        Set-ShapeText -Slide $Slide -Name 'TextBox 13' -Text 'Copyright 2026 AlignHCM  |  Confidential' | Out-Null
        Set-ShapeText -Slide $Slide -Name 'TextBox 14' -Text ('Align HCM   |   {0:d2}' -f $Number) | Out-Null
        return
    }
    foreach ($shape in $Slide.Shapes) {
        if ($shape.Name -eq 'FooterMid') {
            $shape.TextFrame.TextRange.Text = 'Copyright 2026 AlignHCM  |  Confidential'
        }
        if ($shape.Name -eq 'FooterRight') {
            $shape.TextFrame.TextRange.Text = ('Align HCM   |   {0:d2}' -f $Number)
        }
    }
}

$powerPoint = New-Object -ComObject PowerPoint.Application
try {
    $presentation = $powerPoint.Presentations.Open($pptxPath, $false, $false, $false)

    # Keep the exact cover, executive-summary card system, focal-proof page,
    # and close page. Remove sample-content layouts that are not needed here.
    foreach ($index in @(6, 4, 3)) { $presentation.Slides.Item($index).Delete() }

    $cover = $presentation.Slides.Item(1)
    $overview = $presentation.Slides.Item(2)
    $invoke = $presentation.Slides.Item(3)
    $close = $presentation.Slides.Item(4)

    # Cover
    Set-ShapeText -Slide $cover -Name 'TextBox 5' -Text 'ALIGN HCM BRAND SYSTEM' -FontSize 12 | Out-Null
    Set-ShapeText -Slide $cover -Name 'TextBox 6' -Text 'Claude Code Quick Start' -FontSize 30 | Out-Null
    Set-ShapeText -Slide $cover -Name 'TextBox 7' -Text 'Install once. Invoke whenever exact Align output is required.' -FontSize 16 | Out-Null
    Set-ShapeText -Slide $cover -Name 'TextBox 9' -Text 'ORGANIZATION EDITION  |  AUGUST 2026' -FontSize 10 | Out-Null
    Set-ShapeText -Slide $cover -Name 'TextBox 10' -Text 'FOR INTERNAL USE' -FontSize 10 | Out-Null
    (Get-ShapeByName -Slide $cover -Name 'CLIENT_LOGO').Delete()
    $label = $cover.Shapes.AddTextbox(1, 8839184 / 12700, 3163824 / 12700, 2651760 / 12700, 912070 / 12700)
    $label.Name = 'OrganizationGuideLabel'
    $label.TextFrame.TextRange.Text = "CLAUDE CODE`rORGANIZATION GUIDE"
    $label.TextFrame.TextRange.Font.Name = 'Calibri'
    $label.TextFrame.TextRange.Font.Size = 18
    $label.TextFrame.TextRange.Font.Bold = -1
    $label.TextFrame.TextRange.Font.Color.RGB = 16777215
    $label.TextFrame.TextRange.ParagraphFormat.Alignment = 2
    $label.TextFrame.VerticalAnchor = 3
    $label.TextFrame.AutoSize = 0

    # Overview
    Set-ShapeText -Slide $overview -Name 'Eyebrow' -Text 'ONE SKILL  |  EVERY ALIGN SURFACE' | Out-Null
    Set-ShapeText -Slide $overview -Name 'Title' -Text 'What Claude Gets Right Every Time' | Out-Null
    Set-ShapeText -Slide $overview -Name 'Subtitle' -Text 'The plugin carries the approved assets, exact deck reference, surface tokens, and validation rules with it.' -FontSize 17 | Out-Null
    Set-Card $overview 'TextBox 9' 'TextBox 10' 'Exact Align deck system' 'Starts from the bundled privacy-scrubbed master. Preserves the approved geometry, navy, orange, typography, footer rhythm, and Align artwork.'
    Set-Card $overview 'TextBox 14' 'TextBox 15' 'Verified client co-branding' 'Resolves the client from the current brief, uses a verified logo, preserves its aspect ratio, and places it in the approved cover zone.'
    Set-Card $overview 'TextBox 19' 'TextBox 20' 'Surface-specific brand rules' 'Routes decks, documents, web, editorial, social, and motion work to the correct palette and production guidance.'
    Set-Card $overview 'TextBox 24' 'TextBox 25' 'Validation before delivery' 'Checks the exact Align logo, client logo fidelity, placeholders, colors, geometry, contrast, overflow, and final rendered output.'

    # Installation page, duplicated from the approved four-card archetype.
    $installRange = $overview.Duplicate()
    $installRange.MoveTo(3)
    $install = $presentation.Slides.Item(3)
    Set-ShapeText -Slide $install -Name 'Eyebrow' -Text 'ADMIN SETUP  |  RUN ONCE' | Out-Null
    Set-ShapeText -Slide $install -Name 'Title' -Text 'Install It in Claude Code' | Out-Null
    Set-ShapeText -Slide $install -Name 'Subtitle' -Text 'PR #22 must be merged before the organization uses the main-branch commands below.' -FontSize 17 | Out-Null
    Set-Card $install 'TextBox 9' 'TextBox 10' '1  Add the marketplace' "/plugin marketplace add`rhttps://github.com/dillonmohr8777/`rclaude-skills-repo.git" -Code
    Set-Card $install 'TextBox 14' 'TextBox 15' '2  Install the plugin' "/plugin install alignhcm-brand-system@alignhcm-tools" -Code
    Set-Card $install 'TextBox 19' 'TextBox 20' '3  Reload Claude Code' '/reload-plugins' -Code
    Set-Card $install 'TextBox 24' 'TextBox 25' '4  Confirm availability' "Type / and search for:`ralignhcm-brand-system" -Code

    # Invocation page
    $invoke = $presentation.Slides.Item(4)
    Set-ShapeText -Slide $invoke -Name 'Eyebrow' -Text 'USE IN CLAUDE CODE' | Out-Null
    Set-ShapeText -Slide $invoke -Name 'Title' -Text 'Invoke the Skill Directly' | Out-Null
    Set-ShapeText -Slide $invoke -Name 'Subtitle' -Text 'Add the job after the command. Attach the current brief, approved source material, and client logo when available.' -FontSize 17 | Out-Null
    Set-ShapeText -Slide $invoke -Name 'TextBox 7' -Text "/alignhcm-brand-system:`ralignhcm-brand-system" -FontSize 24 -FontName 'Consolas' | Out-Null
    Set-ShapeText -Slide $invoke -Name 'TextBox 8' -Text 'The direct Claude Code command' -FontSize 14 | Out-Null
    Set-ShapeText -Slide $invoke -Name 'TextBox 9' -Text "Example: Create an Align HCM proposal deck for Northwind using the attached brief and verified logo. Return PPTX and PDF." -FontSize 11 | Out-Null
    Set-ShapeText -Slide $invoke -Name 'TextBox 13' -Text 'Claude can also load it automatically' -FontSize 17 | Out-Null
    Set-ShapeText -Slide $invoke -Name 'TextBox 14' -Text 'Ask for an Align HCM or SmartCare deck, proposal, report, one-pager, HubSpot page, social graphic, carousel, video, or brand review. Direct invocation is best when brand fidelity is critical.' -FontSize 13.5 | Out-Null
    Set-ShapeText -Slide $invoke -Name 'TextBox 18' -Text 'Always provide current source material' -FontSize 16 | Out-Null
    Set-ShapeText -Slide $invoke -Name 'TextBox 19' -Text 'Claude will not guess the client, reuse sample pricing, redraw a logo, or carry old engagement facts forward. If identity, provenance, or approved copy is ambiguous, the skill stops before production.' -FontSize 13.5 | Out-Null

    # Delivery gate page
    $gateRange = $overview.Duplicate()
    $gateRange.MoveTo(5)
    $gate = $presentation.Slides.Item(5)
    Set-ShapeText -Slide $gate -Name 'Eyebrow' -Text 'WHAT TO EXPECT' | Out-Null
    Set-ShapeText -Slide $gate -Name 'Title' -Text "Claude's Delivery Gate" | Out-Null
    Set-ShapeText -Slide $gate -Name 'Subtitle' -Text 'A valid invocation produces reviewable work, not a generic template or an unverified brand approximation.' -FontSize 17 | Out-Null
    Set-Card $gate 'TextBox 9' 'TextBox 10' '1  Resolve the assignment' 'Claude states the client, engagement, audience, output surface, date, and source evidence before production.'
    Set-Card $gate 'TextBox 14' 'TextBox 15' '2  Use approved assets' 'The exact Align artwork stays unchanged. Client logos come from an attached approved asset, canonical project folder, official brand kit, or official website.'
    Set-Card $gate 'TextBox 19' 'TextBox 20' '3  Build in the right system' 'Decks clone designed slides. Other surfaces use their own approved palette, typography, layout, imagery, and copy rules.'
    Set-Card $gate 'TextBox 24' 'TextBox 25' '4  Validate the final file' 'Claude runs the surface linter, checks the editable source, renders the output, and reviews logo fidelity, contrast, overflow, and sample residue.'
    (Get-ShapeByName -Slide $gate -Name 'TextBox 25').Height = 64

    # Close
    $close = $presentation.Slides.Item(6)
    Set-ShapeText -Slide $close -Name 'TextBox 5' -Text 'READY TO USE' | Out-Null
    Set-ShapeText -Slide $close -Name 'TextBox 6' -Text 'Start with a clear brief.' -FontSize 30 | Out-Null
    Set-ShapeText -Slide $close -Name 'TextBox 10' -Text '/alignhcm-brand-system:alignhcm-brand-system' -FontSize 14 -FontName 'Consolas' | Out-Null
    Set-ShapeText -Slide $close -Name 'TextBox 11' -Text 'Invoke the approved Claude skill' -FontSize 13 | Out-Null
    Set-ShapeText -Slide $close -Name 'TextBox 14' -Text 'github.com/dillonmohr8777/claude-skills-repo/pull/22' -FontSize 13 | Out-Null
    Set-ShapeText -Slide $close -Name 'TextBox 17' -Text 'Attach the brief, source material, and verified client logo' -FontSize 13 | Out-Null
    Set-ShapeText -Slide $close -Name 'TextBox 18' -Text 'alignhcm.com' | Out-Null

    for ($i = 1; $i -le $presentation.Slides.Count; $i++) {
        Set-Footer -Slide $presentation.Slides.Item($i) -Number $i
    }
    Set-ShapeText -Slide $close -Name 'TextBox 19' -Text ('Copyright 2026 AlignHCM  |  Confidential  |  {0:d2}' -f $presentation.Slides.Count) | Out-Null

    $presentation.Save()
    $presentation.SaveCopyAs($pdfPath, 32)
    $presentation.Export($renderDirectory, 'PNG', 1280, 720)
    $presentation.Close()
}
finally {
    $powerPoint.Quit()
    [Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint) | Out-Null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

Write-Output $pptxPath
Write-Output $pdfPath
Write-Output $renderDirectory
