/**
 * Photo Choice Contract Test
 *
 * Validates the frontend photo-choice integration contract by reading
 * source files and verifying key patterns via string/regex matching.
 *
 * Run: cd frontend && npx tsx src/tests/photo-choice-contract.test.ts
 */

import * as fs from "fs";
import * as path from "path";

// ---- Helpers ----

let passed = 0;
let failed = 0;

function assert(label: string, condition: boolean, detail?: string) {
  if (condition) {
    passed++;
    console.log(`  PASS  ${label}`);
  } else {
    failed++;
    console.log(`  FAIL  ${label}${detail ? " -- " + detail : ""}`);
  }
}

// ---- Load source files ----

const root = path.resolve(__dirname, "..");
const generatePagePath = path.join(root, "app", "generate", "[id]", "page.tsx");
const photoPanelPath = path.join(root, "components", "PhotoChoicePanel.tsx");

const generateSrc = fs.readFileSync(generatePagePath, "utf-8");
const panelSrc = fs.readFileSync(photoPanelPath, "utf-8");

// ============================================================
// 1. SCHEMA CONTRACT: JSON body uses key "choices" not "decisions"
// ============================================================

console.log("\n=== 1. Schema contract: JSON key is 'choices' ===");

// Find the JSON.stringify call in handlePhotoConfirm
const jsonStringifyMatch = generateSrc.match(
  /JSON\.stringify\(\s*\{[^}]*\}\s*\)/s
);
assert(
  "JSON.stringify call found in generate page",
  jsonStringifyMatch !== null
);

if (jsonStringifyMatch) {
  const stringifyArg = jsonStringifyMatch[0];
  assert(
    "JSON.stringify uses key 'choices'",
    stringifyArg.includes("choices"),
    `Found: ${stringifyArg.trim()}`
  );
  assert(
    "JSON.stringify does NOT use key 'decisions'",
    !stringifyArg.includes("decisions"),
    `Found: ${stringifyArg.trim()}`
  );
}

// ============================================================
// 2. LOOP PREVENTION: photoChoicesHandledRef guard
// ============================================================

console.log("\n=== 2. Loop prevention: photoChoicesHandledRef ===");

// 2a. Ref is declared with initial value false
const refDecl = generateSrc.match(
  /photoChoicesHandledRef\s*=\s*useRef\s*\(\s*false\s*\)/
);
assert(
  "photoChoicesHandledRef declared with useRef(false)",
  refDecl !== null
);

// 2b. Polling checks ref BEFORE calling setPhotoChoices
//     We look for the guard pattern: !photoChoicesHandledRef.current appears before setPhotoChoices
const pollingBlock = generateSrc.match(
  /const\s+poll\s*=\s*async\s*\(\)\s*=>\s*\{([\s\S]*?)\n\s{4}\};/
);
assert("Polling function found", pollingBlock !== null);

if (pollingBlock) {
  const pollBody = pollingBlock[1];
  const guardIdx = pollBody.indexOf("!photoChoicesHandledRef.current");
  const setChoicesIdx = pollBody.indexOf("setPhotoChoices(");
  assert(
    "photoChoicesHandledRef.current checked in polling block",
    guardIdx !== -1,
    guardIdx === -1 ? "Guard not found in poll body" : undefined
  );
  assert(
    "Guard appears BEFORE setPhotoChoices in polling",
    guardIdx !== -1 && setChoicesIdx !== -1 && guardIdx < setChoicesIdx,
    `guardIdx=${guardIdx}, setChoicesIdx=${setChoicesIdx}`
  );
}

// 2c. handlePhotoConfirm sets ref to true
const confirmFn = generateSrc.match(
  /handlePhotoConfirm\s*=\s*useCallback\s*\(\s*\n?\s*async\s*\(decisions[^)]*\)\s*=>\s*\{([\s\S]*?)\n\s{2}\},/
);
assert("handlePhotoConfirm function found", confirmFn !== null);

if (confirmFn) {
  const confirmBody = confirmFn[1];
  assert(
    "handlePhotoConfirm sets photoChoicesHandledRef.current = true",
    confirmBody.includes("photoChoicesHandledRef.current = true")
  );
}

