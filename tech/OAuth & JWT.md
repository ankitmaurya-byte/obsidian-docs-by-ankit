# OAuth & JWT

## What is OAuth 2.0
```
overview:
  full_name: Open Authorization 2.0
  type: Authorization framework (NOT authentication)
  purpose: Let users grant third-party apps limited access to their resources without sharing passwords
  specification: RFC 6749
  key_distinction: |
    OAuth = Authorization (what you can access)
    OpenID Connect (OIDC) = Authentication layer on top of OAuth (who you are)

  roles:
    resource_owner: The user who owns the data
    client: The app requesting access (your app)
    authorization_server: Issues tokens (Google, GitHub, Auth0)
    resource_server: Hosts the protected resources (API)

  tokens:
    access_token:
      purpose: Short-lived token to access resources
      lifetime: Minutes to hours (e.g., 15 min - 1 hour)
      sent_as: "Authorization: Bearer <token>"
    refresh_token:
      purpose: Long-lived token to get new access tokens without re-login
      lifetime: Days to months
      storage: Server-side or secure HTTP-only cookie
      note: Not all flows issue refresh tokens
```

## OAuth 2.0 Flows

### Authorization Code Flow (Most Common)
```
authorization_code_flow:
  use_when: Server-side web apps (confidential clients)
  most_secure: Yes, recommended for most applications

  steps:
    1_redirect_to_auth_server:
      description: App redirects user to authorization server
      url: |
        GET https://auth.example.com/authorize?
          response_type=code&
          client_id=YOUR_CLIENT_ID&
          redirect_uri=https://yourapp.com/callback&
          scope=read write&
          state=random_csrf_token

    2_user_authenticates:
      description: User logs in and approves the requested permissions
      happens_at: Authorization server (Google login page, etc.)

    3_auth_server_redirects_back:
      description: Auth server redirects to your callback with an authorization code
      url: "https://yourapp.com/callback?code=AUTH_CODE&state=random_csrf_token"
      note: Authorization code is single-use, expires in ~10 minutes

    4_exchange_code_for_tokens:
      description: Your server exchanges the code for tokens (server-to-server)
      request: |
        POST https://auth.example.com/token
        Content-Type: application/x-www-form-urlencoded

        grant_type=authorization_code&
        code=AUTH_CODE&
        redirect_uri=https://yourapp.com/callback&
        client_id=YOUR_CLIENT_ID&
        client_secret=YOUR_CLIENT_SECRET

    5_receive_tokens:
      description: Auth server returns access token (and optionally refresh token)
      response: |
        {
          "access_token": "eyJhbGci...",
          "token_type": "Bearer",
          "expires_in": 3600,
          "refresh_token": "dGhpcyBpcyBh..."
        }

    6_use_access_token:
      description: Call resource API with the access token
      header: "Authorization: Bearer eyJhbGci..."
```

### Authorization Code + PKCE (Public Clients)
```
pkce_flow:
  full_name: Proof Key for Code Exchange
  pronounced: "pixy"
  rfc: RFC 7636
  use_when: SPAs, mobile apps, CLI tools (public clients that cannot safely store a client_secret)
  recommended_for: All public clients, now recommended even for server apps

  how_it_works:
    1_generate_verifier:
      description: Client generates a random string (code_verifier)
      example: "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"

    2_create_challenge:
      description: Hash the verifier to create code_challenge
      method: "code_challenge = BASE64URL(SHA256(code_verifier))"

    3_send_challenge_in_auth_request:
      url: |
        GET https://auth.example.com/authorize?
          response_type=code&
          client_id=YOUR_CLIENT_ID&
          redirect_uri=https://yourapp.com/callback&
          scope=read&
          state=random_csrf_token&
          code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&
          code_challenge_method=S256

    4_exchange_with_verifier:
      description: When exchanging code for tokens, send the original verifier
      request: |
        POST https://auth.example.com/token

        grant_type=authorization_code&
        code=AUTH_CODE&
        redirect_uri=https://yourapp.com/callback&
        client_id=YOUR_CLIENT_ID&
        code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk

    5_server_verifies:
      description: Auth server hashes the verifier and compares with the stored challenge
      ensures: Only the client that started the flow can exchange the code
```

