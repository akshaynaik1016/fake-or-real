import ssl
import socket
from datetime import datetime, timezone
from typing import Dict, Any
from app.core.config import settings
from app.security.ssrf import validate_and_resolve_url

def analyze_ssl_certificate(hostname: str, port: int = 443, synthetic: bool = False) -> Dict[str, Any]:
    """
    Analyzes SSL/TLS certificate for the given hostname.
    Extracts validity dates, issuer, subject, and attaches the critical cybersecurity disclaimer:
    'HTTPS does not prove that a website is trustworthy. A malicious website can still use a valid HTTPS certificate.'
    """
    clean_host = hostname.lower().strip()
    
    # Handle known demo / offline domains gracefully
    if synthetic and clean_host in ["microsoft-careers-india.xyz", "scholarship-portal-gov.online", "quick-internships-direct.top"]:
        return {
            "is_demo_source": True,
            "has_ssl": True,
            "is_valid": True,
            "issuer": "Let's Encrypt Authority X3 (Automated DV Certificate)",
            "subject": clean_host,
            "valid_from": "2026-10-01T00:00:00Z",
            "valid_until": "2026-12-30T23:59:59Z",
            "days_remaining": 70,
            "tls_version": "TLSv1.3",
            "is_wildcard": False,
            "critical_disclaimer": "HTTPS does not prove that a website is trustworthy. A malicious website can still use a valid HTTPS certificate.",
            "flags": [
                {
                    "code": "DV_CERTIFICATE_ONLY",
                    "severity": "low",
                    "message": "Domain uses a basic Domain Validated (DV) certificate.",
                    "detail": "DV certificates only verify control of the domain name, not the organization's legal identity."
                }
            ]
        }
        
    if not settings.NETWORK_SCANNERS_ENABLED:
        return {"has_ssl": False, "is_valid": False, "issuer": None, "flags": [], "status": "UNAVAILABLE"}
    try:
        safe, _, addresses = validate_and_resolve_url(f"https://{clean_host}:{port}")
        if not safe or not addresses:
            raise ValueError("Destination could not be validated")
        context = ssl.create_default_context()
        context.timeout = 2.5
        with socket.create_connection((addresses[0], port), timeout=2.5) as sock:
            with context.wrap_socket(sock, server_hostname=clean_host) as ssock:
                cert = ssock.getpeercert()
                tls_version = ssock.version()
                
                # Extract dates
                not_before_str = cert.get('notBefore')
                not_after_str = cert.get('notAfter')
                
                valid_until = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z').replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                days_remaining = (valid_until - now).days
                
                # Extract Issuer
                issuer_dict = dict(x[0] for x in cert.get('issuer', []))
                issuer_name = issuer_dict.get('organizationName') or issuer_dict.get('commonName') or "Unknown CA"
                
                # Extract Subject
                subject_dict = dict(x[0] for x in cert.get('subject', []))
                subject_name = subject_dict.get('commonName', clean_host)
                
                flags = []
                if days_remaining <= 0:
                    flags.append({
                        "code": "EXPIRED_SSL",
                        "severity": "critical",
                        "message": "SSL certificate has expired.",
                        "detail": "Expired certificates indicate broken or abandoned infrastructure."
                    })
                elif days_remaining < 14:
                    flags.append({
                        "code": "EXPIRING_SOON_SSL",
                        "severity": "moderate",
                        "message": f"SSL certificate expires in {days_remaining} days.",
                        "detail": "Certificate is nearing its expiration date."
                    })
                    
                return {
                    "has_ssl": True,
                    "is_valid": days_remaining > 0,
                    "issuer": issuer_name,
                    "subject": subject_name,
                    "valid_from": not_before_str,
                    "valid_until": not_after_str,
                    "days_remaining": days_remaining,
                    "tls_version": tls_version,
                    "critical_disclaimer": "HTTPS does not prove that a website is trustworthy. A malicious website can still use a valid HTTPS certificate.",
                    "flags": flags
                }
    except Exception as e:
        return {
            "status": "UNAVAILABLE",
            "has_ssl": False,
            "is_valid": False,
            "issuer": None,
            "subject": None,
            "valid_from": None,
            "valid_until": None,
            "days_remaining": 0,
            "tls_version": None,
            "critical_disclaimer": "HTTPS does not prove that a website is trustworthy. A malicious website can still use a valid HTTPS certificate.",
            "flags": [
                {
                    "code": "SSL_HANDSHAKE_FAILED",
                    "severity": "low",
                    "message": "TLS check unavailable; no certificate verified.",
                    "detail": "A network or validation failure is not proof of fraud."
                }
            ]
        }
