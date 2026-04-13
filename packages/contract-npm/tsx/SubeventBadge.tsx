import React from "react";
import type { Subevent } from "../src/subevents";

export interface SubeventBadgeProps {
  subevent: Subevent;
}

export const SubeventBadge: React.FC<SubeventBadgeProps> = ({ subevent }) => <span>{subevent}</span>;