### Client Credentials Flow
```
client_credentials_flow:
  use_when: Machine-to-machine (M2M) communication, no user involved
  example: Backend service calling another backend service, cron jobs

  steps:
    1_request_token:
      description: Client authenticates directly with client_id and client_secret
      request: |
        POST https://auth.example.com/token
        Content-Type: application/x-www-form-urlencoded

        grant_type=client_credentials&
        client_id=YOUR_CLIENT_ID&
        client_secret=YOUR_CLIENT_SECRET&
        scope=read write

    2_receive_token:
      response: |
        {
          "access_token": "eyJhbGci...",
          "token_type": "Bearer",
          "expires_in": 3600
        }

  note: No refresh token issued (just request a new access token when it expires)
  no_user: This flow does not involve a user, only service accounts
```

## What is JWT
```
jwt_overview:
  full_name: JSON Web Token
  pronounced: "jot"
  specification: RFC 7519
  type: Compact, self-contained token for securely transmitting claims
  format: "header.payload.signature (three Base64URL-encoded parts)"
  key_property: Stateless (server does not need to store the token)

structure:
  header:
    description: Metadata about the token
    example: |
      {
        "alg": "HS256",
        "typ": "JWT"
      }

  payload:
    description: Claims (data) about the user/entity
    standard_claims:
      iss: "Issuer (who created the token)"
      sub: "Subject (user ID)"
      aud: "Audience (intended recipient)"
      exp: "Expiration time (Unix timestamp)"
      iat: "Issued at (Unix timestamp)"
      nbf: "Not before (Unix timestamp)"
      jti: "JWT ID (unique identifier)"
    custom_claims: "Any additional data (role, email, etc.)"
    example: |
      {
        "sub": "user123",
        "name": "Ankit",
        "role": "admin",
        "iat": 1700000000,
        "exp": 1700003600
      }

  signature:
    purpose: Ensures the token has not been tampered with
    hmac_formula: "HMACSHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), secret)"
    rsa_formula: "RSA-SHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), privateKey)"

  algorithms:
    symmetric:
      - "HS256 (HMAC + SHA-256): shared secret, fast, good for single service"
      - "HS384, HS512: stronger variants"
    asymmetric:
      - "RS256 (RSA + SHA-256): private key signs, public key verifies"
      - "ES256 (ECDSA + SHA-256): smaller keys, faster than RSA"
      - "Best for: microservices (auth service signs, other services verify with public key)"

  important_notes:
    - JWT payload is NOT encrypted, only Base64-encoded (anyone can read it)
    - Use HTTPS to prevent token interception
    - Never put secrets in the payload
    - For encrypted tokens, use JWE (JSON Web Encryption)
```

## Session Auth vs Token Auth
```
comparison:
  session_based:
    how_it_works:
      1: "User logs in, server creates a session (stored in memory/DB/Redis)"
      2: "Server sends session ID as a cookie"
      3: "Browser sends cookie with every request"
      4: "Server looks up session ID to find user data"
    storage: Server-side (memory, Redis, database)
    stateful: Yes (server must store session state)
    scalability: Needs sticky sessions or shared session store
    revocation: Easy (just delete the session)
    csrf: Vulnerable (cookies sent automatically)
    best_for: Traditional web apps, server-rendered pages

  token_based:
    how_it_works:
      1: "User logs in, server creates and signs a JWT"
      2: "Server sends JWT to client"
      3: "Client stores JWT (localStorage, cookie, memory)"
      4: "Client sends JWT in Authorization header"
      5: "Server verifies signature, trusts the claims inside"
    storage: Client-side
    stateless: Yes (server stores nothing, just verifies signature)
    scalability: Excellent (any server can verify the token)
    revocation: Hard (token is valid until it expires)
    csrf: Not vulnerable if stored in memory/localStorage (not cookies)
    best_for: SPAs, mobile apps, microservices, APIs

  token_revocation_strategies:
    - Short expiration + refresh tokens
    - Token blacklist in Redis (check on every request)
    - Token versioning (increment user's token version, reject old ones)
```

