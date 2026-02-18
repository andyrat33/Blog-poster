# LinkedIn Posts — Building a Flask API for security training (planetary-api)

---

## Variation 1

Most AppSec training uses slides. I built a live target instead.

planetary-api: Flask API, every endpoint has a vulnerable version and a secure fix. SQL injection, SSRF, path traversal — all intentional. `docker compose up`, break it, check the fix.

http://blog.infosecmatters.net/2026/02/building-flask-api-for-security.html

What does your AppSec training look like?

---

## Variation 2

I got tired of explaining SQL injection in theory.

planetary-api: a Flask API where broken endpoints sit next to their fixed versions. One `docker compose up` and you've got a live target.

http://blog.infosecmatters.net/2026/02/building-flask-api-for-security.html

Do engineers on your team learn security by reading docs or breaking things?

---

## Variation 3

Star Trek planets. Flask. Deliberate SQL injection.

planetary-api: a REST API where the vulnerable endpoint and the secure fix live side by side. Engineers see both. Docker gets it running in minutes.

http://blog.infosecmatters.net/2026/02/building-flask-api-for-security.html

Would a lab like this work for your team?
