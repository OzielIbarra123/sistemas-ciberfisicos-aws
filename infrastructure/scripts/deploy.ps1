<#
  Despliega la pila de telemetría (IaC) en AWS con CloudFormation.
  Requisitos: AWS CLI v2 configurada (`aws configure`) con permisos de administrador.
  Uso:  .\deploy.ps1 -AlertEmail correo@ejemplo.com [-Region us-east-2] [-StackName sci-almacen]
#>
param(
  [Parameter(Mandatory = $true)][string]$AlertEmail,
  [string]$Region = "us-east-2",
  [string]$StackName = "sci-almacen"
)
$ErrorActionPreference = "Stop"

$root     = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$template = Join-Path $root "infrastructure\cloudformation\telemetry-stack.yaml"
$packaged = Join-Path $root "build\packaged-template.yaml"
New-Item -ItemType Directory -Force (Split-Path $packaged) | Out-Null

$account = aws sts get-caller-identity --query Account --output text
$artifactBucket = "$StackName-artifacts-$account"

# Bucket para los artefactos (código de las Lambdas); se crea solo si no existe
aws s3api head-bucket --bucket $artifactBucket 2>$null
if ($LASTEXITCODE -ne 0) {
  aws s3api create-bucket --bucket $artifactBucket --region $Region `
      --create-bucket-configuration LocationConstraint=$Region | Out-Null
  aws s3api put-public-access-block --bucket $artifactBucket `
      --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
}

Write-Host "Validando plantilla..."
aws cloudformation validate-template --template-body "file://$template" --region $Region | Out-Null

Write-Host "Empaquetando código de las Lambdas..."
aws cloudformation package --template-file $template --s3-bucket $artifactBucket `
    --output-template-file $packaged --region $Region

Write-Host "Desplegando pila $StackName..."
aws cloudformation deploy --template-file $packaged --stack-name $StackName `
    --capabilities CAPABILITY_IAM --region $Region `
    --parameter-overrides ProjectName=$StackName AlertEmail=$AlertEmail

aws cloudformation describe-stacks --stack-name $StackName --region $Region `
    --query "Stacks[0].Outputs" --output table
Write-Host "Revisa tu correo y confirma la suscripción de SNS para recibir alertas."
