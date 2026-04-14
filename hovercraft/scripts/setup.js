/* eslint-disable @typescript-eslint/no-require-imports */
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");
const STATE_FILE = path.join(DATA_DIR, "state.json");

function setup() {
  console.log("--- HOVERCRAFT SETUP ---");
  
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
    console.log("Created data directory.");
  }

  if (!fs.existsSync(STATE_FILE)) {
    const initialState = {
      active_circuit: "mcp",
      circuits: ["research", "mcp", "gdr"],
      lang: "ko"
    };
    fs.writeFileSync(STATE_FILE, JSON.stringify(initialState, null, 2));
    console.log("Initialized state.json.");
  }

  console.log("Setup complete.\n");
}

try {
  setup();
} catch (e) {
  console.error("Setup failed:", e);
  process.exit(1);
}
