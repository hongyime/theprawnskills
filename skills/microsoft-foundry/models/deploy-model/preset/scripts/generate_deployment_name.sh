#!/usr/bin/env bash
# Query existing Azure deployments; print a free name. Never creates a deployment.
set -euo pipefail
if [[ $# -ne 3 ]]; then
  printf '%s\n' 'Usage: generate_deployment_name.sh ACCOUNT RESOURCE_GROUP MODEL' >&2
  exit 2
fi
account=$1
resource_group=$2
model=$3
if [[ -z "$account" || -z "$resource_group" || ! "$model" =~ ^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$ ]]; then
  printf '%s\n' 'Account and resource group are required; model must be a valid 1-64 character deployment name.' >&2
  exit 2
fi
command -v az >/dev/null || { printf '%s\n' 'Azure CLI is required.' >&2; exit 2; }
existing=$(az cognitiveservices account deployment list --name "$account" --resource-group "$resource_group" --query '[].name' --output tsv --only-show-errors) || {
  printf '%s\n' 'Cannot list deployments; no name was selected.' >&2
  exit 1
}
candidate=$model
suffix=2
while printf '%s\n' "$existing" | tr -d '\r' | grep -F -i -x -- "$candidate" >/dev/null; do
  suffix_text="-$suffix"
  max_length=$((64 - ${#suffix_text}))
  candidate="${model:0:max_length}${suffix_text}"
  suffix=$((suffix + 1))
done
printf '%s\n' "$candidate"
