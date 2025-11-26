# Identity Checker
  - Namespace: 18739
  - ID: web_inject
  - Type: custom
  - Category: Web Exploitation
  - Points: 200
  - Templatable: yes

## Description

Someone rewrote the login to “encrypt” passwords with a fixed key/nonce, but
they still jam your input straight into the SQL. Can you break in and steal the
flag anyway?

## Details

The service is running {{link_as("HTTP", "/", "here")}}.

For reference:

- Base URL: `{{http_base("HTTP")}}`
- Hostname: `{{server("HTTP")}}`
- Port: `{{port("HTTP")}}`

## Hints

- Login still builds SQL with string formatting. UNION your own SELECT into the
  temp table to pull other rows.
- The same nonce/key is reused for every password. Grab your own ciphertext,
  derive a keystream, and decrypt the admin password from the injected row.
- Once you’ve got the admin password, log in normally and call `/admin/flag`.

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

Register a user with a known password, then log in to get its password
ciphertext (returned in the JSON). Use `/login` with a UNION in the username to
select the admin row alongside your own ciphertext, so the decrypt check passes
but the admin ciphertext lands in the response. XOR your known plaintext with
your ciphertext to get the keystream, XOR that with the admin ciphertext to
recover the admin password. Log in as admin and POST to `/admin/flag`.


## Attributes
- author: gsavant
- event: 18739
