import React from "react";
import type { Binding } from "../src/bindings";

export interface BindingBadgeProps {
  binding: Binding;
}

export const BindingBadge: React.FC<BindingBadgeProps> = ({ binding }) => <span>{binding}</span>;
