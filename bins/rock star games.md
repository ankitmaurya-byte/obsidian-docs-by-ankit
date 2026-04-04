candidate_profile:
  name: "Ankit Maurya"
  target_role: "Associate QA Tester - Game Functionality"
  company: "Rockstar Games"
  location: "Bengaluru, India"
  mindset:
    - "Break the system, not play it"
    - "Reproduce every issue consistently"
    - "Document everything clearly"
    - "Think like a malicious user"

core_concepts:
  testing_types:
    functional_testing:
      description: "Verify features work as expected"
      example: "Character can shoot, reload, and aim correctly"
    regression_testing:
      description: "Ensure old features still work after updates"
      example: "After patch, weapon switching still works"
    smoke_testing:
      description: "Basic sanity check after build"
      example: "Game launches, menu loads"
    exploratory_testing:
      description: "Unscripted testing to discover unknown bugs"
      example: "Spam jump + shoot near edges"

  bug_lifecycle:
    - "New"
    - "Assigned"
    - "Open"
    - "Fixed"
    - "Retest"
    - "Closed"
    - "Reopened"

  severity_priority:
    severity_levels:
      critical: "Game crash, data loss"
      high: "Major feature broken"
      medium: "Partial functionality issue"
      low: "Cosmetic issue"
    priority_levels:
      p0: "Immediate fix"
      p1: "High urgency"
      p2: "Normal"
      p3: "Low"

game_testing_domains:
  gameplay:
    - "Movement mechanics"
    - "Combat systems"
    - "AI behavior"
    - "Physics interactions"
  ui_ux:
    - "Menus"
    - "HUD elements"
    - "Button responses"
  performance:
    - "FPS drops"
    - "Memory leaks"
    - "Load times"
  compatibility:
    - "Different GPUs"
    - "Controllers vs keyboard"
    - "Resolution scaling"
  network:
    - "Multiplayer sync"
    - "Lag handling"
    - "Disconnect scenarios"

test_design:
  techniques:
    boundary_testing:
      description: "Test limits"
      example: "Max ammo, max speed"
    negative_testing:
      description: "Invalid inputs"
      example: "Spam invalid keys"
    stress_testing:
      description: "Overload system"
      example: "Spawn many NPCs"
    edge_cases:
      description: "Unusual scenarios"
      example: "Jump + shoot + reload simultaneously"

bug_report_template:
  title: "<Short clear issue>"
  environment:
    platform: "PC/Console"
    os: "Windows/Linux"
    build_version: "v1.0.0"
  steps_to_reproduce:
    - "Step 1"
    - "Step 2"
    - "Step 3"
  expected_result: "<What should happen>"
  actual_result: "<What happens>"
  reproducibility: "Always/Sometimes/Rare"
  severity: "Critical/High/Medium/Low"
  priority: "P0/P1/P2/P3"
  attachments:
    - "Screenshot"
    - "Video"
    - "Logs"

real_world_test_scenarios:
  movement:
    - "Run into wall repeatedly"
    - "Jump on uneven terrain"
    - "Spam crouch"
  combat:
    - "Shoot while reloading"
    - "Switch weapons rapidly"
    - "Fire with no ammo"
  physics:
    - "Drive vehicle into water"
    - "Crash at high speed"
    - "Stack objects"
  ai:
    - "NPC blocked path"
    - "NPC reaction delay"
    - "NPC stuck in loop"
  ui:
    - "Click buttons rapidly"
    - "Resize resolution"
    - "Open multiple menus"

practice_routine:
  daily:
    - "Play game with tester mindset"
    - "Write 3 bug reports"
    - "Analyze one game system"
  weekly:
    - "Test one full feature deeply"
    - "Simulate regression testing"
    - "Review previous bugs"

tools:
  mandatory:
    - "Microsoft Excel"
    - "Google Sheets"
  bug_tracking:
    - "JIRA"
    - "Bugzilla"
  optional:
    - "TestRail"
    - "Postman (API testing)"
    - "OBS (screen recording)"

games_to_study:
  - name: "Grand Theft Auto V"
    focus:
      - "Open world physics"
      - "Mission flow"
      - "AI behavior"
  - name: "Red Dead Redemption 2"
    focus:
      - "Realistic interactions"
      - "NPC routines"
      - "Environment systems"

interview_preparation:
  questions:
    - question: "What is a bug?"
      answer: "An issue causing deviation from expected behavior"
    - question: "How to test a door?"
      answer:
        - "Open/close repeatedly"
        - "Block it"
        - "Use during combat"
        - "Try edge timings"
    - question: "Severity vs Priority?"
      answer: "Severity = impact, Priority = urgency"
    - question: "Non-reproducible bug?"
      answer:
        - "Retry multiple times"
        - "Change environment"
        - "Capture logs"

resume_points:
  - "Performed functional and exploratory testing on applications"
  - "Created structured bug reports with reproducible steps"
  - "Tested edge cases and UI flows"
  - "Analyzed system behavior under stress conditions"

cover_letter_points:
  - "Passion for games"
  - "Detail-oriented mindset"
  - "Strong bug reporting skills"
  - "Ability to analyze systems deeply"

advanced_testing:
  systems_testing:
    - "Save/load system"
    - "Inventory system"
    - "Mission triggers"
  performance_testing:
    - "FPS benchmarking"
    - "Memory profiling"
  multiplayer_testing:
    - "Latency simulation"
    - "Sync issues"

mindset_training:
  habits:
    - "Question everything"
    - "Assume system will fail"
    - "Test beyond normal usage"
    - "Be patient and repetitive"

final_checklist:
  before_applying:
    - "Resume updated"
    - "3+ sample bug reports ready"
    - "Basic testing concepts clear"
    - "Knowledge of Rockstar games"
    - "Confident in communication"