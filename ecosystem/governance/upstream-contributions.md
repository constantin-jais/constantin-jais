# Upstream contribution gate

This policy covers every publicly visible interaction with a repository outside the contributor's own GitHub organizations: branch pushes to public forks, issues, pull requests, comments, reviews, and changing draft state.

## Rule

Agents may investigate, edit, test, commit and prepare contribution text locally. They must not perform an upstream publication action until the matching human approval is recorded in the active session or decision log.

A draft pull request is already a public publication. “Draft” reduces merge pressure; it does not replace approval before push.

## Two gates

```text
problem + reproduction
→ isolated local patch
→ upstream tests + Wrench evidence
→ contribution-guide, license, scope and disclosure review
→ APPROVE_UPSTREAM_PUSH <repository> <branch> <evidence-ref>
→ push to the contributor fork + open draft PR
→ human review of the exact public diff and message
→ APPROVE_READY_FOR_REVIEW <pull-request-url> <head-sha>
→ mark ready for review
```

`APPROVE_UPSTREAM_PUSH` authorizes only the named repository, branch and evidence revision. A changed HEAD requires another approval. `APPROVE_READY_FOR_REVIEW` authorizes only the named PR at the named HEAD.

## What the gate does in practice

- separates local engineering from external communication;
- gives a human the final decision on reputation, scope, disclosure and maintainer burden;
- prevents batch publication of unrelated or incompletely tested patches;
- leaves a trace connecting the public action to the reviewed commit and evidence;
- makes closing, rewriting or withholding a patch an explicit choice rather than an accidental side effect of automation.

It does **not** prove that a patch is correct, guarantee upstream acceptance, or technically prevent a human from using GitHub outside the harness. It is a process and audit control. Local remote configuration adds defense in depth:

```sh
git remote rename origin upstream                    # when origin currently targets the third party
git remote rename fork origin                        # contributor-owned fork becomes origin
git remote set-url --push upstream DISABLED          # direct upstream push fails locally
git config remote.pushDefault origin
git remote -v
```

## Required evidence

Before the first approval:

1. minimal problem statement and reproduction;
2. focused diff with non-goals;
3. exact validation commands and results;
4. compatibility and security impact;
5. license and contribution-guide compatibility;
6. no secrets, private repository metadata, customer data or personal data;
7. proposed title/body and disclosure route.

Security vulnerabilities follow the upstream private disclosure process. They are never opened as public issues or PRs before coordinated disclosure approval.

## Trade-offs

| Gain | Cost / limitation |
| --- | --- |
| lower reputational and disclosure risk | slower contribution cycle |
| less maintainer noise | two explicit human checkpoints |
| exact audit trail | approvals must be renewed after a rebase or amended commit |
| agents can still prepare complete patches locally | no unattended upstream contribution loop |
| focused, tested submissions | some useful experiments will remain local |

## Dioxus incident — 2026-07-03

Three unrelated Dioxus pull requests were opened non-draft within four seconds, before human review and without visible upstream checks. On 2026-07-11 they were closed with a message explaining that work in progress had been sent accidentally and thanking Dioxus maintainers and contributors. Their branches remain available for local review; no resubmission is implied.
