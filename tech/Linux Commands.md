# Linux Commands

## What are Linux Commands
```
overview:
  description: Essential command-line tools for developers working on Linux/Unix systems
  shell: bash (Bourne Again Shell) is the most common default
  key_concepts:
    - Everything is a file (devices, processes, sockets)
    - Commands follow: command [options] [arguments]
    - Piping (|) connects output of one command to input of another
    - Redirection (>, >>, <) controls input/output streams
    - Exit code 0 = success, non-zero = failure
```

## File Operations
```
file_operations:

  ls:
    description: List directory contents
    commands:
      basic: "ls"
      long_format: "ls -l                          # permissions, size, date"
      show_hidden: "ls -la                         # include hidden files"
      human_sizes: "ls -lh                         # human-readable sizes"
      sort_by_time: "ls -lt                        # newest first"
      sort_by_size: "ls -lS                        # largest first"
      recursive: "ls -R                            # list subdirectories"

  cp:
    description: Copy files and directories
    commands:
      file: "cp file.txt backup.txt"
      directory: "cp -r src/ dest/                 # recursive copy"
      preserve: "cp -p file.txt backup.txt         # preserve permissions and timestamps"
      interactive: "cp -i file.txt dest/            # prompt before overwrite"
      verbose: "cp -rv src/ dest/                  # show what's being copied"

  mv:
    description: Move or rename files
    commands:
      rename: "mv old.txt new.txt"
      move: "mv file.txt /home/ankit/docs/"
      interactive: "mv -i file.txt dest/            # prompt before overwrite"

  rm:
    description: Remove files and directories
    commands:
      file: "rm file.txt"
      directory: "rm -r directory/                  # recursive delete"
      force: "rm -rf directory/                     # force, no prompts"
      interactive: "rm -i file.txt                  # confirm each file"
    warning: "rm -rf / will destroy everything, always double-check paths"

  mkdir:
    description: Create directories
    commands:
      basic: "mkdir projects"
      nested: "mkdir -p projects/go/src            # create parent dirs"

  touch:
    description: Create empty file or update timestamp
    command: "touch newfile.txt"

  find:
    description: Search for files in directory tree
    commands:
      by_name: "find /home -name '*.go'"
      case_insensitive: "find . -iname '*.jpg'"
      by_type: "find . -type f                     # files only"
      by_type_dir: "find . -type d                  # directories only"
      by_size: "find . -size +100M                  # files larger than 100MB"
      by_modified: "find . -mtime -7                # modified in last 7 days"
      execute: "find . -name '*.log' -exec rm {} \\; # delete all .log files"
      with_delete: "find /tmp -name '*.tmp' -delete"
      depth: "find . -maxdepth 2 -name '*.go'"

  chmod:
    description: Change file permissions
    commands:
      numeric: "chmod 755 script.sh                # rwxr-xr-x"
      symbolic: "chmod u+x script.sh               # add execute for owner"
      recursive: "chmod -R 644 docs/               # apply to all files in dir"
    permission_numbers: |
      4 = read (r)
      2 = write (w)
      1 = execute (x)
      755 = rwxr-xr-x (owner: all, group/other: read+execute)
      644 = rw-r--r-- (owner: read+write, group/other: read only)
      600 = rw------- (owner only)

  chown:
    description: Change file ownership
    commands:
      user: "chown ankit file.txt"
      user_group: "chown ankit:developers file.txt"
      recursive: "chown -R ankit:ankit /home/ankit/project"

  ln:
    description: Create links
    commands:
      symlink: "ln -s /path/to/original /path/to/link  # symbolic link"
      hardlink: "ln /path/to/original /path/to/link     # hard link"
```

