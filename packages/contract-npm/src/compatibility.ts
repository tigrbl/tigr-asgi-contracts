export interface Compatibility {
  contract_name: string;
  contract_version: string;
  serde_version: number;
  schema_draft: string;
  min_tigrcorn_version?: string | null;
  min_tigrbl_version?: string | null;
}
