# Identity Checker

Identity Checker “encrypts” passwords with AES-GCM but reuses the same nonce and
copies your input straight into SQL. Use SQLi to pull the admin’s encrypted
password, use your own ciphertext to build the keystream, and decrypt the
admin’s password. Flow:

- Register any user with a known password.
- Log in as that user to get your password ciphertext.
- Send a UNION in the login username to pull the admin row; the response hands
  back the admin ciphertext.
- XOR to recover the admin password, log in as admin, and POST `/admin/flag`.
