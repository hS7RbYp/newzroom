# Create Azure OpenAI model deployments using REST API

$resourceGroup = "rg-aan-dev"
$resourceName = "aan-dev-openai"
$subscriptionId = "8100f321-37f7-44e1-922c-2b68c459bae0"

# Get the API key
$apiKey = az cognitiveservices account keys list --resource-group $resourceGroup --name $resourceName --query "key1" -o tsv
Write-Host "API Key retrieved: $($apiKey.Substring(0, 20))..."

# Base URL for REST API
$baseUrl = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.CognitiveServices/accounts/$resourceName/deployments"

# Headers
$headers = @{
    "Authorization" = "Bearer $(az account get-access-token --query accessToken -o tsv)"
    "Content-Type" = "application/json"
}

# Create GPT-4o-mini deployment
$deploymentName = "gpt-4o-mini"
$deploymentUrl = "$baseUrl/$deploymentName`?api-version=2023-05-01"

$deploymentBody = @{
    sku = @{
        name = "Standard"
        capacity = 10
    }
    properties = @{
        model = @{
            format = "OpenAI"
            name = "gpt-4o-mini"
            version = "2024-07-18"
        }
    }
} | ConvertTo-Json -Depth 10

Write-Host "`n[CREATE] $deploymentName deployment..."
Write-Host "URL: $deploymentUrl"

$response = Invoke-WebRequest -Uri $deploymentUrl `
    -Method Put `
    -Headers $headers `
    -Body $deploymentBody `
    -ContentType "application/json" `
    -UseBasicParsing `
    -ErrorAction SilentlyContinue

Write-Host "Status: $($response.StatusCode)"
if ($response.Content) {
    Write-Host "Response: $($response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3)"
}

# Create GPT-4o deployment
$deploymentName2 = "gpt-4o"
$deploymentUrl2 = "$baseUrl/$deploymentName2`?api-version=2023-05-01"

$deploymentBody2 = @{
    sku = @{
        name = "Standard"
        capacity = 10
    }
    properties = @{
        model = @{
            format = "OpenAI"
            name = "gpt-4o"
            version = "2024-08-06"
        }
    }
} | ConvertTo-Json -Depth 10

Write-Host "`n[CREATE] $deploymentName2 deployment..."
Write-Host "URL: $deploymentUrl2"

$response2 = Invoke-WebRequest -Uri $deploymentUrl2 `
    -Method Put `
    -Headers $headers `
    -Body $deploymentBody2 `
    -ContentType "application/json" `
    -UseBasicParsing `
    -ErrorAction SilentlyContinue
    
Write-Host "Status: $($response2.StatusCode)"
if ($response2.Content) {
    Write-Host "Response: $($response2.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3)"
}

# Create DALL-E 3 deployment
$deploymentName3 = "dall-e-3"
$deploymentUrl3 = "$baseUrl/$deploymentName3`?api-version=2023-05-01"

$deploymentBody3 = @{
    sku = @{
        name = "Standard"
        capacity = 1
    }
    properties = @{
        model = @{
            format = "OpenAI"
            name = "dall-e-3"
            version = "3.0"
        }
    }
} | ConvertTo-Json -Depth 10

Write-Host "`n[CREATE] $deploymentName3 deployment..."
Write-Host "URL: $deploymentUrl3"

$response3 = Invoke-WebRequest -Uri $deploymentUrl3 `
    -Method Put `
    -Headers $headers `
    -Body $deploymentBody3 `
    -ContentType "application/json" `
    -UseBasicParsing `
    -ErrorAction SilentlyContinue
    
Write-Host "Status: $($response3.StatusCode)"
if ($response3.Content) {
    Write-Host "Response: $($response3.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3)"
}

Write-Host "`nDeployment creation initiated!"