## Refresh Token Flow
```
refresh_flow:
  why: Access tokens are short-lived for security, refresh tokens avoid re-login

  flow:
    1: "Client uses access token for API requests"
    2: "Access token expires (e.g., after 15 minutes)"
    3: "Client sends refresh token to auth server"
    4: "Auth server validates refresh token and issues new access + refresh token pair"
    5: "Old refresh token is invalidated (rotation)"

  refresh_request: |
    POST https://auth.example.com/token
    Content-Type: application/x-www-form-urlencoded

    grant_type=refresh_token&
    refresh_token=REFRESH_TOKEN&
    client_id=YOUR_CLIENT_ID

  token_rotation:
    description: Each refresh token can only be used once
    purpose: If a refresh token is stolen, reuse is detected
    detection: If old refresh token is used, revoke all tokens for that user

  storage_best_practices:
    access_token: "In-memory variable (JS) or short-lived cookie"
    refresh_token: "HTTP-only, Secure, SameSite cookie"
    never: "Never store tokens in localStorage for high-security apps"
```

## Code Examples

### JWT Middleware in Go
```go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
    "strings"
    "time"

    "github.com/golang-jwt/jwt/v5"
)

var jwtSecret = []byte("your-256-bit-secret-keep-it-safe")

type Claims struct {
    UserID string `json:"user_id"`
    Role   string `json:"role"`
    jwt.RegisteredClaims
}

// Generate JWT token
func generateToken(userID, role string) (string, error) {
    claims := Claims{
        UserID: userID,
        Role:   role,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(15 * time.Minute)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            Issuer:    "myapp",
        },
    }
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(jwtSecret)
}

// JWT authentication middleware
func authMiddleware(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        authHeader := r.Header.Get("Authorization")
        if authHeader == "" {
            http.Error(w, `{"error":"missing authorization header"}`, http.StatusUnauthorized)
            return
        }

        tokenString := strings.TrimPrefix(authHeader, "Bearer ")

        claims := &Claims{}
        token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
            if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
                return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
            }
            return jwtSecret, nil
        })

        if err != nil || !token.Valid {
            http.Error(w, `{"error":"invalid or expired token"}`, http.StatusUnauthorized)
            return
        }

        // Token is valid, set user info in header for downstream handlers
        r.Header.Set("X-User-ID", claims.UserID)
        r.Header.Set("X-User-Role", claims.Role)
        next(w, r)
    }
}

// Login handler (issues tokens)
func loginHandler(w http.ResponseWriter, r *http.Request) {
    // In production: validate username/password against database
    var req struct {
        Username string `json:"username"`
        Password string `json:"password"`
    }
    json.NewDecoder(r.Body).Decode(&req)

    // Dummy check
    if req.Username != "ankit" || req.Password != "password123" {
        http.Error(w, `{"error":"invalid credentials"}`, http.StatusUnauthorized)
        return
    }

    accessToken, _ := generateToken("user123", "admin")
    // In production: also generate a refresh token and store in DB

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{
        "access_token": accessToken,
        "token_type":   "Bearer",
        "expires_in":   "900",
    })
}

// Protected endpoint
func protectedHandler(w http.ResponseWriter, r *http.Request) {
    userID := r.Header.Get("X-User-ID")
    role := r.Header.Get("X-User-Role")

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{
        "message": "Welcome to the protected route",
        "user_id": userID,
        "role":    role,
    })
}

func main() {
    http.HandleFunc("/login", loginHandler)
    http.HandleFunc("/protected", authMiddleware(protectedHandler))

    fmt.Println("Server on :8080")
    http.ListenAndServe(":8080", nil)
}
```