## Text Processing
```
text_processing:

  grep:
    description: Search text using patterns
    commands:
      basic: "grep 'error' app.log"
      recursive: "grep -r 'TODO' ./src               # search all files"
      case_insensitive: "grep -i 'error' app.log"
      line_numbers: "grep -n 'func main' *.go         # show line numbers"
      count: "grep -c 'ERROR' app.log                 # count matches"
      invert: "grep -v 'DEBUG' app.log                # lines NOT matching"
      regex: "grep -E 'error|warning|fatal' app.log   # extended regex"
      context: "grep -C 3 'panic' app.log              # 3 lines before/after"
      files_only: "grep -rl 'TODO' ./src               # only file names"
      word: "grep -w 'main' *.go                      # whole word match"

  sed:
    description: Stream editor for text transformation
    commands:
      replace_first: "sed 's/old/new/' file.txt       # first occurrence per line"
      replace_all: "sed 's/old/new/g' file.txt        # all occurrences"
      in_place: "sed -i 's/old/new/g' file.txt        # edit file directly"
      delete_line: "sed '/pattern/d' file.txt          # delete matching lines"
      print_range: "sed -n '10,20p' file.txt           # print lines 10-20"
      insert_after: "sed '/pattern/a\\new line' file.txt"
      multiple: "sed -e 's/foo/bar/g' -e 's/baz/qux/g' file.txt"

  awk:
    description: Pattern scanning and text processing language
    commands:
      print_column: "awk '{print $1}' file.txt         # first column"
      specific_cols: "awk '{print $1, $3}' file.txt    # columns 1 and 3"
      delimiter: "awk -F: '{print $1}' /etc/passwd     # colon-delimited"
      with_condition: "awk '$3 > 100 {print $1, $3}' data.txt"
      sum: "awk '{sum += $1} END {print sum}' numbers.txt"
      count_lines: "awk 'END {print NR}' file.txt"
      format: "awk '{printf \"%-20s %s\\n\", $1, $2}' file.txt"

  cut:
    description: Extract columns/fields from text
    commands:
      by_delimiter: "cut -d',' -f1,3 data.csv         # fields 1 and 3"
      by_characters: "cut -c1-10 file.txt              # first 10 characters"
      from_pipe: "echo 'hello:world' | cut -d: -f2    # outputs: world"

  sort:
    description: Sort lines of text
    commands:
      basic: "sort file.txt                           # alphabetical"
      numeric: "sort -n numbers.txt                    # numeric sort"
      reverse: "sort -r file.txt                       # reverse order"
      by_column: "sort -t',' -k2 data.csv              # sort by column 2"
      unique: "sort -u file.txt                        # sort and deduplicate"
      human_numeric: "sort -h sizes.txt                 # 1K, 2M, 3G"

  uniq:
    description: Filter adjacent duplicate lines (use with sort)
    commands:
      basic: "sort file.txt | uniq                     # remove duplicates"
      count: "sort file.txt | uniq -c                  # count occurrences"
      only_dupes: "sort file.txt | uniq -d              # show only duplicates"
      only_unique: "sort file.txt | uniq -u             # show only unique lines"

  other_text_tools:
    wc: "wc -l file.txt                               # count lines"
    head: "head -n 20 file.txt                         # first 20 lines"
    tail: "tail -n 20 file.txt                         # last 20 lines"
    tail_follow: "tail -f app.log                       # follow log in real time"
    cat: "cat file.txt                                 # display file contents"
    tac: "tac file.txt                                 # display in reverse"
    less: "less file.txt                               # scrollable viewer"
    tr: "echo 'HELLO' | tr 'A-Z' 'a-z'                # translate characters"
    tee: "command | tee output.log                      # write to file AND stdout"
    xargs: "find . -name '*.log' | xargs rm            # pass input as arguments"
```

