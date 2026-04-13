from __future__ import annotations
from pathlib import Path
import json
import sys
from pathlib import Path
ROOT0 = Path(__file__).resolve().parents[1]
if str(ROOT0) not in sys.path:
    sys.path.insert(0, str(ROOT0))
from common import contract_data, member_name

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "packages" / "contract-npm"

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def emit_enum(path: Path, enum_name: str, values: list[str]) -> None:
    lines = [f"export enum {enum_name} {{"]
    for v in values:
        lines.append(f"  {member_name(v)} = {json.dumps(v)},")
    lines.append("}")
    lines.append("")
    write(path, "\n".join(lines))

def main() -> None:
    d = contract_data()
    src = OUT / "src"
    emit_enum(src / "scope_types.ts", "ScopeType", d["scope_types"])
    emit_enum(src / "bindings.ts", "Binding", list(d["bindings"].keys()))
    emit_enum(src / "exchanges.ts", "Exchange", d["exchanges"])
    emit_enum(src / "families.ts", "Family", d["families"])
    emit_enum(src / "subevents.ts", "Subevent", d["all_subevents"])
    emit_enum(src / "completion.ts", "EmitCompletionLevel", list(d["completion"]["levels"].keys()))

    write(src / "capabilities.ts", '''export interface FamilyCapabilities {\n  request?: boolean;\n  session?: boolean;\n  message?: boolean;\n  stream_in?: boolean;\n  stream_out?: boolean;\n  datagram?: boolean;\n}\n''')
    write(src / "compatibility.ts", '''export interface Compatibility {\n  contract_name: string;\n  contract_version: string;\n  serde_version: number;\n  schema_draft: string;\n  min_tigrcorn_version?: string | null;\n  min_tigrbl_version?: string | null;\n}\n''')
    write(src / "ids.ts", '''export interface UnitIds {\n  unit_id?: string | null;\n  parent_unit_id?: string | null;\n  session_id?: string | null;\n  stream_id?: number | null;\n  datagram_id?: number | null;\n  emit_id?: string | null;\n}\n''')
    write(src / "models.ts", '''import type { FamilyCapabilities } from "./capabilities";\n\nexport interface TlsMetadata {\n  version?: string | null;\n  cipher?: string | null;\n  verified: boolean;\n  peer_identity?: string | null;\n  peer_cert?: Record<string, unknown> | null;\n}\n\nexport interface TransportMetadata {\n  binding: string;\n  network: string;\n  secure: boolean;\n  alpn?: string | null;\n  tls?: TlsMetadata | null;\n  framing?: string | null;\n}\n\nexport interface WebSocketScopeExt {\n  subprotocol?: string | null;\n}\n\nexport interface SseScopeExt {\n  retry_ms?: number | null;\n  last_event_id?: string | null;\n}\n\nexport interface WebTransportScopeExt {\n  session_id?: string | null;\n  supports_datagrams?: boolean;\n  supports_bidi_streams?: boolean;\n  supports_uni_streams?: boolean;\n  max_datagram_size?: number | null;\n}\n\nexport interface ScopeExt {\n  transport: TransportMetadata;\n  family_capabilities: FamilyCapabilities;\n  websocket?: WebSocketScopeExt | null;\n  sse?: SseScopeExt | null;\n  webtransport?: WebTransportScopeExt | null;\n}\n\nexport interface DerivedEvent {\n  family: string;\n  subevent: string;\n  repeated?: boolean;\n}\n''')
    write(src / "scope.ts", '''import type { ScopeExt } from "./models";\n\nexport interface ContractScope {\n  type: string;\n  asgi: Record<string, unknown>;\n  scheme: string;\n  http_version?: string | null;\n  method?: string | null;\n  path: string;\n  query_string?: string;\n  headers: [string, string][];\n  client?: [string, number] | null;\n  server?: [string, number] | null;\n  ext: ScopeExt;\n}\n''')
    event_values = d["schemas"]["event.schema.json"]["properties"]["type"]["enum"]
    emit_enum(src / "events.ts", "TransportEventType", event_values)
    with open(src / "events.ts", "a", encoding="utf-8") as f:
        f.write('export interface ContractEvent {\n  type: TransportEventType;\n  payload?: Record<string, unknown>;\n}\n')
    write(src / "registry.ts", "export const BINDING_FAMILY_MATRIX = " + json.dumps(d["binding_family"], indent=2) + " as const;\n\n" + "export const FAMILY_SUBEVENT_MATRIX = " + json.dumps(d["family_subevent"], indent=2) + " as const;\n\n" + "export const BINDING_SUBEVENT_MATRIX = " + json.dumps(d["binding_subevent"], indent=2) + " as const;\n")
    write(src / "validators.ts", '''import { BINDING_FAMILY_MATRIX, FAMILY_SUBEVENT_MATRIX, BINDING_SUBEVENT_MATRIX } from "./registry";\n\nexport function bindingSupportsFamily(binding: keyof typeof BINDING_FAMILY_MATRIX, family: string): boolean {\n  return (BINDING_FAMILY_MATRIX as any)[binding][family] !== "F";\n}\n\nexport function familySupportsSubevent(family: keyof typeof FAMILY_SUBEVENT_MATRIX, subevent: string): boolean {\n  return ((FAMILY_SUBEVENT_MATRIX as any)[family] ?? {})[subevent] !== "F";\n}\n\nexport function bindingSupportsSubevent(binding: keyof typeof BINDING_SUBEVENT_MATRIX, subevent: string): boolean {\n  return ((BINDING_SUBEVENT_MATRIX as any)[binding] ?? {})[subevent] !== "F";\n}\n''')
    write(src / "index.ts", '''export * from "./scope_types";\nexport * from "./bindings";\nexport * from "./exchanges";\nexport * from "./families";\nexport * from "./subevents";\nexport * from "./completion";\nexport * from "./capabilities";\nexport * from "./compatibility";\nexport * from "./ids";\nexport * from "./models";\nexport * from "./scope";\nexport * from "./events";\nexport * from "./registry";\nexport * from "./validators";\n''')
    write(OUT / "tsx" / "ScopeView.tsx", '''import React from "react";\nimport type { ContractScope } from "../src/scope";\n\nexport interface ScopeViewProps {\n  scope: ContractScope;\n}\n\nexport const ScopeView: React.FC<ScopeViewProps> = ({ scope }) => {\n  return <pre>{JSON.stringify(scope, null, 2)}</pre>;\n};\n''')
    write(OUT / "tsx" / "BindingBadge.tsx", '''import React from "react";\nimport type { Binding } from "../src/bindings";\n\nexport interface BindingBadgeProps {\n  binding: Binding;\n}\n\nexport const BindingBadge: React.FC<BindingBadgeProps> = ({ binding }) => <span>{binding}</span>;\n''')
    write(OUT / "tsx" / "FamilyBadge.tsx", '''import React from "react";\nimport type { Family } from "../src/families";\n\nexport interface FamilyBadgeProps {\n  family: Family;\n}\n\nexport const FamilyBadge: React.FC<FamilyBadgeProps> = ({ family }) => <span>{family}</span>;\n''')
    write(OUT / "tsx" / "SubeventBadge.tsx", '''import React from "react";\nimport type { Subevent } from "../src/subevents";\n\nexport interface SubeventBadgeProps {\n  subevent: Subevent;\n}\n\nexport const SubeventBadge: React.FC<SubeventBadgeProps> = ({ subevent }) => <span>{subevent}</span>;\n''')

if __name__ == "__main__":
    main()
