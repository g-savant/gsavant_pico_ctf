# Identity Checker
  - Namespace: 18739
  - ID: web_inject
  - Type: custom
  - Category: Web Exploitation
  - Points: 200
  - Templatable: yes

## Description

Some intern set up a dumb login and registration field. How can we take it over
and log in ourselves?

## Details

The service is running {{link_as("HTTP", "/", "here")}}.

For reference:

- Base URL: `{{http_base("HTTP")}}`
- Hostname: `{{server("HTTP")}}`
- Port: `{{port("HTTP")}}`

## Hints

- Try crafting a username/password pair that closes the original `WHERE` clause
  and appends your own SQL.
- Once you control an admin session, hit `/admin/flag`.

## Tags
 - beginner

## Challenge Options

```yaml
cpus: 0.5
memory: 128m
ulimits:
  - nofile=128:128
diskquota: 64m
init: true
```

## Solution Overview

Use the login form to inject `'); INSERT INTO users(username,password,is_admin)`
payloads and create an account you know. Log in normally, keep the returned
session cookie, then call `/admin/flag` with that cookie to retrieve the
instance flag.


## Attributes
- author: gsavant
- event: 18739
