from __future__ import annotations
from tigr_asgi_contract import Binding, Family, binding_supports_family

def test_cross_language_roundtrip_smoke() -> None:
    assert Binding.REST.value == "rest"
    assert binding_supports_family("rest", Family.REQUEST.value) is True
