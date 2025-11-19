<# 
CGCE Bootstrap (Planner + Codex) — next steps scaffolder
Idempotent: safe to re-run; creates only missing files/folders.
#>

param(
  [string]$Root = "$env:USERPROFILE\CGCE",
  [string]$RepoName = "cgce",
  [string]$DocName = "CGCE_v3_full.md"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Info($msg){ Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg){ Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Ok($msg){ Write-Host "[ OK ] $msg" -ForegroundColor Green }
function Ensure-Dir($path){ if(-not (Test-Path $path)){ New-Item -ItemType Directory -Path $path | Out-Null; Write-Ok "Created $path" } else { Write-Info "Exists: $path" } }
function Ensure-File($path, [string]$content){
  if(-not (Test-Path $path)){
    $dir = Split-Path -Parent $path
    if(-not (Test-Path $dir)){ Ensure-Dir $dir }
    $content | Out-File -FilePath $path -Encoding UTF8
    Write-Ok "Created $path"
  } else { Write-Info "Exists: $path" }
}

# --- Paths
$RepoPath   = Join-Path $Root $RepoName
$DocsPath   = Join-Path $RepoPath "docs"
$Prompts    = Join-Path $RepoPath "prompts"
$Schemas    = Join-Path $RepoPath "schemas"
$Tools      = Join-Path $RepoPath "tools"
$Evals      = Join-Path $RepoPath "evals"
$Ops        = Join-Path $RepoPath "ops"

# --- Create folders
Ensure-Dir $Root
Ensure-Dir $RepoPath
Ensure-Dir $DocsPath
Ensure-Dir $Prompts
Ensure-Dir $Schemas
Ensure-Dir $Tools
Ensure-Dir $Evals
Ensure-Dir $Ops

# --- .gitignore (idempotent)
$gitignore = @"
# Node
node_modules/
npm-debug.log*
dist/
.build/
.env

# Python
__pycache__/
*.pyc

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
"@
Ensure-File (Join-Path $RepoPath ".gitignore") $gitignore

# --- README
$readme = @"
# CGCE Monorepo

This repo implements the ChatGPT Center of Excellence v3 workflow:
- Planner (ChatGPT) -> Structured Outputs (JSON Schema) -> Codex (tools)
- Versioned schemas, evals before ship, retries/timeouts/idempotency
- Knowledge store first = local DB; upgrade to vector/RAG via tool if needed.
"@
Ensure-File (Join-Path $RepoPath "README.md") $readme

# --- CGCE v3 Full Doc
$docContent = @"
# ChatGPT Center of Excellence (CGCE) – Version 3
**Purpose:** Create highly reliable, innovative, and functional business tools using ChatGPT (Planner/Orchestrator) and Codex (Implementer/Executor).

**Primary KPI:** Tool Reliability with 97.5% confidence across:
- Consistency
- Reliability
- Functionality
- Security
- Stability

A tool is “Done” when:
1. Automated evals pass,
2. Outputs meet schema contracts,
3. The tool solves the user task without critical errors,
4. Security checks pass,
5. Planner and Codex outputs match acceptance criteria.

## 1. Dual-Engine Model
**Planner (ChatGPT):** holds developer brief, decomposes tasks, emits Structured Outputs (JSON+Schema), calls tools only when necessary, may add ultra-concise natural language.
**Codex (Implementer):** executes tools (code/HTTP/DB/files/tests), returns schema-valid results; ultra-concise natural language for clarity only.

## 2. Workflow Standards
- Planner -> Codex uses **Structured Outputs** with JSON Schema (mandatory).
- Knowledge store vs prompt stuffing: start with **local database**; add vector/RAG via tool as needed.
- Validate sources until **≥85% confidence**, higher when achievable.
- I/O contracts: `task_spec`, `tool_call`, `final_output` (all JSON + Schema).

## 3. Repository Layout
/prompt/ (brief/policies), /schemas/ (versioned), /tools/ (idempotent/retries/timeouts), /evals/ (golden sets), /ops/ (logs/metrics/redaction optional)

## 4. Schema Governance
Single versioned `schemas/` repo; no silent changes—bump semver + canary eval.

## 5. Model, Cost, Performance
Model selection **Accuracy → Cost**; POC on cost-free surfaces; enable prompt caching when net-positive.

## 6. Evals & QA
Required pre-ship; measure schema correctness, functional success, edge-cases, security assertions; canary evals on changes.

## 7. Production Hardening
Every tool call uses **retries, timeouts, idempotency** (mandatory). PII redaction optional (configurable).

## 8. Observability
Dashboards: usage, cost, latency, tool-error rate. Logs captured for debugging/governance.

## 9. Safety & Governance
No free-form handoffs; no unbounded tool loops; version bump + canary eval on any prompt/tool/schema change.

## 10. Roadmap
Adopt by value/complexity: GPT Actions, Agents, MCP servers; Realtime only if voice/streaming UX needed.

## 11. Build Loop
Plan → Spec (schemas+tools) → Implement (tests) → Evaluate → Ship (canary) → Observe → Iterate
"@
Ensure-File (Join-Path $DocsPath $DocName) $docContent

# --- Minimal Schemas (semver 0.1.0) — `$schema` keys escaped
$taskSpec = @"
{
  "`$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "task_spec",
  "version": "0.1.0",
  "type": "object",
  "required": ["objective", "inputs", "acceptance_criteria"],
  "properties": {
    "objective": { "type": "string", "minLength": 5 },
    "inputs": { "type": "object", "additionalProperties": true },
    "acceptance_criteria": {
      "type": "array",
      "items": { "type": "string", "minLength": 3 },
      "minItems": 1
    }
  },
  "additionalProperties": false
}
"@

$toolCall = @"
{
  "`$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "tool_call",
  "version": "0.1.0",
  "type": "object",
  "required": ["tool", "args", "idempotency_key"],
  "properties": {
    "tool": { "type": "string", "minLength": 1 },
    "args": { "type": "object", "additionalProperties": true },
    "idempotency_key": { "type": "string", "minLength": 8 }
  },
  "additionalProperties": false
}
"@

$finalOutput = @"
{
  "`$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "final_output",
  "version": "0.1.0",
  "type": "object",
  "required": ["status", "summary", "data"],
  "properties": {
    "status": { "type": "string", "enum": ["success", "failed", "partial"] },
    "summary": { "type": "string", "minLength": 3 },
    "data": { "type": "object", "additionalProperties": true }
  },
  "additionalProperties": false
}
"@

Ensure-File (Join-Path $Schemas "task_spec.schema.json") $taskSpec
Ensure-File (Join-Path $Schemas "tool_call.schema.json") $toolCall
Ensure-File (Join-Path $Schemas "final_output.schema.json") $finalOutput

# --- Evals: tiny golden set (renamed var to avoid $Evals collision)
$goldenEvalJson = @"
[
  {
    "name": "hello_world_tool",
    "task_spec": {
      "objective": "Echo a message reliably",
      "inputs": { "message": "Hello CGCE" },
      "acceptance_criteria": ["status success", "echo equals input", "schema valid"]
    },
    "expected": {
      "status": "success",
      "summary": "Echoed input",
      "data": { "echo": "Hello CGCE" }
    }
  }
]
"@
Ensure-File (Join-Path $Evals "golden_min.json") $goldenEvalJson

# --- Ops config
$opsConfig = @"
{
  "observability": {
    "dashboards": ["usage", "cost", "latency", "tool_error_rate"]
  },
  "policy": {
    "require_retries_timeouts_idempotency": true,
    "pii_redaction_default": false
  },
  "kpi": {
    "tool_reliability_confidence": 97.5,
    "source_validation_confidence_min": 85
  }
}
"@
Ensure-File (Join-Path $Ops "config.json") $opsConfig

# --- Planner prompt stub
$plannerPrompt = @"
# Planner (ChatGPT) – System Brief (stub)
- Produce task_spec -> tool_call(s) -> final_output according to schemas.
- Keep natural language ultra-concise.
- Validate sources until >=85% confidence or higher.
"@
Ensure-File (Join-Path $Prompts "planner_system_stub.md") $plannerPrompt

# --- Codex tool stub (Node optional)
$pkgJson = @"
{
  "name": "cgce-tools",
  "version": "0.1.0",
  "type": "module",
  "private": true,
  "scripts": {
    "test": "node tools/echoTool.mjs"
  },
  "dependencies": {}
}
"@

$echoTool = @"
import crypto from 'node:crypto';

function withIdempotency(fn){
  const seen = new Set();
  return async (args) => {
    const key = String(args.idempotency_key||'') || crypto.randomUUID();
    if(seen.has(key)) return {status:'success', summary:'Idempotent replay', data:{echo: args.message||''}};
    seen.add(key);
    return fn(args);
  };
}

const echo = withIdempotency(async (args) => {
  if(!args || typeof args.message !== 'string') {
    return {status:'failed', summary:'Invalid args', data:{}};
  }
  return {status:'success', summary:'Echoed input', data:{echo: args.message}};
});

if (process.argv[1] === new URL(import.meta.url).pathname) {
  const args = { message: 'Hello CGCE', idempotency_key: crypto.randomUUID() };
  echo(args).then(r => { console.log(JSON.stringify(r,null,2)); }).catch(e => { console.error(e); process.exit(1); });
}

export default echo;
"@

# Only write Node files if package.json missing (idempotent)
if(-not (Test-Path (Join-Path $RepoPath "package.json"))){
  Ensure-File (Join-Path $RepoPath "package.json") $pkgJson
}
Ensure-File (Join-Path $Tools "echoTool.mjs") $echoTool

# --- Git init (optional)
$git = (Get-Command git -ErrorAction SilentlyContinue)
if($git){
  if(-not (Test-Path (Join-Path $RepoPath ".git"))){
    Write-Info "Initializing git repo..."
    Push-Location $RepoPath
    git init | Out-Null
    git add . | Out-Null
    git commit -m "CGCE bootstrap: docs, schemas, tools, evals, ops" | Out-Null
    Pop-Location
    Write-Ok "Git repo initialized and committed."
  } else {
    Write-Info "Git repo already initialized."
  }
} else {
  Write-Warn "Git not found; skipping repo init."
}

# --- Node check (optional)
$node = (Get-Command node -ErrorAction SilentlyContinue)
if($node){
  Write-Info "Node detected. You can run:  npm test"
} else {
  Write-Warn "Node not found; tool stub present but not runnable until Node is installed."
}

Write-Ok "CGCE bootstrap complete."
Write-Info "Docs: $DocsPath\$DocName"
Write-Info "Schemas: $Schemas"
Write-Info "Tools: $Tools"
Write-Info "Evals: $Evals"
Write-Info "Ops: $Ops"
