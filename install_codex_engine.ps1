param(
    [string]$Root = "C:\Users\jrudy\CGCE"
)

Write-Host "=== Codex Engine Installer ===" -ForegroundColor Cyan
Write-Host "Root: $Root"

$EnginePath      = Join-Path $Root "codex_engine"
$ToolsPath       = Join-Path $EnginePath "tools"
$CheckpointsPath = Join-Path $EnginePath "checkpoints"
$ExtensionsPath  = Join-Path $EnginePath "extensions"
$StatePath       = Join-Path $EnginePath "state"
$AnalyticsPath   = Join-Path $EnginePath "analytics"

# 1) Ensure directories exist
$dirs = @(
    $EnginePath,
    $ToolsPath,
    $CheckpointsPath,
    $ExtensionsPath,
    $StatePath,
    $AnalyticsPath
)

foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d | Out-Null
        Write-Host "Created: $d"
    } else {
        Write-Host "Exists:  $d"
    }
}

# 2) guardrails.json
$guardrailsJson = @'
{
  "denyPaths": ["infra/", ".github/", "migrations/", "secrets/"],
  "allowExtensions": [".js", ".py", ".ts", ".java", ".md", ".json"],
  "maxFilesPerStep": 12,
  "maxTotalAddedLoc": 400,
  "requirePlan": true,
  "approvalTiers": {
    "low": ["add comments", "format code"],
    "medium": ["refactor", "add test"],
    "high": ["change API", "delete files"]
  }
}
'@

$guardrailsPath = Join-Path $ToolsPath "guardrails.json"
$guardrailsJson | Set-Content -Path $guardrailsPath -Encoding UTF8
Write-Host "Wrote: $guardrailsPath"

# 3) context_limits.json
$contextLimitsJson = @'
{
  "planning": 50000,
  "editing": 30000,
  "validation": 20000
}
'@

$contextLimitsPath = Join-Path $ToolsPath "context_limits.json"
$contextLimitsJson | Set-Content -Path $contextLimitsPath -Encoding UTF8
Write-Host "Wrote: $contextLimitsPath"

# 4) state.json
$stateJson = @'
{
  "version": "4.0.0",
  "currentStep": null,
  "lastCheckpointTag": null,
  "lastRunStatus": null,
  "updatedAt": null
}
'@

$statePath = Join-Path $StatePath "state.json"
$stateJson | Set-Content -Path $statePath -Encoding UTF8
Write-Host "Wrote: $statePath"

# 5) analytics file (empty jsonl)
$metricsPath = Join-Path $AnalyticsPath "codex_metrics.jsonl"
if (-not (Test-Path $metricsPath)) {
    "" | Set-Content -Path $metricsPath -Encoding UTF8
    Write-Host "Initialized: $metricsPath"
} else {
    Write-Host "Exists: $metricsPath"
}

# 6) tools/package.json
$toolsPackageJson = @'
{
  "name": "codex-engine",
  "version": "4.0.0",
  "description": "Codex Execution Engine tools for CGCE",
  "main": "codex.mjs",
  "type": "module",
  "bin": {
    "codex-engine": "./codex.mjs"
  },
  "scripts": {
    "start": "node codex.mjs",
    "status": "node codex.mjs status",
    "plan": "node codex.mjs plan",
    "test": "node codex.mjs test"
  },
  "dependencies": {
    "openai": "^6.9.1"
  }
}
'@

$toolsPackagePath = Join-Path $ToolsPath "package.json"
$toolsPackageJson | Set-Content -Path $toolsPackagePath -Encoding UTF8
Write-Host "Wrote: $toolsPackagePath"

# 7) tools/codex.mjs stub
$toolsCodexMjs = @'
#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import OpenAI from "openai";

