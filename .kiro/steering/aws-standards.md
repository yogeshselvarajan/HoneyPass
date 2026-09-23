---
inclusion: auto
name: aws-standards
description: AWS integration standards for Bedrock, KMS, DynamoDB, S3 and AgentCore. Use when writing or reviewing code that calls AWS services or IAM policies.
---
# AWS standards
- Create clients in adapters only, injected via constructors: `boto3.client("kms", config=RETRY_CONFIG)`.
- Region from settings (`AWS_REGION`); never hard-code account IDs, ARNs, or model IDs.
- KMS signing: asymmetric key `ECC_NIST_P256`, `SigningAlgorithm="ECDSA_SHA_256"`, `MessageType="DIGEST"`
  over the SHA-256 of the canonical passport payload. Cache the public key for local verification.
- DynamoDB: single table `honeypass-passports`, PK `plugin#<name>`, SK `passport#<issued_at_iso>`;
  conditional writes to prevent overwriting. S3: `traces/<plugin>/<detention_id>.jsonl`, SSE-KMS.
- Bedrock: model id from `HONEYPASS_BEDROCK_MODEL_ID`; set max tokens and a request timeout; handle throttling.
- AgentCore Runtime is optional (`HONEYPASS_SANDBOX=agentcore`); local sandbox is the default.
- Tests: `moto` for DynamoDB/S3/KMS where supported; mark real-AWS tests `@pytest.mark.aws`.
- Use the AWS Documentation MCP server to confirm current API parameters before writing AWS calls.
