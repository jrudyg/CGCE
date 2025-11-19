#!/usr/bin/env node
import OpenAI from "openai";
import fs from "node:fs";
import readline from "node:readline";

const DEFAULT_MODEL = "gpt-4o-mini";

/**
 * Single-shot mode (existing behavior):
 *  - codex "prompt here"
 *  - echo "prompt" | codex
 */
async function singleShot(client, args) {
  let prompt;

  if (args.length > 0) {
    prompt = args.join(" ");
  } else {
    try {
      const stdin = fs.readFileSync(0, "utf8");
      prompt = stdin;
    } catch {
      prompt = "";
    }
  }

  if (!prompt || !prompt.trim()) {
    console.error("Usage:");
    console.error('  codex "your prompt here"');
    console.error('  echo "your prompt" | codex');
    process.exit(1);
  }

  try {
    const response = await client.responses.create({
      model: DEFAULT_MODEL,
      input: prompt
    });

    const output =
      response.output_text ??
      response.output?.[0]?.content?.[0]?.text ??
      "";

    if (!output.trim()) {
      console.error("codex: received empty response from model.");
      process.exit(1);
    }

    console.log(output.trim());
  } catch (err) {
    console.error("codex error:", err?.message || err);
    process.exit(1);
  }
}

/**
 * Interactive shell:
 *  - codex shell
 */
async function shellMode(client) {
  console.log("Codex Shell");
  console.log("Model:", DEFAULT_MODEL);
  console.log("Commands: /exit, /quit, /help, /model <name>");
  console.log("");

  let currentModel = DEFAULT_MODEL;

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: "codex> "
  });

  rl.prompt();

  rl.on("line", async (line) => {
    const input = line.trim();

    if (!input) {
      rl.prompt();
      return;
    }

    if (input === "/exit" || input === "/quit") {
      rl.close();
      return;
    }

    if (input === "/help") {
      console.log("Shell commands:");
      console.log("  /help              Show this help");
      console.log("  /exit or /quit     Leave the shell");
      console.log("  /model <name>      Set model (current: " + currentModel + ")");
      console.log("Any other text is sent as a prompt to the model.");
      rl.prompt();
      return;
    }

    if (input.startsWith("/model ")) {
      const parts = input.split(/\s+/);
      if (parts.length >= 2) {
        const newModel = parts[1];
        currentModel = newModel;
        console.log("Model set to:", currentModel);
      } else {
        console.log("Usage: /model <model-name>");
      }
      rl.prompt();
      return;
    }

    // Normal prompt
    try {
      const response = await client.responses.create({
        model: currentModel,
        input: input
      });

      const output =
        response.output_text ??
        response.output?.[0]?.content?.[0]?.text ??
        "";

      if (!output.trim()) {
        console.log("[empty response]");
      } else {
        console.log(output.trim());
      }
    } catch (err) {
      console.error("codex error:", err?.message || err);
    }

    rl.prompt();
  });

  rl.on("close", () => {
    console.log("Exiting Codex Shell.");
    process.exit(0);
  });
}

async function main() {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.error("ERROR: OPENAI_API_KEY is not set.");
    console.error("Set it as a user environment variable and reopen your terminal.");
    process.exit(1);
  }

  const client = new OpenAI({ apiKey });
  const args = process.argv.slice(2);

  // Subcommand: shell
  if (args[0] === "shell") {
    await shellMode(client);
    return;
  }

  // Default: single-shot behavior
  await singleShot(client, args);
}

main();