const ROOT = path.resolve(path.join(__dirname, ".."));
const TOOLS = __dirname;
const STATE_DIR = path.join(ROOT, "state");
const STATE_FILE = path.join(STATE_DIR, "state.json");
const GUARDRAILS_FILE = path.join(TOOLS, "guardrails.json");
const CONTEXT_LIMITS_FILE = path.join(TOOLS, "context_limits.json");
const ANALYTICS_DIR = path.join(ROOT, "analytics");
const METRICS_FILE = path.join(ANALYTICS_DIR, "codex_metrics.jsonl");

function readJson(file) {
  try {
    const txt = fs.readFileSync(file, "utf8");
    return JSON.parse(txt);
  } catch {
    return null;
  }
}

function writeJson(file, obj) {
  fs.writeFileSync(file, JSON.stringify(obj, null, 2), "utf8");
}

function appendMetrics(event) {
  const line = JSON.stringify({
    timestamp: new Date().toISOString(),
    ...event
  });
  fs.appendFileSync(METRICS_FILE, line + "\n", "utf8");
}

async function run() {
  const args = process.argv.slice(2);
  const cmd = args[0] || "status";

  const apiKey = process.env.OPENAI_API_KEY;
  const hasApiKey = !!apiKey;

  const state = readJson(STATE_FILE) || {};
  const guardrails = readJson(GUARDRAILS_FILE) || {};
  const contextLimits = readJson(CONTEXT_LIMITS_FILE) || {};

  if (cmd === "status") {
    console.log("Codex Engine Status");
    console.log("-------------------");
    console.log("Root:          ", ROOT);
    console.log("API Key set:   ", hasApiKey ? "yes" : "no");
    console.log("Guardrails:    ", guardrails ? "loaded" : "missing");
    console.log("ContextLimits: ", contextLimits ? "loaded" : "missing");
    console.log("State:         ", state);
    return;
  }

  if (!hasApiKey) {
    console.error("ERROR: OPENAI_API_KEY is not set. Codex Engine cannot call models.");
    process.exit(1);
  }

  const client = new OpenAI({ apiKey });

  if (cmd === "plan") {
    const goal = args.slice(1).join(" ") || "No goal provided.";
    console.log("Planning for goal:", goal);

    const prompt = [
      "You are the Codex Execution Engine planner for the CGCE.",
      "Goal:",
      goal,
      "",
      "Return a short numbered list of steps (max 7) to achieve this change in code,",
      "with each step focused, testable, and safe."
    ].join("\n");

    const response = await client.responses.create({
      model: "gpt-4o-mini",
      input: prompt
    });

    const text = response.output_text ?? "";
    console.log(text.trim());

    state.currentStep = "planned";
    state.lastRunStatus = "ok";
    state.updatedAt = new Date().toISOString();
    writeJson(STATE_FILE, state);

    appendMetrics({
      step: "plan",
      goal,
      status: "ok"
    });

    return;
  }

  if (cmd === "test") {
    console.log("Codex Engine test stub.");
    console.log("Here is where you would wire static analysis and test runs.");
    appendMetrics({ step: "test", status: "stub" });
    return;
  }

  console.error("Unknown command:", cmd);
  console.error("Supported commands: status, plan, test");
  process.exit(1);
}

run().catch((err) => {
  console.error("Codex Engine error:", err?.message || err);
  process.exit(1);
});
'@

$toolsCodexPath = Join-Path $ToolsPath "codex.mjs"
$toolsCodexMjs | Set-Content -Path $toolsCodexPath -Encoding UTF8
Write-Host "Wrote: $toolsCodexPath"

# 8) npm install in tools
Write-Host "Running npm install in $ToolsPath ..."
Push-Location $ToolsPath
try {
    npm install
    Write-Host "npm install completed." -ForegroundColor Green
}
catch {
    Write-Host "npm install failed. Check the error above." -ForegroundColor Red
}
finally {
    Pop-Location
}

Write-Host "=== Codex Engine installation complete ===" -ForegroundColor Cyan
Write-Host "Try:"
Write-Host "  cd `"$ToolsPath`""
Write-Host "  node codex.mjs status"
Write-Host "  node codex.mjs plan `"Add unit tests for module X`""