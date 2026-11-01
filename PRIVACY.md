# Privacy and retention

Uploaded images/PDFs are parsed in memory. Extracted redacted text, findings and
investigation snapshots are retained in the configured SQL database; they are not
automatically deleted. Existing imported history may contain older unredacted data.
The upgrade preserves it instead of silently rewriting/deleting records. Review
historical data and deploy a retention policy before accepting sensitive uploads.

Credential patterns (OTP, PIN, CVV, passwords, card/Aadhaar/PAN numbers) are redacted
before new scan storage and before model transmission. This heuristic is incomplete;
users should remove unnecessary personal information themselves. Sender addresses,
submitted domains, phone/payment identifiers can remain for investigation. No raw
password, OTP or payment credential should be intentionally included in submissions.
Application event logs contain route/scan metadata, not full document bodies.

No LLM data transfer occurs by default. A future explicitly configured adapter
receives a bounded redacted content excerpt and existing evidence copies for
interpretation only. Its operator must disclose provider retention terms.

When TAVILY_API_KEY is configured, organization-focused search terms are sent to
Tavily. Full document bodies and credentials are not sent as research queries.
Search excerpts, public source URLs, retrieval times and relevance are stored.
Configured Google Safe Browsing sends target URLs to Google; URLs can contain
sensitive query strings, so review provider configuration and submitted data.
Optional live DNS/TLS checks disclose destination names to network services.

Local demo mode is shared by design. Outside that mode, token/ownership checks
protect scans and saved reports. Saved report share tokens do not grant anonymous
access. PDFs are downloaded to the user's device and may include retained identity
or payment identifiers. The service does not make a cryptographic authenticity
claim for reports or Trust Passports. Database encryption, backups, deletion APIs,
retention automation and privacy-law compliance are deployment responsibilities.