### JWT + OAuth in Node.js (Express + Passport)
```javascript
const express = require('express');
const jwt = require('jsonwebtoken');
const passport = require('passport');
const { Strategy: JwtStrategy, ExtractJwt } = require('passport-jwt');

const app = express();
app.use(express.json());

const JWT_SECRET = 'your-256-bit-secret-keep-it-safe';

// Configure Passport JWT strategy
passport.use(new JwtStrategy({
    jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
    secretOrKey: JWT_SECRET,
    issuer: 'myapp',
}, (payload, done) => {
    // payload contains decoded JWT claims
    // In production: look up user in database
    return done(null, { id: payload.user_id, role: payload.role });
}));

app.use(passport.initialize());

// Login endpoint (issue JWT)
app.post('/login', (req, res) => {
    const { username, password } = req.body;

    // In production: validate against database
    if (username !== 'ankit' || password !== 'password123') {
        return res.status(401).json({ error: 'Invalid credentials' });
    }

    const accessToken = jwt.sign(
        { user_id: 'user123', role: 'admin' },
        JWT_SECRET,
        { expiresIn: '15m', issuer: 'myapp' }
    );

    const refreshToken = jwt.sign(
        { user_id: 'user123', type: 'refresh' },
        JWT_SECRET,
        { expiresIn: '7d', issuer: 'myapp' }
    );

    res.json({
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'Bearer',
        expires_in: 900,
    });
});

// Refresh token endpoint
app.post('/refresh', (req, res) => {
    const { refresh_token } = req.body;

    try {
        const payload = jwt.verify(refresh_token, JWT_SECRET);
        if (payload.type !== 'refresh') {
            return res.status(401).json({ error: 'Invalid token type' });
        }

        const newAccessToken = jwt.sign(
            { user_id: payload.user_id, role: 'admin' },
            JWT_SECRET,
            { expiresIn: '15m', issuer: 'myapp' }
        );

        res.json({ access_token: newAccessToken, expires_in: 900 });
    } catch (err) {
        res.status(401).json({ error: 'Invalid refresh token' });
    }
});

// Protected route using Passport
app.get('/protected',
    passport.authenticate('jwt', { session: false }),
    (req, res) => {
        res.json({
            message: 'Welcome to the protected route',
            user: req.user,
        });
    }
);

app.listen(8080, () => console.log('Server on :8080'));
```

### OAuth 2.0 Authorization Code Flow in Go
```go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
    "net/url"
    "os"

    "golang.org/x/oauth2"
    "golang.org/x/oauth2/github"
)

var oauthConfig = &oauth2.Config{
    ClientID:     os.Getenv("GITHUB_CLIENT_ID"),
    ClientSecret: os.Getenv("GITHUB_CLIENT_SECRET"),
    RedirectURL:  "http://localhost:8080/callback",
    Scopes:       []string{"read:user", "user:email"},
    Endpoint:     github.Endpoint,
}

// Step 1: Redirect user to GitHub login
func loginHandler(w http.ResponseWriter, r *http.Request) {
    state := "random-csrf-token" // In production: generate random state and store in session
    url := oauthConfig.AuthCodeURL(state)
    http.Redirect(w, r, url, http.StatusTemporaryRedirect)
}

// Step 2: Handle callback with authorization code
func callbackHandler(w http.ResponseWriter, r *http.Request) {
    state := r.URL.Query().Get("state")
    if state != "random-csrf-token" {
        http.Error(w, "Invalid state", http.StatusBadRequest)
        return
    }

    code := r.URL.Query().Get("code")

    // Step 3: Exchange code for token
    token, err := oauthConfig.Exchange(r.Context(), code)
    if err != nil {
        http.Error(w, "Token exchange failed: "+err.Error(), http.StatusInternalServerError)
        return
    }

    // Step 4: Use token to get user info
    client := oauthConfig.Client(r.Context(), token)
    resp, err := client.Get("https://api.github.com/user")
    if err != nil {
        http.Error(w, "Failed to get user info", http.StatusInternalServerError)
        return
    }
    defer resp.Body.Close()

    var user map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&user)

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}

func main() {
    http.HandleFunc("/login", loginHandler)
    http.HandleFunc("/callback", callbackHandler)
    fmt.Println("Visit http://localhost:8080/login")
    http.ListenAndServe(":8080", nil)
}
```

## Tags
```
tags:
  - oauth
  - oauth2
  - jwt
  - authentication
  - authorization
  - tokens
  - access-token
  - refresh-token
  - pkce
  - security
```
