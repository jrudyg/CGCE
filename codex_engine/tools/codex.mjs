#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";
import OpenAI from "openai";

// ESM-compatible __dirname / __filename
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Core paths
const ROOT = path.resolve(path.join(__dirname, ".."));            // ...\codex_engine
const TOOLS = __dirname;                                          // ...\codex_engine\tools
const STATE_DIR = path.join(ROOT, "state");
const STATE_FILE = path.join(STATE_DIR, "state.json");
const GUARDRAILS_FILE = path.join(TOOLS, "guardrails.json");
const CONTEXT_LIMITS_FILE = path.join(TOOLS, "context_limits.json");
const ANALYTICS_DIR = path.join(ROOT, "analytics");
const METRICS_FILE = path.join(ANALYTICS_DIR, "codex_metrics.jsonl");
const WORKTREES_DIR = path.join(ROOT, "worktrees");

// Target repo root for edits/tests/checkpoints (default = parent of codex_engine)
const REPO_ROOT =
  process.env.CODEX_TARGET_ROOT ||
  path.resolve(path.join(ROOT, "..")); // C:\Users\jrudy\CGCE by default

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

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function runCommand(cmd, options = {}) {
  try {
    execSync(cmd, { stdio: "inherit", ...options });
    return { ok: true };
  } catch (err) {
    console.error(`Command failed: ${cmd}`);
    if (err?.message) console.error(err.message);
    return { ok: false, error: err };
  }
}

function nextCheckpointTag(state) {
  const last = state.lastCheckpointTag;
  if (!last || !/^codex-cp-\d+$/.test(last)) {
    return "codex-cp-0001";
  }
  const num = parseInt(last.replace("codex-cp-", ""), 10) || 0;
  const next = (num + 1).toString().padStart(4, "0");
  return `codex-cp-${next}`;
}

function isPathAllowed(relPath, guardrails) {
  const norm = relPath.replace(/\\/g, "/");
  const denyPaths = guardrails?.denyPaths || [];
  const allowExtensions = guardrails?.allowExtensions || [];

  for (const d of denyPaths) {
    if (norm.startsWith(d)) {
      return { allowed: false, reason: `Path ${relPath} is under denied path ${d}` };
    }
  }

  if (allowExtensions.length > 0) {
    const ext = path.extname(norm);
    if (!allowExtensions.includes(ext)) {
      return { allowed: false, reason: `Extension ${ext} is not in allowExtensions` };
    }
  }

  return { allowed: true };
}

async function handleStatus(state, guardrails, contextLimits, hasApiKey) {
  console.log("Codex Engine Status");
  console.log("-------------------");
  console.log("Root:           ", ROOT);
  console.log("Repo root:      ", REPO_ROOT);
  console.log("API Key set:    ", hasApiKey ? "yes" : "no");
  console.log("Guardrails:     ", guardrails ? "loaded" : "missing");
  console.log("ContextLimits:  ", contextLimits ? "loaded" : "missing");
  console.log("State:          ", state || {});
}

async function handlePlan(client, args, state) {
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
}

