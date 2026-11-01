import socket
import ipaddress
from urllib.parse import urlparse
from typing import Tuple, List

BLOCKED_NETWORKS: List[ipaddress.IPv4Network | ipaddress.IPv6Network] = [
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
    ipaddress.ip_network("10.0.0.0/8"),        # Private Class A
    ipaddress.ip_network("172.16.0.0/12"),     # Private Class B
    ipaddress.ip_network("192.168.0.0/16"),    # Private Class C
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local / AWS & GCP Metadata
    ipaddress.ip_network("0.0.0.0/8"),         # Broadcast
    ipaddress.ip_network("::1/128"),           # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),          # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),         # IPv6 Link-Local
]

BLOCKED_HOSTNAMES = {
    "localhost", "localhost.localdomain", "127.0.0.1", "::1", "metadata.google.internal",
    "instance-data", "metadata", "kubernetes.default.svc"
}

class SSRFError(Exception):
    pass

def validate_and_resolve_url(url: str, resolve_dns: bool = True) -> Tuple[bool, str, List[str]]:
    """
    Validates a URL against SSRF attacks and resolves target IPs safely.
    Rejects unsupported schemes (file://, gopher://, ftp://, etc.),
    loopback addresses (127.0.0.1, ::1, localhost),
    private RFC1918 subnets, and cloud metadata link-local endpoints (169.254.169.254).
    Returns (is_safe, error_or_clean_url, resolved_ips)
    """
    if not url or not isinstance(url, str):
        return False, "Empty or invalid URL supplied", []

    clean_url = url.strip()

    # Check scheme explicitly before automatic prefixing
    if "://" in clean_url:
        scheme = clean_url.split("://", 1)[0].lower()
        if scheme not in ("http", "https"):
            return False, f"Unsupported scheme: {scheme} is blocked by SSRF policy", []
    else:
        clean_url = "https://" + clean_url

    try:
        parsed = urlparse(clean_url)
    except Exception as e:
        return False, f"Malformed URL: {str(e)}", []

    scheme = (parsed.scheme or "").lower()
    if scheme not in ("http", "https"):
        return False, f"Unsupported scheme: '{scheme}' is blocked by SSRF policy", []

    hostname = parsed.hostname
    if not hostname:
        return False, "URL does not contain a valid hostname", []

    if parsed.username or parsed.password:
        return False, "Blocked URL credentials", []
    hostname_lower = hostname.lower().rstrip(".")

    # Check blocklist of hostnames
    if hostname_lower in BLOCKED_HOSTNAMES:
        return False, f"Blocked hostname: Access to '{hostname}' is blocked by SSRF policy", []

    if hostname_lower.endswith((".local", ".internal", ".localhost", ".onion", ".lan")):
        return False, f"Blocked hostname: Internal TLD '{hostname_lower}' is blocked", []

    resolved_ips = []

    # Check if the hostname itself is a raw IP literal
    try:
        ip = ipaddress.ip_address(hostname_lower)
        resolved_ips.append(str(ip))
        if not ip.is_global:
            return False, f"Private or loopback IP blocked: {ip}", resolved_ips
        if ip.is_loopback:
            return False, f"Private or loopback IP blocked: '{ip}'", resolved_ips
        if ip.is_link_local:
            return False, f"Cloud metadata link-local address blocked: '{ip}'", resolved_ips
        if ip.is_private:
            return False, f"Private network IP blocked: '{ip}'", resolved_ips
        for net in BLOCKED_NETWORKS:
            if ip in net:
                return False, f"Private or loopback IP blocked: '{ip}' in restricted network", resolved_ips
    except ValueError:
        if not resolve_dns:
            return True, clean_url, []
        # Hostname is a domain name, resolve DNS
        try:
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            resolved_set = {item[4][0] for item in addr_info}
            resolved_ips = list(resolved_set)
            if not resolved_ips:
                return False, f"DNS resolution failed for '{hostname}'", []

            for resolved_ip in resolved_ips:
                ip_obj = ipaddress.ip_address(resolved_ip)
                if not ip_obj.is_global:
                    return False, f"Private or loopback IP blocked: {resolved_ip}", resolved_ips
                if ip_obj.is_loopback:
                    return False, f"Private or loopback IP blocked: Host '{hostname}' resolved to loopback IP '{resolved_ip}'", resolved_ips
                if ip_obj.is_link_local:
                    return False, f"Cloud metadata link-local address blocked: Host '{hostname}' resolved to metadata IP '{resolved_ip}'", resolved_ips
                if ip_obj.is_private:
                    return False, f"Private network IP blocked: Host '{hostname}' resolved to private IP '{resolved_ip}'", resolved_ips
                for net in BLOCKED_NETWORKS:
                    if ip_obj in net:
                        return False, f"Private or loopback IP blocked: Host '{hostname}' resolved to restricted IP '{resolved_ip}'", resolved_ips
        except socket.gaierror:
            # Domain could not be resolved; allowed to proceed into domain intelligence scanner for unresolvable/new domains
            pass
        except Exception as e:
            return False, f"DNS verification error: {str(e)}", []

    return True, clean_url, resolved_ips


def validate_url_safe(url: str, resolve_dns: bool = True) -> Tuple[bool, str]:
    """
    Validates a URL against SSRF attacks.
    Returns (is_safe, error_message_or_clean_url)
    """
    is_safe, msg, _ = validate_and_resolve_url(url, resolve_dns=resolve_dns)
    return is_safe, msg
