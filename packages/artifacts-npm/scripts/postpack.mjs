import { existsSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const pkgRoot = join(here, "..");
const dst = join(pkgRoot, "contract");
if (existsSync(dst)) rmSync(dst, { recursive: true, force: true });
