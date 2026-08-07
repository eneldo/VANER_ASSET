import { readFile, readdir } from "node:fs/promises";
import { extname, join } from "node:path";
import { fileURLToPath } from "node:url";

const forbidden = [
  "RSCHydratedRouter",
  "RSCStaticRouter",
  "unstable_RSCStaticRouter",
  "createCallServer",
  "react-router/dom",
  "react-router/serve",
];

async function collect(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await collect(path));
    else if ([".js", ".jsx"].includes(extname(entry.name))) files.push(path);
  }
  return files;
}

const violations = [];
const sourceRoot = fileURLToPath(new URL("../src", import.meta.url));
for (const path of await collect(sourceRoot)) {
  const source = await readFile(path, "utf8");
  for (const token of forbidden) {
    if (source.includes(token)) violations.push({ path, token });
  }
}

if (violations.length) {
  console.error("React Router RSC APIs are forbidden while GHSA-qwww-vcr4-c8h2 is allowlisted.");
  console.error(violations);
  process.exit(1);
}

console.log("No React Router RSC APIs detected.");
