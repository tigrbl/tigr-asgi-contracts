from pydantic import BaseModel


class Compatibility(BaseModel):
    contract_name: str
    contract_version: str
    serde_version: int
    schema_draft: str
    min_tigrcorn_version: str | None = None
    min_tigrbl_version: str | None = None
