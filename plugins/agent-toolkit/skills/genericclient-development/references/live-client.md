# Live client and account workflow

Read this reference for live RuneLite interaction, account progression, MCP
work, or a bug that depends on visible client state.

## Current paths

- Source repository: `/home/user/GenericClient`
- Built JAR: `/home/user/GenericClient/build/libs/GenericClient-0.12.0-all.jar`
- Installed JAR: `/mnt/c/Users/User/AppData/Local/GenericClient/GenericClient.jar`
- Installed scripts and state: `/mnt/c/Users/User/.runelite/genericclient`
- RuneLite log: `/mnt/c/Users/User/.runelite/logs/client.log`
- Local control bridge: `http://127.0.0.1:17343/rpc`

Resolve process IDs, window handles, account position, schema, and hashes each
time. Never reuse an old PID, HWND, or coordinate as current fact.

## Read before acting

1. `client_status`: login state, player location, active Lua/REPL, behavior,
   safety, recent logs, and chat/system messages.
2. `account_snapshot`: exact skills/XP, inventory, equipment, quest states, GE
   offers, and bank/cash confidence. An unknown bank is not an empty bank.
3. `client_screenshot`: visible ambiguity, including black screens, camera
   occlusion, dialogues, level-up panels, menus, or a walker that appears stuck.
4. Targeted `lua_eval`: immutable exploration before mutation. Return compact
   structured receipts.

Chat messages are evidence. Include recent messages when diagnosing level-ups,
random events, reachability errors, locks, deaths, and quest transitions.

## Interaction rules

- Novel, visibly wrong, or poorly understood quest behavior is a stop condition.
  Stop the active script safely, inspect `client_status`, the account snapshot,
  screenshot, and relevant recent messages, then compare the exact installed
  RuneLite Quest Helper guidance. Ask before recovery; a broad instruction to
  finish the quest does not override this boundary. Use Quest Helper during
  development and diagnosis, keeping runtime Lua standalone.
- Use semantic Lua actions through synthetic/client-only input. Do not move the
  machine's OS cursor.
- Use exact NPC/object/item IDs when available. Re-resolve moving actors at
  click time and verify `MenuOptionClicked` receipts.
- A composite movement-plus-click is one top-level interaction for break logic.
  Pass `breaks=false` through every action in time-sensitive critical sections.
- Walking waits for progress/arrival and retains its accepted waypoint. It
  remembers live solid edges for the active walk and uses accessible traversal
  objects rather than spam-clicking.
- Level-up and ordinary Continue dialogues can interrupt autocast. Combat loops
  must dismiss them and explicitly resume the expected NPC ID.

## Safety and food

- Configure `safety.configure` with ordered approved consumables and exact
  `heal_amount` values.
- Normal combat consumes when the complete heal fits, avoiding overheal.
- Below 30% max HP the framework forces approved food even if a low-max-HP
  account must overheal. A successful food action continues combat.
- At the forced-heal point or hard floor, unavailable food stops the script and
  uses the configured escape when present.
- Sudden-death handling preempts breaks and ordinary script execution. Verify
  the resulting food/escape receipt; do not assume it fired.

## Account mutation

- Read the active goal and account note before purchases or training.
- Enforce the current explicit hard stat caps and cash reserve. Use exact XP
  stops, not approximate levels.
- Buy only the next required deficit, bank first when the workflow specifies
  JIT purchasing, and preserve unrelated GE offers.
- Do not buy or redeem bonds, transfer wealth, drop valuables, or enter risk PvP
  unless the current user instruction explicitly authorizes that action.
- Record only verified milestones in account notes. Label old exact cash audits
  as old when the bank cache is currently unknown.

## Long operations

Run monitors with local background jobs. A useful state-change line includes:

- script status and active script;
- player x/y and HP;
- safety last event;
- behavior state and remaining break time;
- last client status.

Treat `COMPLETED`, `FAULTED`, and `IDLE` as terminal. Cancel the monitor when the
script is manually stopped. A quiet monitor is not proof that RuneLite stopped;
refresh `client_status` directly.

The user has previously authorized manual break cancellation during active
validation. Re-check current instructions before relying on that authority in a
new context.