async function handleTest(state) {
  console.log("Codex Engine Test Runner");
  console.log("------------------------");
  console.log("Repo root:", REPO_ROOT);

  ensureDir(REPO_ROOT);

  // Decide what to run
  let cmd = process.env.CODEX_TEST_CMD || null;
  let cwd = process.env.CODEX_TEST_CWD || REPO_ROOT;

  if (!cmd) {
    const pkgJson = path.join(REPO_ROOT, "package.json");
    const evalScript = path.join(REPO_ROOT, "eval_v2.ps1");

    if (fs.existsSync(pkgJson)) {
      cmd = "npm test";
      console.log("No CODEX_TEST_CMD set. Detected package.json – defaulting to: npm test");
    } else if (fs.existsSync(evalScript)) {
      cmd = 'powershell -ExecutionPolicy Bypass -File .\\eval_v2.ps1';
      console.log("No CODEX_TEST_CMD set. Detected eval_v2.ps1 – defaulting to:", cmd);
    } else {
      console.log("No CODEX_TEST_CMD set and no obvious test runner detected.");
      console.log("Stub: marking test as 'skipped'. Configure CODEX_TEST_CMD for real behavior.");
      appendMetrics({ step: "test", status: "skipped" });
      state.lastRunStatus = "skipped";
      state.updatedAt = new Date().toISOString();
      writeJson(STATE_FILE, state);
      return;
    }
  } else {
    console.log("Using configured CODEX_TEST_CMD:", cmd);
    console.log("CWD:", cwd);
  }

  const result = runCommand(cmd, { cwd });

  if (result.ok) {
    console.log("Tests passed.");
    appendMetrics({ step: "test", status: "passed", cmd, cwd });
    state.lastRunStatus = "passed";
  } else {
    console.log("Tests failed.");
    appendMetrics({ step: "test", status: "failed", cmd, cwd });
    state.lastRunStatus = "failed";
  }

  state.currentStep = "tested";
  state.updatedAt = new Date().toISOString();
  writeJson(STATE_FILE, state);
}

