"""Regression tests for RDP security options without contacting a target host."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "apps/rdp-gateway"))
from rdp_config import connection_parameters


def test_defaults_negotiate_and_validate_certificates():
    params = connection_parameters({
        "rdp_host": "host",
        "rdp_port": 3389,
        "rdp_username": "u",
        "rdp_password": "p",
    })
    assert params["security"] == "any"
    assert params["ignore-cert"] == "false"


def test_all_security_modes_and_explicit_certificate_opt_out():
    base = {"rdp_host": "host", "rdp_port": 3389, "rdp_username": "u", "rdp_password": "p"}
    for mode in ("any", "nla", "tls", "rdp"):
        params = connection_parameters({**base, "rdp_security": mode, "rdp_ignore_cert": mode == "tls"})
        assert params["security"] == mode
        assert params["ignore-cert"] == ("true" if mode == "tls" else "false")


def test_invalid_options_fail_closed():
    base = {"rdp_host": "host", "rdp_port": 3389, "rdp_username": "u", "rdp_password": "p"}
    try:
        connection_parameters({**base, "rdp_security": "bogus"})
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported security mode was accepted")
    try:
        connection_parameters({**base, "rdp_ignore_cert": "true"})
    except ValueError:
        pass
    else:
        raise AssertionError("non-boolean certificate option was accepted")


if __name__ == "__main__":
    test_defaults_negotiate_and_validate_certificates()
    test_all_security_modes_and_explicit_certificate_opt_out()
    test_invalid_options_fail_closed()
    print("PASS: RDP option mapping regression tests")
