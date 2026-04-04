# Git

## What is Git
```
overview:
  type: Distributed version control system
  created_by: Linus Torvalds (2005)
  key_traits:
    - Distributed (every clone is a full repository)
    - Snapshots, not diffs (each commit is a complete snapshot)
    - Integrity via SHA-1 hashes (every object has a unique hash)
    - Branching is cheap and fast (just a pointer to a commit)
    - Staging area (index) for crafting commits
```

## Git Internals
```
internals:

  objects:
    blob:
      description: File contents (no filename, just raw data)
      example: "git hash-object -w file.txt"
    tree:
      description: Directory listing (maps filenames to blob/tree hashes)
      example: "git cat-file -p HEAD^{tree}"
    commit:
      description: Snapshot pointer with metadata (tree, parent, author, message)
      example: "git cat-file -p HEAD"
    tag:
      description: Named pointer to a commit (annotated tags are objects)
      example: "git cat-file -p v1.0"

  storage: |
    .git/
      objects/    # all blobs, trees, commits (content-addressed)
      refs/       # branches and tags (pointers to commits)
        heads/    # local branches
        remotes/  # remote-tracking branches
        tags/     # tag references
      HEAD        # pointer to current branch (ref: refs/heads/main)
      index       # staging area (binary file)
      config      # repository-level config

  refs:
    HEAD: "Points to current branch (ref: refs/heads/main) or detached commit"
    branch: "Just a file containing a commit hash (refs/heads/main)"
    tag: "Named pointer to a specific commit (refs/tags/v1.0)"
    remote_tracking: "refs/remotes/origin/main - last known state of remote branch"

  how_commits_work: |
    1. git add -> copies files to staging area (index)
    2. git commit -> creates tree object from index, then commit object
    3. Commit points to: tree (snapshot), parent commit(s), metadata
    4. Branch pointer moves forward to new commit
    5. HEAD follows the branch pointer
```

## Essential Commands
```
commands:

  setup:
    init: "git init                           # create new repo"
    clone: "git clone <url>                    # clone remote repo"
    config_name: "git config --global user.name 'Ankit'"
    config_email: "git config --global user.email 'ankit@example.com'"

  basic_workflow:
    status: "git status                        # show working tree status"
    add_file: "git add file.go                  # stage specific file"
    add_all: "git add .                         # stage all changes"
    commit: "git commit -m 'add user auth'     # commit staged changes"
    push: "git push origin main               # push to remote"
    pull: "git pull origin main               # fetch + merge"
    fetch: "git fetch origin                   # download without merging"

  diff:
    working: "git diff                          # unstaged changes"
    staged: "git diff --staged                 # staged changes"
    between_commits: "git diff abc123..def456   # diff between two commits"
    between_branches: "git diff main..feature   # diff between branches"

  log:
    basic: "git log                            # full commit history"
    oneline: "git log --oneline                 # compact one-line format"
    graph: "git log --oneline --graph --all    # visual branch graph"
    by_author: "git log --author='Ankit'        # filter by author"
    by_file: "git log -- path/to/file.go       # history of specific file"
    since: "git log --since='2025-01-01'       # commits after date"
    search: "git log --grep='fix bug'          # search commit messages"
    show_commit: "git show abc123               # show commit details + diff"

  remote:
    list: "git remote -v                       # show remotes"
    add: "git remote add origin <url>          # add remote"
    remove: "git remote remove origin           # remove remote"
    set_url: "git remote set-url origin <url>   # change remote URL"
```