## Process Management
```
process_management:

  ps:
    description: Show running processes
    commands:
      current_user: "ps aux                            # all processes, detailed"
      tree: "ps auxf                                   # process tree"
      by_name: "ps aux | grep nginx"
      by_pid: "ps -p 1234"
      custom_format: "ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head"

  top:
    description: Real-time process monitoring
    command: "top"
    shortcuts: |
      M = sort by memory
      P = sort by CPU
      k = kill process (enter PID)
      q = quit
      1 = show per-CPU stats

  htop:
    description: Interactive process viewer (better than top)
    command: "htop"
    features:
      - "Color-coded CPU and memory bars"
      - "Mouse support"
      - "Tree view (F5)"
      - "Filter processes (F4)"
      - "Kill process (F9)"

  kill:
    description: Send signals to processes
    commands:
      graceful: "kill 1234                             # SIGTERM (graceful shutdown)"
      force: "kill -9 1234                             # SIGKILL (force kill)"
      by_name: "killall nginx                          # kill all by name"
      by_name_safe: "pkill -f 'node app.js'            # kill by pattern"
    signals: |
      SIGTERM (15) - ask process to terminate gracefully (default)
      SIGKILL (9)  - force kill immediately (cannot be caught)
      SIGHUP  (1)  - reload configuration
      SIGINT  (2)  - interrupt (Ctrl+C)

  systemctl:
    description: Manage systemd services
    commands:
      start: "sudo systemctl start nginx"
      stop: "sudo systemctl stop nginx"
      restart: "sudo systemctl restart nginx"
      reload: "sudo systemctl reload nginx            # reload config without restart"
      status: "sudo systemctl status nginx"
      enable: "sudo systemctl enable nginx             # start on boot"
      disable: "sudo systemctl disable nginx"
      list: "systemctl list-units --type=service"
      logs: "journalctl -u nginx -f                    # follow service logs"

  background_jobs:
    background: "long-command &                         # run in background"
    list: "jobs                                        # list background jobs"
    foreground: "fg %1                                  # bring job 1 to foreground"
    nohup: "nohup long-command > output.log 2>&1 &     # survive terminal close"
```

## Networking
```
networking:

  curl:
    description: Transfer data with URLs (HTTP client)
    commands:
      get: "curl https://api.example.com/users"
      post_json: "curl -X POST -H 'Content-Type: application/json' -d '{\"name\":\"Ankit\"}' https://api.example.com/users"
      with_headers: "curl -H 'Authorization: Bearer token123' https://api.example.com/me"
      download: "curl -O https://example.com/file.tar.gz"
      follow_redirect: "curl -L https://example.com/redirect"
      verbose: "curl -v https://api.example.com/health"
      silent: "curl -s https://api.example.com/data | jq ."
      with_output: "curl -o output.json https://api.example.com/data"
      timeout: "curl --connect-timeout 5 -m 30 https://api.example.com/slow"

  wget:
    description: Download files from the web
    commands:
      download: "wget https://example.com/file.tar.gz"
      rename: "wget -O custom-name.tar.gz https://example.com/file.tar.gz"
      recursive: "wget -r -l 2 https://example.com/docs/"
      continue: "wget -c https://example.com/large-file.iso  # resume download"

  ss:
    description: Socket statistics (modern replacement for netstat)
    commands:
      listening: "ss -tlnp                             # TCP listening ports with process"
      all_tcp: "ss -ta                                 # all TCP connections"
      by_port: "ss -tlnp | grep :8080                  # what's on port 8080"
      summary: "ss -s                                   # connection summary"

  netstat:
    description: Network statistics (older, still widely available)
    commands:
      listening: "netstat -tlnp                         # TCP listening ports"
      all: "netstat -an                                 # all connections"
      routing: "netstat -r                              # routing table"

  ping:
    description: Test network connectivity
    commands:
      basic: "ping google.com"
      count: "ping -c 4 google.com                     # send 4 packets"
      timeout: "ping -W 2 192.168.1.1                  # 2 second timeout"

  traceroute:
    description: Show network path to destination
    command: "traceroute google.com"

  ip:
    description: Network interface and routing configuration
    commands:
      show_interfaces: "ip addr show                   # all interfaces and IPs"
      specific: "ip addr show eth0                     # specific interface"
      routing_table: "ip route show                    # routing table"
      add_ip: "sudo ip addr add 192.168.1.100/24 dev eth0"

  dns:
    dig: "dig example.com                              # DNS lookup"
    nslookup: "nslookup example.com"
    host: "host example.com"

  other:
    nc: "nc -zv hostname 80                            # test if port is open"
    ssh_tunnel: "ssh -L 8080:localhost:3000 user@server # local port forwarding"
```

