# Deploying Searchable KB

Every step is an AWS CLI command so each resource is created on purpose and can be explained. Run them in **one terminal window** so the variables from step 0 stay set. If you open a new terminal, re-run step 0.

```
Browser ──> Lambda Function URL ──> Lambda (container image from ECR)
                                      ├── S3        (source markdown)
                                      └── DynamoDB  (entries + embeddings)
GitHub push ──> Actions: test → build arm64 image → push to ECR → update Lambda
```

## Cost

The account is on the AWS **Free plan**. Nothing is charged to a card on that plan; usage draws down promotional credits. Even so, the setup avoids anything that consumes credits meaningfully:

| Choice | Why |
| --- | --- |
| Lambda + Function URL (no API Gateway, ALB, Fargate, NAT) | Lambda is always-free up to 1M requests / 400k GB-seconds a month. Load balancers and Fargate bill by the hour. |
| DynamoDB **provisioned** at 5 RCU / 5 WCU | Always-free covers 25 RCU/WCU of provisioned capacity. On-demand mode isn't covered. |
| ECR lifecycle policy keeping 2 images | Each CI run pushes a new image; without cleanup storage keeps growing. |
| Token in a Lambda env var, not Secrets Manager | Secrets Manager is $0.40/secret/month. |
| CloudWatch log retention of 7 days | Logs otherwise stay forever. |

**Do not** click "Upgrade to paid plan" in the console. Tear everything down (last section) once you're done with it.

---

## 0. Variables

```bash
cd ~/Searchable_KB
export AWS_REGION=us-west-2
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export APP=searchable-kb
export BUCKET=$APP-docs-$ACCOUNT_ID
export TABLE=$APP-entries
export REGISTRY=$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
export IMAGE=$REGISTRY/$APP
export INGEST_TOKEN=$(openssl rand -hex 16)
echo "Ingest token (save it somewhere): $INGEST_TOKEN"
```

## 1. Run it locally (no Docker)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```bash
curl -X POST localhost:8000/api/ingest        # embeds kb/*.md into data/index.json
curl "localhost:8000/api/search?q=cant+hear+anyone+on+my+call"
open http://localhost:8000
```

## 2. Run it in Docker locally

```bash
docker build -t searchable-kb:local .
docker run --rm -p 8080:8080 --read-only --tmpfs /tmp searchable-kb:local
```

`--read-only --tmpfs /tmp` imitates Lambda, where everything except `/tmp` is read-only. If the app tries to write anywhere else, it breaks here instead of in AWS.

```bash
curl -X POST localhost:8080/api/ingest
open http://localhost:8080
```

## 3. S3: upload the source documents

```bash
aws s3api create-bucket --bucket $BUCKET \
  --create-bucket-configuration LocationConstraint=$AWS_REGION
aws s3 sync kb/ s3://$BUCKET/kb/
aws s3 ls s3://$BUCKET/kb/
```

New buckets block public access by default. Only the Lambda role will be able to read it.

## 4. DynamoDB: table for the index

```bash
aws dynamodb create-table --table-name $TABLE \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
aws dynamodb wait table-exists --table-name $TABLE
```

## 5. ECR: push the image

```bash
aws ecr create-repository --repository-name $APP \
  --image-scanning-configuration scanOnPush=true

aws ecr put-lifecycle-policy --repository-name $APP --lifecycle-policy-text \
  '{"rules":[{"rulePriority":1,"description":"keep last 2 images","selection":{"tagStatus":"any","countType":"imageCountMoreThan","countNumber":2},"action":{"type":"expire"}}]}'

aws ecr get-login-password | docker login --username AWS --password-stdin $REGISTRY

docker buildx build --platform linux/arm64 --provenance=false -t ${IMAGE}:v1 --push .
```

- `--platform linux/arm64`: the Lambda will run on Graviton (arm64). That's also what an Apple Silicon Mac builds natively.
- `--provenance=false`: without it, buildx pushes an image index with an attestation manifest, and Lambda rejects that format.

## 6. IAM: execution role for the Lambda

```bash
cat > /tmp/lambda-trust.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "lambda.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role --role-name $APP-lambda-role \
  --assume-role-policy-document file:///tmp/lambda-trust.json

aws iam attach-role-policy --role-name $APP-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

