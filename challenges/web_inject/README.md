# Identity Checker

Identity Checker is just a bad login portal: it copies your input straight
into a string-building SQL query, so you can inject arbitrary statements. The
flow is basically:

- Push an `INSERT INTO users(...) VALUES (...)` payload into the password field.
- Log in as the account you just injected and note the returned token.
- Call `/admin/flag` with that token to grab the flag.