## Disk Management
```
disk_management:

  df:
    description: Show disk space usage
    commands:
      human: "df -h                                    # human-readable sizes"
      specific: "df -h /home                           # specific mount point"
      type: "df -hT                                    # show filesystem type"
      inodes: "df -i                                    # inode usage"

  du:
    description: Show directory/file sizes
    commands:
      summary: "du -sh /home/ankit                     # total size of directory"
      top_level: "du -h --max-depth=1 /home            # size per subdirectory"
      largest: "du -h --max-depth=1 / | sort -rh | head -10  # 10 largest dirs"
      specific_file: "du -h file.tar.gz"

  mount:
    description: Mount filesystems
    commands:
      list: "mount                                     # show all mounts"
      mount_disk: "sudo mount /dev/sdb1 /mnt/data"
      unmount: "sudo umount /mnt/data"
      fstab: "cat /etc/fstab                           # persistent mounts"

  lsblk:
    description: List block devices
    command: "lsblk                                    # show disks and partitions"

  fdisk:
    description: Disk partitioning
    command: "sudo fdisk -l                            # list all partitions"
```

## Package Managers
```
package_managers:

  apt:
    description: Debian/Ubuntu package manager
    commands:
      update: "sudo apt update                         # refresh package index"
      install: "sudo apt install nginx"
      remove: "sudo apt remove nginx"
      purge: "sudo apt purge nginx                     # remove with config files"
      upgrade_all: "sudo apt upgrade                   # upgrade all packages"
      search: "apt search nginx"
      info: "apt show nginx                            # package details"
      autoremove: "sudo apt autoremove                  # remove unused dependencies"
      list_installed: "apt list --installed"

  yum:
    description: RHEL/CentOS package manager (dnf on newer systems)
    commands:
      install: "sudo yum install nginx"
      remove: "sudo yum remove nginx"
      update: "sudo yum update"
      search: "yum search nginx"
      info: "yum info nginx"
      list_installed: "yum list installed"
      dnf: "sudo dnf install nginx                     # modern replacement"
```

## SSH
```
ssh:

  commands:
    connect: "ssh user@hostname"
    with_port: "ssh -p 2222 user@hostname"
    with_key: "ssh -i ~/.ssh/mykey.pem user@hostname"

  key_management:
    generate: "ssh-keygen -t ed25519 -C 'ankit@example.com'"
    copy_to_server: "ssh-copy-id user@hostname"
    config_file: |
      # ~/.ssh/config
      Host myserver
        HostName 192.168.1.100
        User ankit
        Port 22
        IdentityFile ~/.ssh/mykey

  tunneling:
    local_forward: "ssh -L 8080:localhost:3000 user@server  # access server:3000 via localhost:8080"
    remote_forward: "ssh -R 8080:localhost:3000 user@server # expose local:3000 on server:8080"
    socks_proxy: "ssh -D 1080 user@server                   # SOCKS proxy"

  file_transfer:
    scp_to: "scp file.txt user@server:/home/user/"
    scp_from: "scp user@server:/home/user/file.txt ."
    scp_recursive: "scp -r ./project user@server:/home/user/"
    rsync: "rsync -avz ./project/ user@server:/home/user/project/"
```

## tmux
```
tmux:

  description: Terminal multiplexer - multiple sessions, windows, and panes in one terminal

  commands:
    new_session: "tmux new -s myproject"
    list_sessions: "tmux ls"
    attach: "tmux attach -t myproject"
    detach: "Ctrl+b d"
    kill_session: "tmux kill-session -t myproject"

  key_bindings:
    prefix: "Ctrl+b (all shortcuts start with this)"

    windows:
      create: "Ctrl+b c                               # new window"
      next: "Ctrl+b n                                  # next window"
      previous: "Ctrl+b p                              # previous window"
      select: "Ctrl+b 0-9                              # go to window by number"
      rename: "Ctrl+b ,                                # rename window"
      close: "Ctrl+b &                                 # close window"

    panes:
      split_horizontal: "Ctrl+b %                      # split left/right"
      split_vertical: "Ctrl+b \"                       # split top/bottom"
      navigate: "Ctrl+b arrow-keys                     # move between panes"
      resize: "Ctrl+b Ctrl+arrow-keys                  # resize pane"
      close: "Ctrl+b x                                 # close pane"
      zoom: "Ctrl+b z                                  # toggle fullscreen pane"

  common_workflow: |
    # Start a project session with multiple windows
    tmux new -s project
    # Window 0: editor (vim/nvim)
    # Ctrl+b c -> Window 1: server (go run main.go)
    # Ctrl+b c -> Window 2: git operations
    # Ctrl+b c -> Window 3: logs (tail -f app.log)
    # Ctrl+b d to detach, tmux attach -t project to return
```

