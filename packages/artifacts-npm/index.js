import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { readFileSync } from "node:fs";

const here = dirname(fileURLToPath(import.meta.url));

export function contractRoot() {
  return join(here, "contract");
}

export function manifest() {
  return JSON.parse(readFileSync(join(contractRoot(), "manifest.json"), "utf8"));
}

export function checksums() {
  return readFileSync(join(contractRoot(), "checksums.txt"), "utf8");
}
