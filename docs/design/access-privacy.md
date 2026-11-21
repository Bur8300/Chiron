# Access and Privacy Design (WBS-2.1)

| Field | Details |
|---|---|
| WBS activity | WBS-2.1 Access and privacy design (task T-02, issue #20) |
| Owner | Burak Emre Polat |
| Reviewer | Metin Furkan Amarat |
| Used by | WBS-2.2 authorization tests (Berkay), WBS-2.3 authentication and role-based access (Burak), WBS-2.4 account pages (Faruk), WBS-9.1 deployment design (Berkay), WBS-12.x mobile application |
| Status | Draft, 21.11.2026 |

This note describes how Chiron controls access and how it handles personal data (KVKK).
It builds on the [architecture note](architecture.md), the [API contract](../../contracts/openapi.yaml), the [portal data design](portal-data.md) and the database design (`database.md`, PR #48).

Requirements: FR-02 to FR-09, FR-17, FR-40, NFR-01 to NFR-07.
Items marked **Proposal** are not decided yet. The review of this PR decides them.

## 1. Decisions

| Decision | Section | Who |
|---|---|---|
| Passwords have 8 to 128 characters. No other character rules. The API refuses a common password and a password that is the same as the portal ID. | 2 | Burak, 21.11.2026 |
| The web application keeps the access token in memory and the refresh token in an `HttpOnly` cookie. The mobile applications keep the refresh token in secure storage. | 3 | Burak, 21.11.2026 |
| A refresh token is valid for 30 days. Each refresh gives a new token (rotation). | 3 | Burak, 21.11.2026 |
| If a revoked refresh token is used again, the API revokes all refresh tokens of the user (reuse detection). | 3 | Burak, 21.11.2026 (proposal by Metin) |
| Login and activate have a rate limit for each portal ID and for each IP address. | 4 | Burak, 21.11.2026 (proposal by Metin) |
| CORS allows only a fixed list of origins. | 5 | Burak, 21.11.2026 |
| An account deletion deletes the database rows at once. A background job deletes the files. | 7.4 | Burak, 21.11.2026 |
| A later import adds a deleted user again as a new account. Chiron keeps no list of deleted users. | 7.4 | Burak, 16.11.2026 (database design) |

## 2. Passwords (FR-02, FR-03, NFR-01)

- **Length:** 8 to 128 characters. The API counts Unicode characters, so Turkish letters count as one character.
- **No composition rules.** Chiron does not ask for upper case letters, digits or symbols. NIST SP 800-63B does not recommend these rules. They make users choose passwords that are easy to guess.
- **Refused passwords** (`422 weak_password`):
  - a password from a list of common passwords,
  - a password that is the same as the portal ID (case is not important).
- **Hash:** Argon2id with a random salt for each password (NFR-01). The database keeps only the hash (`users.password_hash`).
- **Proposal:** the list of common passwords is the 10,000 most common passwords of the SecLists project, with common Turkish passwords added. The file is in the backend code (WBS-2.3).

## 3. Sessions and tokens (FR-03, FR-04, FR-40)

### 3.1 Tokens

| Token | Content | Lifetime | Where the server keeps it |
|---|---|---|---|
| Access token | JWT with the user ID (`sub`), the role and the expiry time | 15 minutes | Not kept. The API checks the signature. |
| Refresh token | Random value (256 bits) | 30 days | `refresh_tokens.token_hash` (SHA-256 of the value) |

- The API signs the access token with a secret key. The key comes from an environment variable or a GCP secret (NFR-02).
- The role in the access token is only for the client. The API reads the role and the assignments from the database on every call (NFR-03).

### 3.2 Web application

1. The web application sends `client: web` to `POST /auth/login` or `POST /auth/activate`.
2. The API returns the access token in the body. It puts the refresh token in the `chiron_refresh` cookie:
   `HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth; Max-Age=2592000` (30 days).
3. The web application keeps the access token only in memory (a JavaScript variable). It never writes a token to `localStorage` or `sessionStorage`.
4. When the access token expires, or when the page loads again, the web application sends `POST /auth/refresh` with no body. The browser sends the cookie.
5. `POST /auth/logout` revokes the refresh token and deletes the cookie.

JavaScript cannot read an `HttpOnly` cookie. An XSS attack cannot steal the refresh token.

**Same origin is necessary.** The web application and the API must have the same origin (for example `https://chiron.example/` and `https://chiron.example/api/v1/`). Browsers block cookies between two different `*.run.app` addresses, because each address is a different site. WBS-9.1 must serve the frontend and the API from one origin (for example with a load balancer or with the backend serving the frontend files).

**CSRF.** `SameSite=Strict` stops the browser from sending the cookie with requests from other sites. The cookie path is only `/api/v1/auth`, so the cookie never goes to other endpoints. All other endpoints use the access token in the `Authorization` header, which the browser does not send by itself.

### 3.3 Mobile applications

1. The application sends `client: mobile` (the default).
2. The API returns both tokens in the body.
3. The application keeps the refresh token in the secure storage of the phone (Keychain on iOS, Keystore on Android) and the access token in memory (FR-40).
4. The application sends the refresh token in the body of `POST /auth/refresh` and `POST /auth/logout`.
5. On logout, the application deletes the refresh token from secure storage (FR-40).

### 3.4 Rotation and reuse detection

- Each refresh revokes the old refresh token and gives a new one. The new token belongs to the same **token family** as the old one.
- A login or an activation starts a new token family.
- If a revoked refresh token is used again, someone else probably has a copy. The API then revokes **all** refresh tokens of the user and returns `401`. All devices of the user must log in again.
- Logout revokes only the token family of that device.

**Database change (WBS-2.3):** `refresh_tokens` needs a `family_id` column. The database design (PR #48) does not have it yet.

## 4. Rate limits (FR-03, FR-05)

| Limit | Key | Rule | Applies to |
|---|---|---|---|
| Portal ID | The portal ID in the request | After 5 failed attempts in 15 minutes, the API refuses all attempts for this portal ID for 15 minutes. A successful login resets the count. | `POST /auth/login`, `POST /auth/activate` |
| IP address | The IP address of the client | At most 20 attempts in 1 minute, failed or successful | `POST /auth/login`, `POST /auth/activate` |

- Redis keeps the counters. They expire by themselves.
- When a limit is reached, the API returns `429 too_many_attempts` with a `Retry-After` header.
- The API counts an unknown portal ID like a known one. The answer does not tell which portal IDs exist (FR-05).
- The IP limit is high because all students of a class can use the same IP address at school.
- **Known risk (accepted):** the lock is for the portal ID, not for the person who tries. Classmates know the portal IDs of each other. A person can block the login of another student for 15 minutes with 5 wrong passwords, and can do this again every 15 minutes (for example just before an exam). The mobile applications and the web application keep a logged-in user logged in (section 3), so the lock stops only new logins. A longer lock would make the risk worse. Other solutions are an increasing delay after each failed attempt instead of a lock, or a lock only for new devices or IP addresses. The team discusses them together with the activation code (section 8).
- On Cloud Run, the API takes the client IP address from the `X-Forwarded-For` header that Google's front end adds. WBS-9.1 must confirm this.

## 5. CORS

- The web application uses the same origin as the API, so it does not need CORS.
- CORS allows only these origins:

| Origin | Client |
|---|---|
| `capacitor://localhost` | iOS application |
| `https://localhost` | Android application |
| `http://localhost:5173` | Web development server (development only) |

- The list comes from the `CORS_ORIGINS` environment variable. The production configuration does not have the development origin.
- `allow_credentials` is off. The mobile applications send the access token in the `Authorization` header, not in a cookie.
- **Proposal:** the web development server sends API calls through the Vite proxy. Then the development setup has the same origin like production, and the cookie works.

## 6. Access control (FR-06, FR-07, FR-08, NFR-03)

### 6.1 Rules

- The API checks the access token on every call, except the public operations: `/health`, activate, login, refresh and logout.
- The API then checks the role (`x-roles` in the contract). A wrong role gets `403 forbidden`.
- The API then checks the data (`x-access` in the contract):
  - `self`: only the data of the logged-in user.
  - `own`: only resources that the logged-in student owns. For a course: the student is enrolled in the course.
  - `assigned`: only students, teachers and data in the assignment group of the user.
  - `none`: no data check.
- The client hides pages that the role cannot use (FR-06). This is not an access control. The API always checks.
- **Proposal:** for a resource of another user (for example `GET /sources/{id}` of another student), the API returns `404`, not `403`. This does not tell which IDs exist. The contract already does this for `source_ids` (`source_not_found`).

### 6.2 Access matrix

| Data | Student | Teacher | Administrator |
|---|---|---|---|
| Own account (`/me`, token usage, logout) | Yes | Yes (no token usage) | Yes (no token usage) |
| Courses, units, topics, own grades | Own courses | No | No |
| Sources, files, passages | Own sources | No | No |
| Questions, summaries, quizzes, jobs | Own | No | Own import jobs |
| Study plan | Own | No | No |
| Per-topic success rates of students | No | Assigned students, own subject only | Assigned students, all subjects |
| Token usage of students | No | Assigned students | Assigned students |
| Assignments | No | No | Own group: move students to teachers and to administrators, move teachers to administrators |
| Portal import | No | No | Yes |
| Delete an account | No | No | Students and teachers of own group. Not administrators. |

- **Nobody** sees the uploaded files, the questions or the answers of another user. Teachers and administrators see only success rates and token totals.
- "Assigned students" of a teacher come from `student_teachers`. "Assigned students" of an administrator come from `student_administrators` (architecture note, section 4.1).

WBS-2.2 writes one authorization test for each row and each role, including access to another user's data.

## 7. Personal data (KVKK, NFR-04 to NFR-07)

### 7.1 Data that Chiron keeps

| Data | Purpose | Requirements | Kept until |
|---|---|---|---|
| Portal ID, first name, last name, role, class | Login and showing the user | FR-02, FR-03, FR-10 | Account deletion |
| Password hash, activation time | Login | FR-02, FR-03, NFR-01 | Account deletion |
| Refresh token hashes | Sessions | FR-04, FR-40 | Expiry or revocation. **Proposal:** a daily job deletes expired and revoked tokens. |
| Assignments | Access control and dashboards | FR-07, FR-08 | Account deletion |
| Grades and the time of the last grade read | Success rates and study plans | FR-11, FR-27 | Replaced at each grade read; account deletion |
| Uploaded files, passages and embeddings | Answers, summaries and quizzes | FR-13 to FR-18 | Source deletion or account deletion |
| Questions and answers | Question history | FR-20 | Account deletion. A source deletion deletes the citations of the source. |
| Summaries, quizzes, quiz answers and scores | Study material | FR-21 to FR-24 | Account deletion |
| Study plans | Weekly plan | FR-29, FR-30 | Account deletion |
| Token usage records | Dashboards and the monthly limit | FR-34, FR-35, FR-37 | Account deletion |

Chiron does not keep e-mail addresses, national ID numbers, birth dates or phone numbers. The portal data does not have them (portal data design, section 3.2).

### 7.2 Data that goes to AI providers

The AI providers receive the question, the passages of the selected sources and the source text for summaries, quizzes and study steps.

- **Proposal:** the gateway sends no name, portal ID or user ID to a provider. It records the token usage for the student inside Chiron (FR-35).
- Uploaded files can have personal data in them. The student chooses what to upload.
- The providers are outside Turkey. WBS-8.1 must choose providers that do not use API data for training. The team must write this in the gateway design.

### 7.3 Logs

- **Proposal:** the logs do not have passwords, tokens, file contents, questions or answers. They have user IDs, endpoints, status codes and times.

### 7.4 Deletion (FR-09, FR-17, NFR-06)

- **Account deletion:**
  1. The API deletes the user in one transaction. The database deletes all rows of the user (`ON DELETE CASCADE`, database design section 3). The user cannot log in after this.
  2. The API starts a storage cleanup job with the storage keys of the user's files. The job has no owner (`user_id` is null), so the account deletion does not delete the job.
  3. The job deletes the files from Cloud Storage. If it fails, it runs again.
  4. The API returns `204` after step 2. The contract does not change.
- **Source deletion (FR-17):** the same steps for one source.
- **Database change (WBS-2.3):** `jobs.type` needs the value `storage_cleanup`.
- **Later imports:** a later import adds a deleted user again as a new account that is not active (database design, section 1).

### 7.5 Development and test data

- Only the mock portal data. No real student data (NFR-05).
- Tests use made-up files without personal data.

## 8. Open points

| Point | Status | Decides in |
|---|---|---|
| Account takeover at activation. With only the portal ID, a person who knows the portal ID of another user can activate that account first and see the grades of that user. A one-time activation code for each user in the portal data stops this. | Team decision. It changes FR-02 or adds a new requirement. | Team; Requirements Analysis (Hasan) |
| A person can lock the login of another student with wrong passwords (section 4) | Accepted risk. Alternatives: increasing delay, or a lock only for new devices or IP addresses. | Team, together with the activation code |
| The list of common passwords | Proposal in section 2 | Review, WBS-2.3 |
| `404` or `403` for a resource of another user | Proposal in section 6.1 | Review |
| One origin for the web application and the API | Needed for the cookie (section 3.2) | WBS-9.1 (Berkay) |
| Client IP address behind the Cloud Run front end | Needed for the IP limit (section 4) | WBS-9.1 (Berkay) |
| AI providers that do not use API data for training | Needed for KVKK (section 7.2) | WBS-8.1 (Burak) |
| GCP region of the database and the files | Not set | WBS-9.1 (Berkay) |

## 9. Changes for other activities

| Change | Activity |
|---|---|
| Contract: `client` field, `chiron_refresh` cookie, `429` on login and activate, password length (this PR) | WBS-1.1 (done here) |
| Migration: `refresh_tokens.family_id`, job type `storage_cleanup` | WBS-2.3 |
| Authorization tests for the matrix in section 6.2 | WBS-2.2 |
| Web application: tokens in memory, `client: web`, refresh on page load, Vite proxy | WBS-1.6, WBS-2.4 |
| Mobile applications: secure storage, `client: mobile` | WBS-12.3 |
| One origin, client IP address, region | WBS-9.1 |
| Providers that do not train on API data | WBS-8.1 |
