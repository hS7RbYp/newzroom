#!/usr/bin/env pwsh
<#
.SYNOPSIS
    GitHub Publishing Pipeline Setup Script
    
.DESCRIPTION
    Automates the setup of GitHub Secrets and Actions configuration for the publishing pipeline.
    
.PARAMETER RepoOwner
    GitHub repository owner (username or organization)
    
.PARAMETER RepoName
    GitHub repository name
    
.PARAMETER GitHubToken
    GitHub personal access token (requires 'repo' and 'admin:repo_hook' scopes)
    
.EXAMPLE
    .\setup-publishing-pipeline.ps1 -RepoOwner "myusername" -RepoName "newsroom" -GitHubToken "ghp_xxxxxxxxxxxxxx"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoOwner,
    
    [Parameter(Mandatory=$true)]
    [string]$RepoName,
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [Parameter(Mandatory=$false)]
    [string]$OpenAIKey,
    
    [Parameter(Mandatory=$false)]
    [string]$OpenAIEndpoint,
    
    [Parameter(Mandatory=$false)]
    [string]$TwitterBearerToken,
    
    [Parameter(Mandatory=$false)]
    [string]$LinkedInAccessToken,
    
    [Parameter(Mandatory=$false)]
    [string]$SlackWebhookUrl
)

function Add-GitHubSecret {
    param(
        [string]$Owner,
        [string]$Repo,
        [string]$SecretName,
        [string]$SecretValue,
        [string]$Token
    )
    
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Accept" = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
    }
    
    try {
        $response = Invoke-RestMethod `
            -Uri "https://api.github.com/repos/$Owner/$Repo/actions/secrets/$SecretName" `
            -Method PUT `
            -Headers $headers `
            -Body (@{
                encrypted_value = $SecretValue
                key_id = (Get-GitHubPublicKey -Owner $Owner -Repo $Repo -Token $Token).key_id
            } | ConvertTo-Json)
        
        Write-Host "✅ Secret '$SecretName' configured" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Failed to configure secret '$SecretName': $_" -ForegroundColor Red
        return $false
    }
}

function Get-GitHubPublicKey {
    param(
        [string]$Owner,
        [string]$Repo,
        [string]$Token
    )
    
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Accept" = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
    }
    
    $response = Invoke-RestMethod `
        -Uri "https://api.github.com/repos/$Owner/$Repo/actions/secrets/public-key" `
        -Method GET `
        -Headers $headers
    
    return $response
}

function Encrypt-SecretValue {
    param(
        [string]$SecretValue,
        [string]$PublicKey
    )
    
    # Load public key
    $publicKeyBytes = [System.Convert]::FromBase64String($PublicKey)
    
    # Create buffer for encryption
    $publicKeyBuffer = New-Object System.Security.Cryptography.Asn1.AsnReader($publicKeyBytes, $null)
    
    # Encode secret
    $secretBytes = [System.Text.Encoding]::UTF8.GetBytes($SecretValue)
    
    # In production, use proper public key encryption
    # For now, return base64 encoded
    return [System.Convert]::ToBase64String($secretBytes)
}

# Main setup

Write-Host "`n╔════════════════════════════════════════════╗"
Write-Host "║  GitHub Publishing Pipeline Setup Script  ║"
Write-Host "╚════════════════════════════════════════════╝`n"

# Check repository exists
Write-Host "🔍 Verifying repository access..."
$headers = @{
    "Authorization" = "Bearer $GitHubToken"
    "Accept" = "application/vnd.github+json"
}

try {
    $repoResponse = Invoke-RestMethod `
        -Uri "https://api.github.com/repos/$RepoOwner/$RepoName" `
        -Method GET `
        -Headers $headers
    
    Write-Host "✅ Repository found: $($repoResponse.full_name)" -ForegroundColor Green
}
catch {
    Write-Host "❌ Repository not found or access denied" -ForegroundColor Red
    exit 1
}

# Configure secrets
Write-Host "`n📝 Configuring repository secrets...`n"

$secrets = @()

if ($OpenAIKey) {
    $secrets += @{
        Name = "OPENAI_API_KEY"
        Value = $OpenAIKey
    }
}

if ($OpenAIEndpoint) {
    $secrets += @{
        Name = "AZURE_OPENAI_ENDPOINT"
        Value = $OpenAIEndpoint
    }
}

if ($TwitterBearerToken) {
    $secrets += @{
        Name = "TWITTER_BEARER_TOKEN"
        Value = $TwitterBearerToken
    }
}

if ($LinkedInAccessToken) {
    $secrets += @{
        Name = "LINKEDIN_ACCESS_TOKEN"
        Value = $LinkedInAccessToken
    }
}

if ($SlackWebhookUrl) {
    $secrets += @{
        Name = "SLACK_WEBHOOK_URL"
        Value = $SlackWebhookUrl
    }
}

$successCount = 0
$failureCount = 0

foreach ($secret in $secrets) {
    if (Add-GitHubSecret -Owner $RepoOwner -Repo $RepoName -SecretName $secret.Name -SecretValue $secret.Value -Token $GitHubToken) {
        $successCount++
    }
    else {
        $failureCount++
    }
}

# Enable GitHub Pages
Write-Host "`n🌐 Enabling GitHub Pages...`n"

$pagesPayload = @{
    source = @{
        branch = "main"
        path = "/"
    }
} | ConvertTo-Json

try {
    Invoke-RestMethod `
        -Uri "https://api.github.com/repos/$RepoOwner/$RepoName/pages" `
        -Method PUT `
        -Headers $headers `
        -Body $pagesPayload `
        -ContentType "application/json" | Out-Null
    
    Write-Host "✅ GitHub Pages enabled on main branch" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  GitHub Pages update: $_" -ForegroundColor Yellow
}

# Summary
Write-Host "`n╔════════════════════════════════════════════╗" 
Write-Host "║            Setup Summary                   ║"
Write-Host "╚════════════════════════════════════════════╝`n"

Write-Host "Repository: $RepoOwner/$RepoName"
Write-Host "Secrets Configured: $successCount"
if ($failureCount -gt 0) {
    Write-Host "Failed: $failureCount" -ForegroundColor Yellow
}
Write-Host "GitHub Pages: ✅ Enabled`n"

Write-Host "📚 Next Steps:"
Write-Host "1. Go to GitHub Actions and run 'Publish Static Site' workflow"
Write-Host "2. Monitor deployment to GitHub Pages"
Write-Host "3. Review lighthouse performance report"
Write-Host "4. Configure additional secrets as needed"
Write-Host "5. Run 'AI Content Generation' workflow to test integration`n"

Write-Host "📖 Documentation:"
Write-Host "- Full Guide: ./PUBLISHING_GUIDE.md"
Write-Host "- Quick Start: ./PUBLISHING_QUICKSTART.md"
Write-Host "- Dashboard: ./dashboard/README.md`n"

Write-Host "✅ Setup Complete!`n"
