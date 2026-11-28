## Containers

### Build and Push Images

```bash
# Build container image
wrangler containers build -t my-app:latest .

# Build and push in one command
wrangler containers build -t my-app:latest . --push

# Push existing image to Cloudflare registry
wrangler containers push my-app:latest
```

### Manage Containers

```bash
# List containers
wrangler containers list

# Get container info
wrangler containers info <CONTAINER_ID>

# Delete container
wrangler containers delete <CONTAINER_ID>
```

### Manage Images

```bash
# List images in registry
wrangler containers images list

# Delete image
wrangler containers images delete my-app:latest
```

### Manage External Registries

> **Security**: Never hardcode registry credentials in commands. Use environment variables.

```bash
# List configured registries
wrangler containers registries list

# Configure external registry (e.g., ECR)
wrangler containers registries configure <DOMAIN> \
  --aws-access-key-id "$AWS_ACCESS_KEY_ID"

# Configure DockerHub
wrangler containers registries configure <DOMAIN> \
  --dockerhub-username "$DOCKERHUB_USERNAME"

# Delete registry configuration
wrangler containers registries delete <DOMAIN>
```

---

## Workflows

### Manage Workflows

```bash
# List workflows
wrangler workflows list

# Describe workflow
wrangler workflows describe my-workflow

# Trigger workflow instance
wrangler workflows trigger my-workflow

# Trigger with parameters
wrangler workflows trigger my-workflow --params '{"key": "value"}'

# Delete workflow
wrangler workflows delete my-workflow
```

### Manage Workflow Instances

```bash
# List instances
wrangler workflows instances list my-workflow

# Describe instance
wrangler workflows instances describe my-workflow <INSTANCE_ID>

# Terminate instance
wrangler workflows instances terminate my-workflow <INSTANCE_ID>
```

---

## Pipelines

### Manage Pipelines

```bash
# Create pipeline
wrangler pipelines create my-pipeline --r2 my-bucket

# List pipelines
wrangler pipelines list

# Show pipeline details
wrangler pipelines show my-pipeline

# Update pipeline
wrangler pipelines update my-pipeline --batch-max-mb 100

# Delete pipeline
wrangler pipelines delete my-pipeline
```

---

## Secrets Store

### Manage Stores

```bash
# Create store
wrangler secrets-store store create my-store

# List stores
wrangler secrets-store store list

# Delete store
wrangler secrets-store store delete <STORE_ID>
```

### Manage Secrets in Store

```bash
# Add secret to store
wrangler secrets-store secret put <STORE_ID> my-secret

# List secrets in store
wrangler secrets-store secret list <STORE_ID>

# Get secret
wrangler secrets-store secret get <STORE_ID> my-secret

# Delete secret from store
wrangler secrets-store secret delete <STORE_ID> my-secret
```

---

## Pages (Frontend Deployment)

```bash
# Create Pages project
wrangler pages project create my-site

# Deploy directory to Pages
wrangler pages deploy ./dist

# Deploy with specific branch
wrangler pages deploy ./dist --branch main

# List deployments
wrangler pages deployment list --project-name my-site
```

---

