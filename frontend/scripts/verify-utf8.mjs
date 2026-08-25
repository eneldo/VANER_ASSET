import fs from "node:fs";
import path from "node:path";

const suspicious = /[ÃƒÃ‚]|Ã¢[â‚¬â€šÆ’â€žâ€¦â€ â€¡Ë†â€°Å â€¹Å’Å½â€˜â€™â€œâ€â€¢â€“â€”Ëœâ„¢Å¡â€ºÅ“Å¾Å¸]/u;
const extensions = new Set([".js", ".jsx", ".css", ".html"]);
const failures = [];

function walk(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const filePath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      walk(filePath);
    } else if (extensions.has(path.extname(entry.name))) {
      const content = fs.readFileSync(filePath, "utf8");
      if (suspicious.test(content)) failures.push(filePath);
    }
  }
}

walk(path.resolve("src"));
if (failures.length) {
  console.error("Se detectó posible mojibake en:");
  failures.forEach((file) =>
    console.error("- " + path.relative(process.cwd(), file)),
  );
  process.exit(1);
}

console.log("Frontend UTF-8 verificado.");