## Branching
```
branching:

  commands:
    list: "git branch                          # list local branches"
    list_all: "git branch -a                    # include remote branches"
    create: "git branch feature/auth            # create branch"
    switch: "git checkout feature/auth          # switch to branch"
    create_switch: "git checkout -b feature/auth # create and switch"
    delete: "git branch -d feature/auth         # delete merged branch"
    force_delete: "git branch -D feature/auth   # delete unmerged branch"
    rename: "git branch -m old-name new-name    # rename branch"

  strategies:
    gitflow:
      description: |
        Formal branching model with dedicated branches for features,
        releases, and hotfixes. Good for scheduled releases.
      branches:
        main: "Production-ready code, tagged releases"
        develop: "Integration branch for features"
        feature: "feature/* - branched from develop, merged back to develop"
        release: "release/* - branched from develop, merged to main + develop"
        hotfix: "hotfix/* - branched from main, merged to main + develop"
      flow: |
        develop -> feature/auth -> develop -> release/1.0 -> main
        main -> hotfix/fix-crash -> main + develop

    trunk_based:
      description: |
        Everyone commits to main (trunk) frequently. Short-lived
        feature branches (1-2 days max). Relies on feature flags.
      principles:
        - "Small, frequent commits to main"
        - "Feature branches live < 2 days"
        - "Feature flags for incomplete features"
        - "CI/CD runs on every push to main"
      best_for: "Teams practicing continuous delivery"

    github_flow:
      description: |
        Simplified model: main branch + feature branches + pull requests.
      flow: |
        1. Create branch from main
        2. Make commits
        3. Open pull request
        4. Code review
        5. Merge to main
        6. Deploy
```

## Merge vs Rebase
```
merge_vs_rebase:

  merge:
    command: |
      git checkout main
      git merge feature/auth
    description: Creates a merge commit combining two branches
    result: |
      * Merge branch 'feature/auth' into main  (merge commit)
      |\
      | * Add token validation
      | * Add login endpoint
      |/
      * Previous main commit
    pros:
      - Preserves complete history and branch topology
      - Non-destructive (doesn't rewrite history)
      - Easy to understand what was merged and when
    cons:
      - Creates extra merge commits (cluttered history)
    when_to_use: "Merging feature branches into main, shared branches"

  rebase:
    command: |
      git checkout feature/auth
      git rebase main
    description: Replays feature commits on top of main (rewrites history)
    result: |
      * Add token validation     (new hash, rebased)
      * Add login endpoint       (new hash, rebased)
      * Previous main commit
    pros:
      - Clean linear history (no merge commits)
      - Easier to read git log
    cons:
      - Rewrites commit hashes (NEVER rebase shared/pushed branches)
      - Can cause confusion if others based work on original commits
    when_to_use: "Updating local feature branch with latest main before merging"

  golden_rule: |
    NEVER rebase commits that have been pushed to a shared branch.
    Only rebase your own local, unpushed work.

  common_workflow: |
    # Update feature branch with latest main, then merge
    git checkout feature/auth
    git rebase main              # replay feature on top of latest main
    git checkout main
    git merge feature/auth       # fast-forward merge (linear)
```

## Cherry-Pick
```
cherry_pick:

  description: Apply a specific commit from one branch to another

  commands:
    single: "git cherry-pick abc123                # apply one commit"
    multiple: "git cherry-pick abc123 def456        # apply multiple commits"
    range: "git cherry-pick abc123..def456          # apply range (exclusive start)"
    no_commit: "git cherry-pick --no-commit abc123  # apply changes without committing"
    abort: "git cherry-pick --abort                 # cancel in-progress cherry-pick"

  when_to_use:
    - "Backport a bug fix from main to a release branch"
    - "Pull a specific feature commit without merging entire branch"
    - "Recover a commit from a deleted branch"

  example: |
    # Hotfix on main needs to go to release/1.0
    git checkout release/1.0
    git cherry-pick abc123        # the specific fix commit
    git push origin release/1.0
```

## Stash
```
stash:

  description: Temporarily save uncommitted changes and clean working directory

  commands:
    save: "git stash                              # stash tracked changes"
    save_message: "git stash push -m 'WIP: auth' # stash with description"
    include_untracked: "git stash -u               # include untracked files"
    list: "git stash list                          # show all stashes"
    apply: "git stash apply                        # apply latest, keep in stash"
    pop: "git stash pop                            # apply latest, remove from stash"
    apply_specific: "git stash apply stash@{2}     # apply specific stash"
    drop: "git stash drop stash@{0}                # delete specific stash"
    clear: "git stash clear                        # delete all stashes"
    show: "git stash show -p stash@{0}             # show stash diff"

  common_use: |
    # Need to switch branches but have uncommitted work
    git stash
    git checkout main
    # do something on main
    git checkout feature/auth
    git stash pop
```

