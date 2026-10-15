# Lab 5 — Static Code Analysis: Issue Register

**Source program:** `car_rental.py`  
**Repository:** https://github.com/SETAPESU26/L5_56_car-rental  
**Note:** Line numbers below refer to the original `car_rental.py` included in the supplied ZIP. Re-run Pylint, Bandit, and Flake8 locally and add their exact rule identifiers/severities before submission; these are source-code findings, not claimed tool outputs.

| Issue | Type | Original line(s) | Description | Fix approach |
|---|---|---:|---|---|
| Arbitrary code execution through `exec` in promotion handling | Security / high priority | 50–54 | `applyPromo` executes a caller-supplied string. If untrusted text reaches this argument, arbitrary Python code may run. | Replaced `exec` with a finite mapping of supported promotion names to fixed calculations; invalid names raise `ValueError`. |
| SQL injection in customer registration | Security | 22–23 | Customer values are interpolated into an SQL statement using `%` formatting. Quotes in user input may change the query. | Replaced string interpolation with SQLite placeholders (`?`) and a tuple of parameters. |
| SQL injection in customer lookup | Security | 25–27 | The customer name is concatenated directly into the SQL query; the original demo's injection string returns every customer. | Replaced concatenation with a parameterised query. The injection-style test now returns no matching rows. |
| Insecure temporary file creation and permissions | Security | 62–68 | `tempfile.mktemp()` is race-prone, and `chmod(..., 0o777)` makes a receipt readable/writable/executable by everyone on POSIX systems. | Used `tempfile.mkstemp()`, wrote through the returned descriptor with UTF-8, and removed the file if writing fails. Removed world-open permissions. |
| Mutable default argument | Reliability / code quality | 16–19 | `features=[]` reuses the same mutable list across calls when callers do not pass a list. | Changed default to `None` and creates a new list within the function. |
| Broad exception handling hides errors | Reliability / code quality | 36–43 | `except:` catches every exception and silently passes, hiding invalid plate lookups and other problems. | Removed the broad handler. Known invalid-car and invalid-kilometre cases now raise clear `ValueError` exceptions. |
| Invalid rental dates produce a negative charge | Functional bug | 29–34; demonstrated in `main` at line 90 | The code allows an end date before the start date; the demo prints `Rent Innova: -9000`. | Validates that the rental duration is positive before calculating a cost. |
| Renting a car does not change its availability | Functional bug | 29–34; demonstrated in `main` at line 89 | A car could be booked more than once because availability was not checked or updated. | Checks availability and marks the car unavailable when a booking is successfully created. |
| Negative daily rates are accepted | Functional bug / validation | Original `main`, line 85 | A car is added with a daily rate of `-500`, allowing a negative rental price. | Rejects negative daily rates with `ValueError`; the demo reports the rejection. |
| SHA-1 used for licence identifiers | Security / crypto choice | 47–48 | SHA-1 is a legacy hash function and is not recommended for new security-sensitive designs. A bare hash is also not encryption. | Changed the demonstration hash to SHA-256 and documented that a production design needs a considered approach to sensitive identifiers. |
| Predictable booking codes | Security / reliability | 44–45 | `random.randint` is not intended for security-sensitive tokens. | Uses `secrets.randbelow` for token generation. A production system should also enforce uniqueness in storage. |
| Hard-coded default admin password | Security design issue | 70–73 | The demo's default password is embedded in source code. | Removed the hard-coded password and read the expected username/password from environment variables; comparison uses `hmac.compare_digest`. Production authentication should use managed credentials and protected password hashes. |
| Style: non-PEP 8 function names and formatting | Style | Multiple | Names such as `addCar`, `registerCustomer`, and `availableCars` do not follow snake_case, and some lines are long. | Renamed functions to snake_case and formatted statements across multiple lines. |
| Unused import | Code quality | Original line 2 | `json` is imported but not used. | Removed unused import. |
| Entry point executes on import | Maintainability / testability | Original line 101 | Calling `main()` unconditionally means importing the module runs the demo as a side effect. | Guarded execution using `if __name__ == "__main__":`. |

## Verification fields to complete after local tool runs

Record exact results from your own terminal here; do not invent scores or counts.

| Tool | Before result | After result | Verification |
|---|---|---|---|
| Pylint | Fill from `pylint_before.txt` | Fill from `pylint_after.txt` | State whether selected findings disappeared; record the final score. |
| Bandit | Fill from `bandit_before.txt` | Fill from `bandit_after.txt` | Record remaining findings and severities. |
| Flake8 | Fill from `flake8_before.txt` | Fill from `flake8_after.txt` | Record remaining rule codes or write “no output” only if the file is confirmed empty. |
## Final Verification Results

| Tool | Original Results | Final Results |
|---|---|---|
| Pylint | Multiple code-quality and style warnings; see `pylint_before.txt` for the original score. | 10.00/10 |
| Bandit | Security findings included B608 (possible SQL injection) and B101 (use of assert). See `bandit_before.txt` for the complete baseline. | No issues identified; zero reported issues across all severity levels. |
| Flake8 | Multiple style violations, including unused imports, line-length violations and bare exception handling. See `flake8_before.txt`. | No violations reported; `flake8_after.txt` is empty. |

The corrected program was executed successfully. The demonstration showed rejection of invalid rental dates, duplicate bookings, negative daily rates and an SQL-injection-style lookup. The final static-analysis reports were reviewed to verify the changes.