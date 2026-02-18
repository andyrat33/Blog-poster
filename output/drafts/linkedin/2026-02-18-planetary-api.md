# LinkedIn Post Drafts — planetary-api

---

## Variation 1

I built a deliberately vulnerable Flask API to use as a training target.

It's got SQL Injection, Command Injection, SSRF, and Path Traversal baked in — all paired with secure versions of the same endpoints. Star Trek planets as the dataset. Jenkins pipeline running Semgrep and OWASP checks on every commit.

Full walkthrough here: http://blog.infosecmatters.net/2026/02/building-flask-api-for-security.html

Would this be useful for your team's AppSec workshops?

---

## Variation 2

Most AppSec training uses slides. I prefer a live target you can actually break.

Built planetary-api for exactly that — a Flask REST API with intentional vulnerabilities and their fixes side by side. Spin it up with Docker, run your tools against it, then look at the code.

Post: http://blog.infosecmatters.net/2026/02/building-flask-api-for-security.html

How does your team run AppSec training?

---

## Variation 3

Vulnerable by design. That's the point.

planetary-api is a Flask REST API I put together for security training — SQL Injection, Command Injection, SSRF, Path Traversal, all intentional. Each bad endpoint has a secure counterpart so you can compare the code directly.

Read the full post: http://blog.infosecmatters.net/2026/02/building-flask-api-for-security.html

What tools do you use to test against a target like this?