cat > /tmp/lambda-permissions.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListKbPrefix",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::$BUCKET",
      "Condition": { "StringLike": { "s3:prefix": ["kb/*"] } }
    },
    {
      "Sid": "ReadKbDocs",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET/kb/*"
    },
    {
      "Sid": "ReadWriteIndex",
      "Effect": "Allow",
      "Action": ["dynamodb:Scan", "dynamodb:PutItem", "dynamodb:DeleteItem", "dynamodb:BatchWriteItem"],
      "Resource": "arn:aws:dynamodb:${AWS_REGION}:${ACCOUNT_ID}:table/$TABLE"
    }
  ]
}
EOF

aws iam put-role-policy --role-name $APP-lambda-role \
  --policy-name kb-data-access --policy-document file:///tmp/lambda-permissions.json
```

The role can read one S3 prefix and touch one table. Nothing else.

## 7. Lambda: create the function

```bash
sleep 10   # new IAM roles take a few seconds before Lambda can assume them

aws lambda create-function \
  --function-name $APP \
  --package-type Image \
  --code ImageUri=${IMAGE}:v1 \
  --role arn:aws:iam::${ACCOUNT_ID}:role/$APP-lambda-role \
  --architectures arm64 \
  --memory-size 1536 \
  --timeout 60 \
  --environment "Variables={STORAGE=aws,S3_BUCKET=$BUCKET,S3_PREFIX=kb/,TABLE_NAME=$TABLE,INGEST_TOKEN=$INGEST_TOKEN}"

aws lambda wait function-active-v2 --function-name $APP
```

## 8. Function URL: give it a public HTTPS endpoint

```bash
aws lambda create-function-url-config --function-name $APP --auth-type NONE

aws lambda add-permission --function-name $APP --statement-id public-url \
  --action lambda:InvokeFunctionUrl --principal "*" --function-url-auth-type NONE

aws lambda add-permission --function-name $APP --statement-id public-url-invoke \
  --action lambda:InvokeFunction --principal "*" --invoked-via-function-url

export URL=$(aws lambda get-function-url-config --function-name $APP --query FunctionUrl --output text)
echo $URL
```

Public URLs need both permissions: `InvokeFunctionUrl`, plus `InvokeFunction` scoped to calls that come through the URL.

## 9. Ingest and try it

```bash
curl -X POST "${URL}api/ingest" -H "X-Ingest-Token: $INGEST_TOKEN"
curl "${URL}api/search?q=got+a+new+phone+and+cant+approve+sign+ins"
open $URL
```

The first request after a deploy is a cold start: the container boots, then the model loads. Later requests are much faster.

Logs, and a 7-day retention limit (the log group appears after the first request):

```bash
aws logs tail /aws/lambda/$APP --follow
aws logs put-retention-policy --log-group-name /aws/lambda/$APP --retention-in-days 7
```

## 10. CI/CD: GitHub Actions deploys on push to main

GitHub gets **no stored AWS keys**. It signs in to AWS with OIDC, which issues short-lived credentials to one repo's main branch only.

```bash
export GH_REPO=$(gh api user --jq .login)/Searchable_KB

aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com

cat > /tmp/github-trust.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub": "repo:${GH_REPO}:ref:refs/heads/main"
      }
    }
  }]
}
EOF

aws iam create-role --role-name $APP-github-deploy \
  --assume-role-policy-document file:///tmp/github-trust.json

cat > /tmp/github-permissions.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": "ecr:GetAuthorizationToken", "Resource": "*" },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability", "ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer",
        "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload", "ecr:PutImage",
        "ecr:GetRepositoryPolicy", "ecr:SetRepositoryPolicy"
      ],
      "Resource": "arn:aws:ecr:${AWS_REGION}:${ACCOUNT_ID}:repository/$APP"
    },
    {
      "Effect": "Allow",
      "Action": ["lambda:UpdateFunctionCode", "lambda:GetFunction", "lambda:GetFunctionConfiguration"],
      "Resource": "arn:aws:lambda:${AWS_REGION}:${ACCOUNT_ID}:function:$APP"
    }
  ]
}
EOF

aws iam put-role-policy --role-name $APP-github-deploy \
  --policy-name deploy --policy-document file:///tmp/github-permissions.json
```

Create the repo, set the secret **before** the first push, then push:

```bash
git init -b main
git add .
git commit -m "Searchable KB: semantic search over IT knowledge base entries"

gh repo create Searchable_KB --public --source . --remote origin
gh secret set AWS_DEPLOY_ROLE_ARN --body "arn:aws:iam::${ACCOUNT_ID}:role/$APP-github-deploy"
git push -u origin main
gh run watch
```

The arm64 build runs under QEMU emulation on GitHub's x86 runners, so the first run takes several minutes. Later runs reuse the layer cache.

To test the pipeline, change something visible (like the subtitle in `app/static/index.html`), push it, and reload the URL once the run finishes.

If you add or edit entries in `kb/`, sync them and re-ingest:

```bash
aws s3 sync kb/ s3://$BUCKET/kb/ --delete
curl -X POST "${URL}api/ingest" -H "X-Ingest-Token: $INGEST_TOKEN"
```

---

## Teardown

Run step 0 first if this is a new terminal.

```bash
aws lambda delete-function-url-config --function-name $APP
aws lambda delete-function --function-name $APP
aws logs delete-log-group --log-group-name /aws/lambda/$APP
aws ecr delete-repository --repository-name $APP --force
aws dynamodb delete-table --table-name $TABLE
aws s3 rb s3://$BUCKET --force

aws iam delete-role-policy --role-name $APP-lambda-role --policy-name kb-data-access
aws iam detach-role-policy --role-name $APP-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name $APP-lambda-role

aws iam delete-role-policy --role-name $APP-github-deploy --policy-name deploy
aws iam delete-role --role-name $APP-github-deploy
aws iam delete-open-id-connect-provider --open-id-connect-provider-arn \
  arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com

gh workflow disable test-build-deploy   # otherwise future pushes fail at the deploy step
```
