#!/usr/bin/env bash
# Despliega la pila de telemetría con CloudFormation (equivalente a deploy.ps1).
# Uso: ./deploy.sh correo@ejemplo.com [region] [stack]
set -euo pipefail

ALERT_EMAIL="${1:?Uso: ./deploy.sh correo@ejemplo.com [region] [stack]}"
REGION="${2:-us-east-2}"
STACK="${3:-sci-almacen}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TEMPLATE="$ROOT/infrastructure/cloudformation/telemetry-stack.yaml"
PACKAGED="$ROOT/build/packaged-template.yaml"
mkdir -p "$(dirname "$PACKAGED")"

ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"
ARTIFACTS="$STACK-artifacts-$ACCOUNT"

if ! aws s3api head-bucket --bucket "$ARTIFACTS" 2>/dev/null; then
  aws s3api create-bucket --bucket "$ARTIFACTS" --region "$REGION" \
    --create-bucket-configuration LocationConstraint="$REGION"
  aws s3api put-public-access-block --bucket "$ARTIFACTS" \
    --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
fi

aws cloudformation validate-template --template-body "file://$TEMPLATE" --region "$REGION" >/dev/null
aws cloudformation package --template-file "$TEMPLATE" --s3-bucket "$ARTIFACTS" \
  --output-template-file "$PACKAGED" --region "$REGION"
aws cloudformation deploy --template-file "$PACKAGED" --stack-name "$STACK" \
  --capabilities CAPABILITY_IAM --region "$REGION" \
  --parameter-overrides ProjectName="$STACK" AlertEmail="$ALERT_EMAIL"
aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs" --output table