async function handleCheckpoint(args, state) {
  const message = args.slice(1).join(" ") || "Codex checkpoint";

  console.log("Creating checkpoint...");
  console.log("Repo root:", REPO_ROOT);
  console.log("Message:  ", message);

  // Verify git repo
  let topLevel = null;
  try {
    topLevel = execSync(`git -C "${REPO_ROOT}" rev-parse --show-toplevel`, {
      encoding: "utf8"
    }).trim();
  } catch {
    console.error("ERROR: REPO_ROOT is not a git repository or git is not available.");
    console.error("Checkpoint will NOT be created. Configure REPO_ROOT and git, then retry.");
    appendMetrics({ step: "checkpoint", status: "failed", reason: "no-git" });
    return;
  }

  console.log("Git repo root:", topLevel);

  const tag = nextCheckpointTag(state);
  console.log("Tag:", tag);

  // Create annotated tag
  const safeMessage = message.replace(/"/g, '\\"');
  const result = runCommand(`git -C "${REPO_ROOT}" tag -a ${tag} -m "${safeMessage}"`);

  if (!result.ok) {
    console.error("Failed to create git tag. Check git status/log.");
    appendMetrics({ step: "checkpoint", status: "failed", tag });
    return;
  }

  console.log("Checkpoint created:", tag);

  state.lastCheckpointTag = tag;
  state.currentStep = "checkpoint";
  state.lastRunStatus = "ok";
  state.updatedAt = new Date().toISOString();
  writeJson(STATE_FILE, state);

  appendMetrics({ step: "checkpoint", status: "ok", tag, message });
}

async function handleEdit(client, args, state, guardrails) {
  console.log("Codex Engine Edit");
  console.log("-----------------");
  console.log("Repo root:", REPO_ROOT);

  // Parse args: edit [goal words...] --files "a,b,c"
  const rest = args.slice(1);
  const filesIndex = rest.indexOf("--files");

  if (filesIndex === -1 || filesIndex === rest.length - 1) {
    console.error('Usage: node codex.mjs edit <goal text...> --files "relative/path1,relative/path2"');
    process.exit(1);
  }

  const goalWords = rest.slice(0, filesIndex);
  const goal = goalWords.join(" ") || "Edit files as appropriate.";
  const filesArg = rest[filesIndex + 1];
  const relFiles = filesArg.split(",").map((s) => s.trim()).filter(Boolean);

  if (relFiles.length === 0) {
    console.error("No files provided to --files.");
    process.exit(1);
  }

  const maxFiles = guardrails?.maxFilesPerStep ?? 12;
  if (relFiles.length > maxFiles) {
    console.error(`Refusing to edit ${relFiles.length} files; maxFilesPerStep is ${maxFiles}.`);
    process.exit(1);
  }

  // Guardrails: denyPaths + allowed extensions
  for (const f of relFiles) {
    const check = isPathAllowed(f, guardrails);
    if (!check.allowed) {
      console.error(`Guardrails violation for ${f}: ${check.reason}`);
      process.exit(1);
    }
  }

  // Try to create a git worktree
  ensureDir(WORKTREES_DIR);
  const worktreeName = `codex-edit-${Date.now()}`;
  const worktreePath = path.join(WORKTREES_DIR, worktreeName);

  console.log("Attempting to create git worktree at:", worktreePath);

  let activeRoot = REPO_ROOT;
  let usingWorktree = false;

  const worktreeResult = runCommand(
    `git -C "${REPO_ROOT}" worktree add "${worktreePath}"`,
    {}
  );

  if (worktreeResult.ok) {
    console.log("Worktree created.");
    activeRoot = worktreePath;
    usingWorktree = true;
  } else {
    console.warn("Could not create worktree. Falling back to editing in-place in REPO_ROOT.");
    console.warn("Make sure you have git initialized and a clean working tree.");
  }

  const edited = [];

  for (const rel of relFiles) {
    const targetPath = path.join(activeRoot, rel);
    console.log("");
    console.log("Editing file:", targetPath);

    if (!fs.existsSync(targetPath)) {
      console.error("File does not exist, skipping:", targetPath);
      continue;
    }

    const original = fs.readFileSync(targetPath, "utf8");

    const prompt = [
      "You are the Codex Execution Engine code editor for CGCE.",
      "You will receive:",
      "- A description of the goal/change.",
      "- The full current contents of a file.",
      "",
      "You must return ONLY the full revised file content, with no explanations, no markdown, no code fences.",
      "",
      "Goal:",
      goal,
      "",
      "File path:",
      rel,
      "",
      "Current file contents:",
      "----------------------",
      original
    ].join("\n");

    try {
      const response = await client.responses.create({
        model: "gpt-4o-mini",
        input: prompt
      });

      const newContent = (response.output_text ?? "").trim();
      if (!newContent) {
        console.error("Received empty content for file, skipping:", rel);
        continue;
      }

      fs.writeFileSync(targetPath, newContent, "utf8");
      console.log("Updated:", rel);
      edited.push(rel);
    } catch (err) {
      console.error("Error editing file", rel, ":", err?.message || err);
    }
  }

  if (edited.length === 0) {
    console.log("No files were successfully edited.");
  } else {
    console.log("");
    console.log("Edited files:");
    edited.forEach((f) => console.log(" -", f));
    if (usingWorktree) {
      console.log("");
      console.log("Edits applied in worktree:");
      console.log("  ", worktreePath);
      console.log("Review and commit/merge from that worktree as desired.");
    } else {
      console.log("");
      console.log("WARNING: Edits were applied directly in REPO_ROOT. Use git status/commit to review.");
    }
  }

  state.currentStep = "edited";
  state.lastRunStatus = edited.length > 0 ? "ok" : "no-edits";
  state.updatedAt = new Date().toISOString();
  writeJson(STATE_FILE, state);

  appendMetrics({
    step: "edit",
    status: state.lastRunStatus,
    goal,
    files: edited,
    usingWorktree
  });
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
    await handleStatus(state, guardrails, contextLimits, hasApiKey);
    return;
  }

  // Commands that need model access
  const client = hasApiKey ? new OpenAI({ apiKey }) : null;

  if (cmd === "plan") {
    if (!client) {
      console.error("ERROR: OPENAI_API_KEY is not set. Cannot plan.");
      process.exit(1);
    }
    await handlePlan(client, args, state);
    return;
  }

  if (cmd === "test") {
    await handleTest(state);
    return;
  }

  if (cmd === "checkpoint") {
    await handleCheckpoint(args, state);
    return;
  }

  if (cmd === "edit") {
    if (!client) {
      console.error("ERROR: OPENAI_API_KEY is not set. Cannot edit.");
      process.exit(1);
    }
    await handleEdit(client, args, state, guardrails);
    return;
  }

  console.error("Unknown command:", cmd);
  console.error("Supported commands: status, plan, test, checkpoint, edit");
  process.exit(1);
}

run().catch((err) => {
  console.error("Codex Engine error:", err?.message || err);
  process.exit(1);
});
