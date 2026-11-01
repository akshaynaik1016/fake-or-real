# Security implementation and boundaries

## Configuration and access

Production startup rejects missing/known-default/short JWT secrets and enabled demo
mode. Wildcard CORS origins are rejected. Development generates an ephemeral JWT
secret when one is not supplied; tokens then expire on process restart. Production
must configure a stable random secret. Docker Compose no longer supplies a known
JWT/database password. Database/cache published ports bind to loopback.

With local development DEMO_MODE=true, anonymous API access deliberately uses a
shared demonstration workspace. This is not suitable for public deployment.
Outside that mode, valid tokens and active users are required. Scan, investigation,
AI, comparison and report access checks ownership or ADMIN; admin routes require
ADMIN. `/auth/me` validates the caller and never returns the first user or creates
an administrator. Dashboard/history query only the caller's scans, except ADMIN.
The frontend authenticates and keeps its token in sessionStorage; production should
add a hardened session/CSRF strategy appropriate to its deployment.

POST routes use the existing per-process sliding limiter at 60/minute/IP. This is
not a distributed limiter, and trusted reverse-proxy/IP policy must be configured
before multi-worker public deployment. No Redis-backed queue or limiter is claimed.

## Network boundary

Untrusted URLs are parsed and checked for schemes, credentials and internal literal
addresses. URL structure inspection performs no fetch. DNS/TLS are disabled by
default. When TLS is enabled, all resolved addresses are checked for global routing;
the connection uses the validated IP with the original hostname for SNI/certificate
verification, preventing a second DNS lookup between check and connect. Unresolved
hosts may be inspected structurally but cannot be connected to by TLS. IP blocks
include private, loopback, link-local, multicast and reserved ranges.

Tavily uses a fixed HTTPS endpoint, an explicit timeout, no proxy environment,
no redirects and no arbitrary page fetching. Citation links reject dangerous
schemes, embedded credentials and local literal destinations; their DNS is not
resolved because the app never fetches those pages. A user clicking a third-party
source still visits an external site. Adding page fetching later requires validated
IP pinning and destination validation on every redirect, not only the initial URL.

## Documents and provider isolation

Uploads are size bounded before parser invocation, extension/magic-byte checked,
and never executed. WebP requires RIFF plus WEBP signature. Missing OCR is explicit;
there are no fabricated fallback documents or bounding boxes. PDF and image parsing
still need stronger resource isolation against decompression/page-count attacks for
public production use. File content is redacted before scan persistence and model
processing; evidence and research excerpts are also redacted. Logs record operations,
IDs and timing, not document bodies or provider secrets. Redaction is heuristic,
not a complete DLP system. See PRIVACY.md for retention and third-party disclosure.

Provider outputs are untrusted. Language output cannot contain risk scores,
verification decisions, new evidence or tool requests. Exact claims and citation
IDs are validated, but model paraphrases cannot be fully fact-checked by schema;
they remain unverified interpretations and are excluded from scoring and graph
relations. Uploaded/web instructions do not control tool execution. Only trusted
code chooses fixed follow-up tools, budgets and search terms.

## Remaining production work

See LIMITATIONS.md: distributed throttling, durable execution recovery, account
verification/recovery, deeper parser isolation, calibrated scoring, independent
source/offer authentication and a deployment penetration test remain pending.
No security certification, blanket prompt-injection immunity or cryptographically
signed Trust Passport is claimed.