## Piping and Redirection
```
piping_and_redirection:

  piping:
    description: Send output of one command as input to another
    examples:
      basic: "ls -la | grep '.go'                     # find .go files"
      chain: "cat access.log | grep 'POST' | wc -l    # count POST requests"
      sort_uniq: "cut -d' ' -f1 access.log | sort | uniq -c | sort -rn | head  # top IPs"
      filter: "ps aux | grep nginx | grep -v grep"
      format: "docker ps | awk '{print $1, $2}'       # container IDs and images"

  output_redirection:
    overwrite: "command > file.txt                     # stdout to file (overwrite)"
    append: "command >> file.txt                       # stdout to file (append)"
    stderr: "command 2> errors.log                     # stderr to file"
    both: "command > output.log 2>&1                   # both stdout and stderr"
    both_modern: "command &> output.log                 # shorthand for both"
    discard: "command > /dev/null 2>&1                  # discard all output"
    separate: "command > stdout.log 2> stderr.log      # separate files"

  input_redirection:
    from_file: "command < input.txt                    # read input from file"
    heredoc: |
      cat <<EOF > config.yaml
      server:
        port: 8080
        host: 0.0.0.0
      EOF

  useful_patterns:
    tee: "command | tee output.log                     # write to file AND show on screen"
    process_substitution: "diff <(sort file1.txt) <(sort file2.txt)  # diff sorted versions"
    command_substitution: "echo \"Today is $(date)\"   # embed command output"
    xargs: "find . -name '*.tmp' | xargs rm            # pass stdin as arguments"
    xargs_parallel: "find . -name '*.go' | xargs -P 4 -I {} go build {}  # parallel execution"

  operators:
    and: "command1 && command2                          # run command2 only if command1 succeeds"
    or: "command1 || command2                           # run command2 only if command1 fails"
    sequence: "command1; command2                       # run both regardless of exit code"
    background: "command &                              # run in background"
```

## Useful One-Liners
```
one_liners:

  system_info:
    os_version: "cat /etc/os-release"
    kernel: "uname -r"
    uptime: "uptime"
    memory: "free -h"
    cpu_info: "lscpu"
    hostname: "hostname"
    who_is_logged_in: "w"

  file_operations:
    find_large_files: "find / -type f -size +500M 2>/dev/null | head -20"
    find_recently_modified: "find . -type f -mmin -30          # modified in last 30 min"
    count_files_by_extension: "find . -type f | sed 's/.*\\.//' | sort | uniq -c | sort -rn"
    replace_in_files: "find . -name '*.go' -exec sed -i 's/oldFunc/newFunc/g' {} +"
    tar_compress: "tar -czf archive.tar.gz directory/"
    tar_extract: "tar -xzf archive.tar.gz"

  monitoring:
    watch_command: "watch -n 2 'docker ps'              # run every 2 seconds"
    disk_usage_alert: "df -h | awk '$5+0 > 80 {print $0}' # partitions over 80%"
    port_check: "ss -tlnp | grep :8080"
    open_files: "lsof -i :8080                          # what's using port 8080"
    memory_by_process: "ps aux --sort=-%mem | head -10"
    cpu_by_process: "ps aux --sort=-%cpu | head -10"

  text_processing:
    json_pretty: "cat data.json | jq ."
    csv_column: "awk -F',' '{print $2}' data.csv"
    count_lines: "wc -l *.go"
    remove_blank_lines: "sed '/^$/d' file.txt"
    extract_ips: "grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+' access.log | sort -u"
    top_10_lines: "sort file.txt | uniq -c | sort -rn | head -10"
```
