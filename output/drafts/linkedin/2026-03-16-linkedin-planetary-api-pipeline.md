# LinkedIn Posts — Planetary API AWS Pipeline

Blog post: http://blog.infosecmatters.net/2026/03/securing-aws-codepipeline-end-to-end.html

---

## Variation 1

I built a pipeline designed to find vulnerabilities I wrote on purpose.

planetary-api is a deliberately vulnerable Flask API. Semgrep, Snyk, and Postman tests run in parallel and feed AWS Security Hub. A gate blocks on HIGH/CRITICAL findings — overriding it requires a conscious call.

http://blog.infosecmatters.net/2026/03/securing-aws-codepipeline-end-to-end.html

Would you build the gate differently?

---

## Variation 2

Three parallel scans. One hard gate. One human sign-off. Then it ships.

I wrote up the 10-stage CodePipeline I built for planetary-api — Semgrep SAST, Snyk SCA, and Postman security tests all feeding AWS Security Hub.

http://blog.infosecmatters.net/2026/03/securing-aws-codepipeline-end-to-end.html

What does your security gate look like?

---

## Variation 3

Most pipelines report vulnerabilities. Fewer actually block on them.

planetary-api's pipeline blocks on every HIGH/CRITICAL finding in Security Hub. Overriding requires an explicit SSM flag — auditable by design. Then a human approves before anything ships.

http://blog.infosecmatters.net/2026/03/securing-aws-codepipeline-end-to-end.html

Does your pipeline force that decision?
