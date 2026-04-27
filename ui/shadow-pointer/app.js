const stateCopy = {
  off: {
    label: "Off",
    workstream: "Off",
    seeing: "None",
    ignoring: "All observation stopped",
    memory: "None",
    skill: "None",
  },
  observing: {
    label: "Observing",
    workstream: "Debugging auth flow",
    seeing: "VS Code, Terminal, Chrome",
    ignoring: "password fields, private messages",
    memory: "Auth bug reproduction flow",
    skill: "Frontend auth debugging",
  },
  private_masking: {
    label: "Private Masking",
    workstream: "Debugging auth flow",
    seeing: "VS Code, Terminal",
    ignoring: "password fields, private messages, token-like text",
    memory: "Masked reproduction notes",
    skill: "Frontend auth debugging",
  },
  remembering: {
    label: "Remembering",
    workstream: "Debugging auth flow",
    seeing: "Terminal, Chrome",
    ignoring: "password fields, private messages",
    memory: "OAuth redirect mismatch and reproduction path",
    skill: "Frontend auth debugging",
  },
  agent_contexting: {
    label: "Agent Contexting",
    workstream: "Codex context pack",
    seeing: "Project memory, terminal traces, source refs",
    ignoring: "raw screenshots, masked secrets",
    memory: "Smallest safe change preference",
    skill: "Frontend auth debugging",
  },
  needs_approval: {
    label: "Needs Approval",
    workstream: "Skill gate",
    seeing: "Draft patch, test result",
    ignoring: "external send actions",
    memory: "Deployment settings require confirmation",
    skill: "Frontend auth debugging",
  },
  paused: {
    label: "Paused",
    workstream: "Observation paused",
    seeing: "None",
    ignoring: "Everything until resumed",
    memory: "None",
    skill: "None",
  },
};

const pointer = document.querySelector("#pointer");
const buttons = document.querySelectorAll("[data-state]");
const fields = {
  state: document.querySelector("#state-label"),
  pointerState: document.querySelector("#pointer-state"),
  workstream: document.querySelector("#workstream"),
  seeing: document.querySelector("#seeing"),
  ignoring: document.querySelector("#ignoring"),
  memory: document.querySelector("#memory"),
  skill: document.querySelector("#skill"),
};

function setState(nextState) {
  const copy = stateCopy[nextState] || stateCopy.observing;
  document.body.className = `state-${nextState}`;
  fields.state.textContent = copy.label;
  fields.pointerState.textContent = copy.label;
  fields.workstream.textContent = copy.workstream;
  fields.seeing.textContent = copy.seeing;
  fields.ignoring.textContent = copy.ignoring;
  fields.memory.textContent = copy.memory;
  fields.skill.textContent = copy.skill;

  buttons.forEach((button) => {
    button.classList.toggle("active", button.dataset.state === nextState);
  });
}

buttons.forEach((button) => {
  button.addEventListener("click", () => setState(button.dataset.state));
});

pointer.addEventListener("click", () => {
  const panel = document.querySelector("#panel");
  const expanded = pointer.getAttribute("aria-expanded") === "true";
  pointer.setAttribute("aria-expanded", String(!expanded));
  panel.toggleAttribute("hidden", expanded);
});

document.querySelector("#delete-recent").addEventListener("click", () => {
  setState("private_masking");
  fields.memory.textContent = "Last 10 minutes marked for deletion";
});

document.querySelector("#open-memory").addEventListener("click", () => {
  setState("agent_contexting");
});

setState("observing");

