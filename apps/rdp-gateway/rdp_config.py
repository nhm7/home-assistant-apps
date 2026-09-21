"""Pure RDP option mapping shared by the gateway and regression tests."""

RDP_SECURITY_MODES = frozenset({"any", "nla", "tls", "rdp"})


def connection_parameters(options: dict) -> dict[str, str]:
    """Map app options to Guacamole RDP parameters, failing closed."""
    security = options.get("rdp_security", "any")
    if security not in RDP_SECURITY_MODES:
        raise ValueError(f"Unsupported rdp_security mode: {security!r}")
    ignore_cert = options.get("rdp_ignore_cert", False)
    if not isinstance(ignore_cert, bool):
        raise ValueError("rdp_ignore_cert must be a boolean")
    return {
        "hostname": str(options["rdp_host"]),
        "port": str(options["rdp_port"]),
        "username": str(options["rdp_username"]),
        "password": str(options["rdp_password"]),
        "domain": str(options.get("rdp_domain", "")),
        "security": security,
        # Guacamole's parameter is hyphenated. Certificate validation remains
        # enabled unless the operator explicitly opts out.
        "ignore-cert": "true" if ignore_cert else "false",
    }
