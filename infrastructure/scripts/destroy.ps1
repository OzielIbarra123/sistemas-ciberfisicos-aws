<#
  Elimina la pila y sus recursos para evitar costos.
  Vacía primero el bucket de telemetría (CloudFormation no borra buckets con objetos).
  Uso:  .\destroy.ps1 [-Region us-east-2] [-StackName sci-almacen]
#>
param(
  [string]$Region = "us-east-2",
  [string]$StackName = "sci-almacen"
)
$ErrorActionPreference = "Stop"

$bucket = aws cloudformation describe-stacks --stack-name $StackName --region $Region `
    --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text
if ($bucket) {
  Write-Host "Vaciando bucket $bucket (incluye versiones)..."
  $versions = aws s3api list-object-versions --bucket $bucket --output json | ConvertFrom-Json
  $objects = @($versions.Versions) + @($versions.DeleteMarkers) | Where-Object { $_ }
  foreach ($o in $objects) {
    aws s3api delete-object --bucket $bucket --key $o.Key --version-id $o.VersionId | Out-Null
  }
}
aws cloudformation delete-stack --stack-name $StackName --region $Region
aws cloudformation wait stack-delete-complete --stack-name $StackName --region $Region
Write-Host "Pila $StackName eliminada. El bucket de artefactos ($StackName-artifacts-<cuenta>) se conserva; bórralo manualmente si ya no lo necesitas."
