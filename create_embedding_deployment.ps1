# Create text-embedding-3-small deployment for vector embeddings

$resourceGroup = "rg-aan-dev"
$resourceName = "aan-dev-openai"
$subscriptionId = "8100f321-37f7-44e1-922c-2b68c459bae0"

# Get the API key
$apiKey = az cognitiveservices account keys list --resource-group $resourceGroup --name $resourceName --query "key1" -o tsv
Write-Host "Creating embeddings deployment..."

# Base URL for REST API
$baseUrl = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.CognitiveServices/accounts/$resourceName/deployments"

# Headers
$headers = @{
    "Authorization" = "Bearer $(az account get-access-token --query accessToken -o tsv)"
    "Content-Type" = "application/json"
}

# Create text-embedding-3-small deployment
$deploymentName = "text-embedding-3-small"
$deploymentUrl = "$baseUrl/$deploymentName`?api-version=2023-05-01"

$deploymentBody = @{
    sku = @{
        name = "Standard"
        capacity = 1
    }
    properties = @{
        model = @{
            format = "OpenAI"
            name = "text-embedding-3-small"
            version = "1"
        }
    }
} | ConvertTo-Json -Depth 10

Write-Host "[CREATE] $deploymentName deployment..."

$response = Invoke-WebRequest -Uri $deploymentUrl `
    -Method Put `
    -Headers $headers `
    -Body $deploymentBody `
    -ContentType "application/json" `
    -UseBasicParsing `
    -ErrorAction SilentlyContinue

Write-Host "Status: $($response.StatusCode)"
if ($response.Content) {
    $content = $response.Content | ConvertFrom-Json
    if ($content.name) {
        Write-Host "Deployment created: $($content.name)"
        Write-Host "Model: $($content.properties.model.name)"
    }
}

Write-Host "`nEmbedding deployment deployment created!"
