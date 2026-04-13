from __future__ import annotations
from tigr_asgi_contract import Binding, Family, binding_supports_family

def test_python_binding_supports_family() -> None:
    assert binding_supports_family(Binding.WEBSOCKET.value, Family.MESSAGE.value) is True
