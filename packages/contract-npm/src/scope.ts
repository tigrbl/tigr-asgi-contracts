import type { ScopeExt } from "./models";

export interface ContractScope {
  type: string;
  asgi: Record<string, unknown>;
  scheme: string;
  http_version?: string | null;
  method?: string | null;
  path: string;
  query_string?: string;
  headers: [string, string][];
  client?: [string, number] | null;
  server?: [string, number] | null;
  ext: ScopeExt;
}
