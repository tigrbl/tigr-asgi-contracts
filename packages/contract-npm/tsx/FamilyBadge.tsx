import React from "react";
import type { Family } from "../src/families";

export interface FamilyBadgeProps {
  family: Family;
}

export const FamilyBadge: React.FC<FamilyBadgeProps> = ({ family }) => <span>{family}</span>;
