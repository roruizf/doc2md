# Security Policy

## Secrets and API Keys

Never commit API keys, tokens, passwords, or private documents to the repository.

`OPENROUTER_API_KEY` is required when using:

```bash
doc2md input.pdf -o output.md --images=vlm --vlm-provider openrouter
```

Use [.env.example](./.env.example) as a template for local development, then
create a private `.env` file that is not committed.

## VLM Privacy Note

When `--images=vlm` is active, extracted images are sent to the selected VLM
provider for description. Do not use VLM mode on sensitive documents unless your
provider, account, and data handling policy allow it.

## Reporting Vulnerabilities

Please report suspected vulnerabilities privately to the repository maintainer.
If no dedicated security contact is published, open a minimal GitHub issue that
requests a private disclosure channel without including exploit details.

Include:

- affected version or commit
- impact summary
- reproduction steps
- whether secrets, private files, or third-party API calls are involved
