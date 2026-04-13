import React from "react";
import type { ContractScope } from "../src/scope";

export interface ScopeViewProps {
  scope: ContractScope;
}

export const ScopeView: React.FC<ScopeViewProps> = ({ scope }) => {
  return <pre>{JSON.stringify(scope, null, 2)}</pre>;
};
