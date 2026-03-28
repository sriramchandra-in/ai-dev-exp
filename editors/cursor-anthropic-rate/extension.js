"use strict";
const vscode = require("vscode");
const { execFile } = require("child_process");

/**
 * @param {string} cliPath
 * @param {(text: string) => void} done
 */
function runBrief(cliPath, done) {
  execFile(
    cliPath,
    ["anthropic-rate-brief"],
    { env: process.env, timeout: 120000 },
    (_err, stdout) => {
      done((stdout || "").trim());
    },
  );
}

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  const sb = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 99);
  sb.command = "aiDevExp.refreshAnthropicRate";
  sb.tooltip =
    "Anthropic API rate limits (from Messages response headers). " +
    "Not Cursor subscription usage. Requires ANTHROPIC_API_KEY in the environment that launched Cursor.";

  const refresh = () => {
    const cfg = vscode.workspace.getConfiguration();
    const cliPath = cfg.get("aiDevExp.anthropicRateCliPath", "ai-dev-exp");
    sb.text = "API …";
    sb.show();
    runBrief(cliPath, (text) => {
      sb.text = text || "$(warning) Anthropic: (no output)";
      sb.show();
    });
  };

  refresh();
  const minutes = vscode.workspace
    .getConfiguration()
    .get("aiDevExp.anthropicRateIntervalMinutes", 3);
  const intervalMs = Math.max(60000, (minutes || 3) * 60000);
  const timer = setInterval(refresh, intervalMs);

  context.subscriptions.push(
    sb,
    vscode.commands.registerCommand("aiDevExp.refreshAnthropicRate", refresh),
    { dispose: () => clearInterval(timer) },
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