// 2d. handlePhotoCancel sets ref to true
const cancelFn = generateSrc.match(
  /handlePhotoCancel\s*=\s*useCallback\s*\(\s*\(\)\s*=>\s*\{([\s\S]*?)\}\s*,/
);
assert("handlePhotoCancel function found", cancelFn !== null);

if (cancelFn) {
  const cancelBody = cancelFn[1];
  assert(
    "handlePhotoCancel sets photoChoicesHandledRef.current = true",
    cancelBody.includes("photoChoicesHandledRef.current = true")
  );
}

// ============================================================
// 3. PhotoDecision -> PhotoChoiceItem MAPPING
// ============================================================

console.log("\n=== 3. PhotoDecision to PhotoChoiceItem mapping ===");

// 3a. "retry" maps to "stock"
const retryMapping = generateSrc.match(
  /action:\s*d\.action\s*===\s*["']retry["']\s*\?\s*["']stock["']\s*:\s*d\.action/
);
assert(
  "action 'retry' is mapped to 'stock' before sending",
  retryMapping !== null,
  retryMapping ? `Found: ${retryMapping[0]}` : "Pattern not found"
);

// 3b. section_type is passed through
const sectionTypePassthrough = generateSrc.match(
  /section_type:\s*d\.section_type/
);
assert(
  "section_type passed through from decision",
  sectionTypePassthrough !== null
);

// 3c. photo_url is passed through (or null)
const photoUrlMapping = generateSrc.match(
  /photo_url:\s*d\.photo_url\s*\|\|\s*null/
);
assert(
  "photo_url mapped from decision (with null fallback)",
  photoUrlMapping !== null
);

// 3d. photo_urls is always null
const photoUrlsNull = generateSrc.match(/photo_urls:\s*null/);
assert(
  "photo_urls is always set to null",
  photoUrlsNull !== null
);

// ============================================================
// 4. STATE MACHINE VERIFICATION
// ============================================================

console.log("\n=== 4. State machine verification ===");

// 4a. Initial state: photoChoices = null
const initialChoices = generateSrc.match(
  /useState<PhotoChoice\[\]\s*\|\s*null>\s*\(\s*null\s*\)/
);
assert(
  "photoChoices initial state is null",
  initialChoices !== null
);

// 4b. Initial state: photoChoicesHandledRef = false (already checked above)
assert(
  "photoChoicesHandledRef initial state is false (via useRef(false))",
  refDecl !== null
);

// 4c. After confirm: setPhotoChoices(null) clears state
const confirmClearsChoices =
  confirmFn && confirmFn[1].includes("setPhotoChoices(null)");
assert(
  "handlePhotoConfirm clears photoChoices to null",
  !!confirmClearsChoices
);

// 4d. After cancel: setPhotoChoices(null) clears state
const cancelClearsChoices =
  cancelFn && cancelFn[1].includes("setPhotoChoices(null)");
assert(
  "handlePhotoCancel clears photoChoices to null",
  !!cancelClearsChoices
);

// 4e. Panel rendered only when photoChoices is non-null and non-empty
const panelRender = generateSrc.match(
  /\{photoChoices\s*&&\s*photoChoices\.length\s*>\s*0\s*&&/
);
assert(
  "PhotoChoicePanel only rendered when photoChoices is non-null and has items",
  panelRender !== null
);

// ============================================================
// 5. PhotoChoicePanel TYPES (from component file)
// ============================================================

console.log("\n=== 5. PhotoChoicePanel exported types ===");

// 5a. PhotoChoice interface exists
assert(
  "PhotoChoice interface exported",
  panelSrc.includes("export interface PhotoChoice")
);

// 5b. PhotoDecision interface exists with correct action union
const decisionInterface = panelSrc.match(
  /export\s+interface\s+PhotoDecision\s*\{([\s\S]*?)\}/
);
assert("PhotoDecision interface exported", decisionInterface !== null);

if (decisionInterface) {
  const body = decisionInterface[1];
  assert(
    "PhotoDecision.action includes 'stock' | 'upload' | 'retry'",
    body.includes('"stock"') && body.includes('"upload"') && body.includes('"retry"')
  );
}

// 5c. Generate page imports types from PhotoChoicePanel
const importLine = generateSrc.match(
  /import\s+PhotoChoicePanel,\s*\{[^}]*PhotoChoice[^}]*PhotoDecision[^}]*\}\s*from/
);
assert(
  "Generate page imports PhotoChoice and PhotoDecision types",
  importLine !== null
);

// ============================================================
// 6. ENDPOINT & METHOD
// ============================================================

console.log("\n=== 6. Endpoint and HTTP method ===");

const fetchCall = generateSrc.match(
  /fetch\(\s*`\$\{API_BASE\}\/api\/generate\/\$\{siteId\}\/photo-choices`/
);
assert(
  "POST endpoint is /api/generate/{siteId}/photo-choices",
  fetchCall !== null
);

const methodPost = generateSrc.match(
  /method:\s*["']POST["']/
);
assert("HTTP method is POST", methodPost !== null);

// ============================================================
// SUMMARY
// ============================================================

console.log("\n" + "=".repeat(50));
console.log(`TOTAL: ${passed + failed} checks, ${passed} passed, ${failed} failed`);
console.log("=".repeat(50));

if (failed > 0) {
  console.log("\nSome checks FAILED. See details above.");
  process.exit(1);
} else {
  console.log("\nAll checks PASSED.");
  process.exit(0);
}