## Reset
```
reset:

  soft:
    command: "git reset --soft HEAD~1"
    description: Move HEAD back, keep changes staged
    use_case: "Undo last commit but keep changes ready to re-commit"
    what_changes:
      HEAD: moves back
      staging_area: unchanged (changes stay staged)
      working_directory: unchanged

  mixed:
    command: "git reset HEAD~1"
    description: Move HEAD back, unstage changes (default mode)
    use_case: "Undo commit and unstage, but keep files modified"
    what_changes:
      HEAD: moves back
      staging_area: reset (changes become unstaged)
      working_directory: unchanged

  hard:
    command: "git reset --hard HEAD~1"
    description: Move HEAD back, discard ALL changes
    use_case: "Completely undo last commit and all changes"
    what_changes:
      HEAD: moves back
      staging_area: reset
      working_directory: reset (changes GONE)
    warning: "Destructive! Use reflog to recover if needed"

  reset_file:
    unstage: "git reset HEAD file.go               # unstage a file"
    restore: "git checkout -- file.go               # discard working dir changes"
    modern: "git restore --staged file.go           # unstage (modern syntax)"
```

## Reflog
```
reflog:

  description: |
    Records every change to HEAD and branch tips. Your safety net
    for recovering from mistakes. Entries kept for 90 days by default.

  commands:
    view: "git reflog                              # show HEAD movements"
    branch: "git reflog show feature/auth           # show branch movements"
    with_dates: "git reflog --date=relative          # show relative dates"

  recover_scenarios:
    after_hard_reset: |
      git reflog
      # Find the commit hash before the reset
      # abc123 HEAD@{1}: commit: add user auth
      git reset --hard abc123

    deleted_branch: |
      git reflog
      # Find last commit of deleted branch
      git checkout -b recovered-branch abc123

    bad_rebase: |
      git reflog
      # Find the commit before rebase started
      # abc123 HEAD@{5}: checkout: moving from main to feature
      git reset --hard abc123

  note: "Reflog is LOCAL only, not shared with remotes"
```

## Bisect
```
bisect:

  description: |
    Binary search through commit history to find which commit
    introduced a bug. Tests O(log n) commits instead of all of them.

  manual: |
    git bisect start
    git bisect bad                 # current commit is broken
    git bisect good v1.0           # v1.0 was working fine

    # Git checks out a middle commit
    # Test it manually, then:
    git bisect good                # this commit is fine
    # or
    git bisect bad                 # this commit is broken

    # Repeat until Git finds the first bad commit
    # "abc123 is the first bad commit"

    git bisect reset               # go back to original HEAD

  automated: |
    # Run a test script automatically on each commit
    git bisect start HEAD v1.0
    git bisect run go test ./...
    # Git automatically tests commits and finds the bad one

  tip: "Works best with small, focused commits"
```

## Interactive Rebase
```
interactive_rebase:

  description: Rewrite commit history by editing, squashing, reordering, or dropping commits

  command: "git rebase -i HEAD~5               # edit last 5 commits"

  options: |
    pick   abc123 Add user model          # keep commit as-is
    reword def456 Fix typo                # edit commit message
    edit   ghi789 Add auth middleware     # stop to amend commit
    squash jkl012 Fix auth bug            # merge into previous commit (keep message)
    fixup  mno345 Lint fix                # merge into previous, discard message
    drop   pqr678 Debug logging           # remove commit entirely

  common_uses:
    squash_commits: |
      # Combine 3 WIP commits into one clean commit before merging
      git rebase -i HEAD~3
      # Change "pick" to "squash" for the last 2 commits

    reword_message: |
      # Fix a commit message
      git rebase -i HEAD~2
      # Change "pick" to "reword" for the target commit

    reorder_commits: |
      # Rearrange the order of lines in the editor
      # Commits are applied top to bottom

  warning: "Only rebase unpushed commits. Never rebase shared history."
```

