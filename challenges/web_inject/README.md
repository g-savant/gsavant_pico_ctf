# Identity Checker

Identity Checker is just a bad login portal: it copies your input straight
into a string-building SQL query, so you can inject arbitrary statements. The
flow now is:

- Push an `INSERT INTO users(...) VALUES (...)` payload into the password field.
- Log in as the account you just injected and keep the session cookie.
- Call `/admin/flag` with that cookie to grab the flag.
