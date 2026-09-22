## Description:

Tencent News integrated information service for news, fact-checking, weather and weather alerts, and Gaokao admission-data queries and application planning.

This skill is ready for commercial/non-commercial use.

## Publisher:

[tencentnewsteam](https://clawhub.ai/user/tencentnewsteam)

### License/Terms of Use:

MIT-0

## Use Case:

External users and agents use this skill to query Tencent News services for current news, fact-checking, China weather and weather alerts, and ordinary Gaokao admission data or application-planning guidance.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Install and update instructions include commands that execute remote scripts from a Tencent CDN.

Mitigation: Download and inspect the installer first, verify it through trusted Tencent News channels, and run it only in an environment where executing that code is acceptable.

Risk: The skill depends on a local Tencent News CLI and API key, so credentials may be exposed if users paste real keys into chats or logs.

Mitigation: Keep API key entry local, use placeholders in agent conversations, and avoid echoing or storing real keys in prompts, reports, or diagnostic output.

Risk: CLI diagnostics and wrapper scripts inspect local installation state and execute the resolved Tencent News CLI.

Mitigation: Review the resolved CLI path and wrapper behavior before deployment, and run the skill with least-privilege local account permissions.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/tencentnewsteam/skills/tencent-news)
- [Publisher profile](https://clawhub.ai/user/tencentnewsteam)
- [Fact-checking guide](references/factcheck.md)
- [Weather query guide](references/weather.md)
- [Weather alert guide](references/weather-alert.md)
- [Gaokao volunteer planning guide](references/gaokao-volunteer.md)
- [Gaokao HTML interaction reference](references/gaokao-html-interaction-reference.html)
- [Installation guide](references/installation-guide.md)
- [Update guide](references/update-guide.md)
- [API key setup guide](references/env-setup-guide.md)
- [Tencent News API key page](https://news.qq.com/exchange?scene=appkey)
- [Tencent JiaoZhen AI fact-checking page](https://view.inews.qq.com/ai/agent/UTR2025041800262600?no-redirect=1)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown with inline shell commands and occasional HTML reports]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Outputs depend on Tencent News CLI responses and local API key configuration.]

## Skill Version(s):

1.2.3 (source: frontmatter and release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