## .gitignore
```
gitignore:

  description: Specifies files and directories Git should ignore

  common_patterns: |
    # Binaries and build output
    /bin/
    /dist/
    /build/
    *.exe
    *.o
    *.so

    # Dependencies
    node_modules/
    vendor/

    # Environment and secrets
    .env
    .env.local
    *.pem
    *.key

    # IDE and OS files
    .vscode/
    .idea/
    *.swp
    .DS_Store
    Thumbs.db

    # Logs
    *.log
    logs/

    # Go specific
    go.sum

    # Test coverage
    coverage/
    *.cover
    *.out

  syntax:
    comment: "# this is a comment"
    directory: "logs/              # ignore directory"
    wildcard: "*.log               # all .log files"
    negation: "!important.log      # don't ignore this file"
    root_only: "/build             # only root /build, not src/build"
    double_star: "**/logs          # logs directory anywhere in tree"

  already_tracked: |
    # File already tracked? .gitignore won't help
    # Remove from tracking but keep the file:
    git rm --cached file.env
    # Then add to .gitignore
```

## Git Hooks
```
hooks:

  description: Scripts that run automatically at certain Git events

  location: ".git/hooks/ (local, not committed to repo)"

  common_hooks:
    pre_commit:
      runs: "Before commit is created"
      use_cases:
        - "Run linter (golangci-lint, eslint)"
        - "Run formatter (gofmt, prettier)"
        - "Check for secrets (detect-secrets)"
        - "Run unit tests"
      example: |
        #!/bin/sh
        # .git/hooks/pre-commit
        echo "Running linter..."
        golangci-lint run ./...
        if [ $? -ne 0 ]; then
          echo "Lint failed. Fix issues before committing."
          exit 1
        fi

    commit_msg:
      runs: "After commit message is entered"
      use_cases:
        - "Enforce commit message format"
        - "Check for ticket number in message"
      example: |
        #!/bin/sh
        # .git/hooks/commit-msg
        if ! grep -qE "^(feat|fix|docs|refactor|test|chore):" "$1"; then
          echo "Commit message must start with: feat:|fix:|docs:|refactor:|test:|chore:"
          exit 1
        fi

    pre_push:
      runs: "Before push to remote"
      use_cases:
        - "Run full test suite"
        - "Prevent push to main/master directly"

  shared_hooks: |
    # Use tools like Husky (JS) or lefthook (any) for team-wide hooks
    # Committed to repo, installed automatically

    # Husky (package.json)
    npm install --save-dev husky
    npx husky init
    echo "npm test" > .husky/pre-commit
```

## Resolving Conflicts
```
conflicts:

  when_they_happen: |
    - Merging branches that modified the same lines
    - Rebasing onto a branch with conflicting changes
    - Cherry-picking a commit that conflicts

  conflict_markers: |
    <<<<<<< HEAD
    const port = 3000;        // your changes (current branch)
    =======
    const port = 8080;        // their changes (incoming branch)
    >>>>>>> feature/new-port

  resolution_steps: |
    1. git status                     # see conflicting files
    2. Open conflicting file in editor
    3. Choose one side, combine both, or write new code
    4. Remove conflict markers (<<<, ===, >>>)
    5. git add resolved-file.go       # mark as resolved
    6. git commit                     # complete the merge (or git rebase --continue)

  abort: |
    git merge --abort                 # cancel merge
    git rebase --abort                # cancel rebase
    git cherry-pick --abort           # cancel cherry-pick

  tips:
    - "Pull frequently to reduce conflict size"
    - "Keep commits small and focused"
    - "Communicate with team about shared files"
    - "Use git diff --name-only main to see what you changed"
```

## Best Practices
```
best_practices:

  commits:
    - "Commit often, push frequently"
    - "Each commit should be one logical change"
    - "Write clear commit messages: 'fix user auth token expiry' not 'fix bug'"
    - "Use conventional commits: feat:, fix:, docs:, refactor:, test:, chore:"
    - "Never commit secrets, credentials, or .env files"

  branching:
    - "Keep feature branches short-lived (1-3 days)"
    - "Name branches descriptively: feature/user-auth, fix/login-crash"
    - "Delete branches after merging"
    - "Protect main branch with required reviews"

  workflow:
    - "Pull before you push"
    - "Rebase local work before merging (cleaner history)"
    - "Use pull requests for code review"
    - "Squash WIP commits before merging to main"
    - "Tag releases: git tag -a v1.0.0 -m 'Release 1.0.0'"

  recovery:
    - "Use reflog to recover from mistakes"
    - "Don't panic after a bad reset or rebase"
    - "Never force push to shared branches"
    - "When in doubt, create a backup branch first"
```
