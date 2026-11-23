const fs = require("fs");
const os = require("os");
const path = require("path");

const PATTERNS = [
  /\bkaggle\b[\s\S]{0,40}\b(competitions?|comps?|kompetisi|lomba|challenge|leaderboard|lb)\b/i,
  /\b(competitions?|kompetisi|lomba|challenge)\b[\s\S]{0,40}\bkaggle\b/i,
  /kaggle\.com\/(c|competitions)\//i,
];

function readStdin() {
  try {
    return fs.readFileSync(0, "utf8");
  } catch (e) {
    return "";
  }
}

let prompt = "";
try {
  const data = JSON.parse(readStdin() || "{}");
  prompt = String(data.prompt || data.user_prompt || "");
} catch (e) {
  prompt = "";
}

if (!PATTERNS.some((re) => re.test(prompt))) {
  process.exit(0);
}

const lessons = path.join(os.homedir(), ".claude", "kaggle-competition", "LESSONS.md");
const hasLessons = fs.existsSync(lessons);

const context = [
  "Kaggle competition context detected by the kaggle-competition plugin.",
  "If the kaggle-competition:workflow skill is not loaded in this session yet, load it with the Skill tool before planning or coding, and follow its phases.",
  "Treat the competition's rules, FAQ and the project's comp_notes/RULES.md ledger as a hard gate for every technique; when a rule is unclear, ask the user or the organizers instead of guessing.",
  hasLessons
    ? `Read the cross-competition lessons file before planning: ${lessons}`
    : `No cross-competition lessons file yet; create it at ${lessons} when the first lesson is recorded.`,
].join(" ");

process.stdout.write(
  JSON.stringify({
    hookSpecificOutput: { hookEventName: "UserPromptSubmit", additionalContext: context },
  })
);
