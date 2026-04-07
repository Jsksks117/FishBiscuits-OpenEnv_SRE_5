# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
SRE Agent Task Definitions.

Each task defines:
  - name: Human-readable task title
  - difficulty: easy / medium / hard
  - description: What the agent is told (the "goal")
  - setup_script: Bash script injected into the container to create the bug
  - grade(container): Deterministic grading function returning 0.0–1.0
"""

import logging

logger = logging.getLogger(__name__)

def _get_history(container) -> str:
    """Retrieves the bash history to check for messy or brute-force commands."""
    return _exec(container, "cat ~/.bash_history || echo ''")

# ---------------------------------------------------------------------------
#  Task Registry
# ---------------------------------------------------------------------------

TASK_DEFINITIONS = {
"task_1_permissions": {
    "name": "Fix File Permissions",
    "difficulty": "easy",
    # "description": (
    #     "A critical web page file at /var/www/html/index.html has had its "
    #     "permissions completely removed (set to 000). No user can read it. "
    #     "Fix the file permissions so the web server can serve the file. "
    #     "The recommended permission is 644 (owner read/write, others read)."
    # ),
    "description": (
        "A critical web page file somewhere inside var has had its "
        "permissions completely removed (set to 000). No user can read it. "
        "Fix the html file permissions(only) so the web server can serve the file. "
        "so that owner can read/write, and others can read."
    ),
    "setup_script": (
        "set -e\n"
        "mkdir -p /var/www/html\n"
        "echo '<h1>Welcome to SRE Agent Server</h1>"
        "<p>Service is operational.</p>' > /var/www/html/index.html\n"
        "chmod 000 /var/www/html/index.html\n"
    ),
},
"task_2_service": {
    "name": "Restart Crashed Web Server",
    "difficulty": "medium",
    "description": (
        "The nginx web server has crashed unexpectedly and left a stale "
        "PID file somewhere. The server needs to be restarted and "
        "listening on port 80. Diagnose the issue, clean up any stale state, "
        "and restart the service.\n"
        "give step by step commands to fix the issue.\n"
        "IMPORTANT: This is a Docker container — use 'service nginx start' "
        "instead of 'systemctl'."
    ),
    "setup_script": (
        "set -e\n"
        "export DEBIAN_FRONTEND=noninteractive\n"
        "apt-get update -qq > /dev/null 2>&1\n"
        "apt-get install -y -qq nginx procps iproute2 > /dev/null 2>&1\n"
        "echo '<h1>SRE Agent Server</h1><p>Service restored.</p>' "
        "> /var/www/html/index.html\n"
        "service nginx start\n"
        "sleep 1\n"
        "pkill -9 nginx || true\n"
        "sleep 0.5\n"
        "echo '99999' > /run/nginx.pid\n"
    ),
},
"task_3_nginx_config": {
    "name": "Fix Broken Nginx Configuration",
    "difficulty": "hard",
    # "description": (
    #     "The nginx web server has a syntax error in its main configuration "
    #     "file (/etc/nginx/nginx.conf) that prevents it from starting. "
    #     "Diagnose the configuration error, fix it, start nginx, and verify "
    #     "it serves content on port 80.\n"
    #     "The expected web content is already placed in /var/www/html/index.html.\n"
    #     "IMPORTANT: This is a Docker container — use 'service nginx start' "
    #     "instead of 'systemctl'. You can validate the config with 'nginx -t'."
    # ),
    "description": (
        "The nginx web server has a syntax error in its main configuration "
        "file somewhere inside that prevents it from starting. "
        "Diagnose the configuration error, fix it, start nginx, and verify "
        "it serves content on port 80.\n"
        "The expected web content is already placed in /var/www/html/index.html.\n"
        "IMPORTANT: This is a Docker container — use 'service nginx start' "
        "instead of 'systemctl'. You can validate the config with 'nginx -t'."
    ),
    "setup_script": (
        "set -e\n"
        "export DEBIAN_FRONTEND=noninteractive\n"
        "apt-get update -qq > /dev/null 2>&1\n"
        "apt-get install -y -qq nginx curl procps iproute2 > /dev/null 2>&1\n"
        "echo '<h1>SRE Agent Fixed This!</h1>"
        "<p>Configuration repaired successfully.</p>' "
        "> /var/www/html/index.html\n"
        "# Break nginx config — remove the last closing brace\n"
        "sed -i '$ d' /etc/nginx/nginx.conf\n"
        "service nginx stop 2>/dev/null || true\n"
        "pkill nginx 2>/dev/null || true\n"
    ),
},
"task_4_port_conflict": {
    "name": "Resolve Port Conflict",
    "difficulty": "medium",
    "description": (
        "The Nginx web server refuses to start because Port 80 is already in use "
        "by another process. Identify the rogue process holding the port, "
        "terminate it, and then successfully start the nginx service.\n"
        "Use 'service nginx start' and verify it's listening on port 80."
    ),
    "setup_script": (
        "set -e\n"
        "export DEBIAN_FRONTEND=noninteractive\n"
        "apt-get update -qq > /dev/null 2>&1\n"
        "apt-get install -y -qq nginx net-tools procps > /dev/null 2>&1\n"
        "service nginx stop || true\n"
        "# Start a rogue python listener on port 80\n"
        "python3 -c 'import socket; s=socket.socket(); s.bind((\"0.0.0.0\", 80)); s.listen(1); import time; time.sleep(3600)' &\n"
        "sleep 1\n"
    ),
},
"task_5_disk_pressure": {
    "name": "Emergency Disk Clearance",
    "difficulty": "hard",
    "description": (
        "The system is reporting 'No space left on device' errors. "
        "A rogue log file has consumed the entire available disk space in /var/log. "
        "Find the oversized file, remove it, and restart the logging service (rsyslog)."
    ),
    "setup_script": (
        "set -e\n"
        "export DEBIAN_FRONTEND=noninteractive\n"
        "apt-get update -qq > /dev/null 2>&1\n"
        "apt-get install -y -qq rsyslog > /dev/null 2>&1\n"
        "mkdir -p /var/log/app/\n"
        "truncate -s 10M /var/log/app/debug.log.1\n"
        "chown -R syslog:adm /var/log/app\n"
        "service rsyslog start\n"
    ),
},
"task_6_dns_poisoning": {
    "name": "Fix Local Service Discovery",
    "difficulty": "hard",
    "description": (
        "The application is failing to connect to the internal database at 'db.local'. "
        "The database is verified as running on localhost:5432, but the app "
        "cannot resolve the address correctly. Fix the resolution issue."
    ),
    "setup_script": (
        "set -e\n"
        "export DEBIAN_FRONTEND=noninteractive\n"
        "apt-get update -qq > /dev/null 2>&1\n"
        "apt-get install -y -qq iputils-ping dnsutils > /dev/null 2>&1\n"
        "echo '10.255.255.255 db.local' >> /etc/hosts\n"
    ),
},
}


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

def _exec(container, cmd: str) -> str:
    """Run a command inside a Docker container and return stripped stdout."""
    try:
        result = container.exec_run(["/bin/bash", "-c", cmd])
        return result.output.decode("utf-8", errors="replace").strip()
    except Exception as e:
        logger.warning(f"Grader exec failed: {e}")
        return ""


# ---------------------------------------------------------------------------
#  Public grading entry-point
# ---------------------------------------------------------------------------

def grade_task(task_id: str, container) -> float:
    """
    Grade a task by inspecting the current state of the container.

    Returns a score between 0.0 and 1.0.
    """
    graders = {
        "task_1_permissions": _grade_permissions,
        "task_2_service": _grade_service,
        "task_3_nginx_config": _grade_nginx_config,
        "task_4_port_conflict": _grade_port_conflict,
        "task_5_disk_pressure": _grade_disk_pressure,
        "task_6_dns_poisoning": _grade_dns_poisoning,
    }
    grader = graders.get(task_id)
    if grader is None:
        logger.error(f"No grader for task: {task_id}")
        return 0.0
    try:
        return grader(container)
    except Exception as e:
        logger.error(f"Grader crash for {task_id}: {e}")
        return 0.0


# ---------------------------------------------------------------------------
#  Individual graders
# ---------------------------------------------------------------------------
def _grade_permissions(container) -> float:
    """
    Task 1 (Easy): Fix File Permissions.
    
    Checkpoints:
      - File exists and permissions are 644/755/664  -> 1.0
      - Permissions changed from 000 but not ideal  -> 0.5
    
    Penalties:
      - Leftover 'trash' files in /var/www/html      -> -0.2
      - Excessive commands (>10) for easy task      -> -0.1
    """
    score = 0.0
    # 1. Check current state
    raw = _exec(container, "stat -c '%a' /var/www/html/index.html 2>/dev/null || echo 'MISSING'")
    if raw == "MISSING": return 0.0

    perms = int(raw) if raw.isdigit() else 0
    if perms in (644, 755, 664):
        score = 1.0
    elif perms > 0:
        score = 0.5

    # --- PENALTIES ---
    # Penalty for leaving backup files (e.g., index.html.bak)
    extras = _exec(container, "ls /var/www/html/ | grep -v '^index.html$'")
    if extras:
        score -= 0.2
    
    # Penalty for being slow (more than 10 commands for an 'easy' task)
    history = _get_history(container).splitlines()
    if len(history) > 10:
        score -= 0.1

    return max(0.0, min(1.0, score))


def _grade_service(container) -> float:
    """
    Task 2 (Medium): Restart Crashed Web Server.
    
    Checkpoints:
      - Stale PID file handled (removed/valid)       -> +0.3
      - nginx master process running                 -> +0.3
      - Port 80 is listening                         -> +0.4
      
    Penalties:
      - Used 'kill -9' (Brute force)                 -> -0.1
      - Did not delete the specific '99999' PID file -> -0.2
    """
    score = 0.0

    # --- checkpoint 1: stale PID ------------------------------------------------
    pid_status = _exec(container, (
        "if [ -f /run/nginx.pid ]; then "
        "  pid=$(cat /run/nginx.pid 2>/dev/null); "
        "  if [ -n \"$pid\" ] && kill -0 \"$pid\" 2>/dev/null; then "
        "    echo VALID; "
        "  else "
        "    echo STALE; "
        "  fi; "
        "else "
        "  echo REMOVED; "
        "fi"
    ))
    if pid_status in ("VALID", "REMOVED"):
        score += 0.3

    # --- checkpoint 2: nginx process running ------------------------------------
    proc = _exec(
        container,
        "pgrep -x nginx > /dev/null 2>&1 && echo RUNNING || echo STOPPED",
    )
    if "RUNNING" in proc:
        score += 0.3

    # --- checkpoint 3: port 80 listening ----------------------------------------
    port = _exec(
        container,
        "ss -tlnp 2>/dev/null | grep -q ':80 ' && echo LISTENING || echo NO",
    )
    if "LISTENING" in port:
        score += 0.4

    pid_val = _exec(container, "cat /run/nginx.pid 2>/dev/null || echo ''")
    if pid_val == "99999":
        score -= 0.2

    # Penalty: Brute force usage of kill -9
    if "kill -9" in _get_history(container):
        score -= 0.1

    # return max(-1.0, round(score, 2))

    # return min(round(score, 2), 1.0)
    return max(0.0, min(1.0, round(score, 2)))


def _grade_nginx_config(container) -> float:
    """
    Task 3 (Hard): Fix Broken Nginx Configuration.
    
    Checkpoints:
      - nginx -t passes                               -> +0.4
      - nginx master process running                  -> +0.3
      - curl localhost:80 returns 200 + "SRE Agent"   -> +0.3
      
    Penalties:
      - Backup files left in /etc/nginx/ (.bak, .tmp) -> -0.15
      - Bloat: Installed editors (vim/nano)           -> -0.1
    """
    score = 0.0

    # --- checkpoint 1: valid config ---------------------------------------------
    cfg = _exec(container, "nginx -t 2>&1; echo EXIT_CODE=$?")
    if "EXIT_CODE=0" in cfg:
        score += 0.4

    # --- checkpoint 2: nginx running --------------------------------------------
    proc = _exec(
        container,
        "pgrep -x nginx > /dev/null 2>&1 && echo RUNNING || echo STOPPED",
    )
    if "RUNNING" in proc:
        score += 0.3

    # --- checkpoint 3: HTTP 200 + correct content -------------------------------
    http_code = _exec(
        container,
        "curl -s -o /dev/null -w '%{http_code}' http://localhost:80/ 2>/dev/null "
        "|| echo 000",
    )
    if http_code.strip() == "200":
        body = _exec(container, "curl -s http://localhost:80/ 2>/dev/null")
        if "SRE Agent" in body:
            score += 0.3

    config_backups = _exec(container, "ls /etc/nginx/ | grep -E '.bak|.tmp|.old'")
    if config_backups:
        score -= 0.15

    # Penalty: Installing unnecessary software (bloat)
    history = _get_history(container)
    if "apt install" in history and "nginx" not in history:
        score -= 0.1

    return max(0.0, min(1.0, round(score, 2)))


def _grade_port_conflict(container) -> float:
    """
    Task 4 (Medium): Resolve Port Conflict.

    Checkpoints:
      - Rogue Python process killed                  -> +0.4
      - Nginx is the listener on port 80             -> +0.6
    """
    score = 0.0

    # Checkpoint 1: Did they kill the rogue Python process? (+0.4)
    rogue_proc = _exec(container, "pgrep -f 'python3 -c import socket'")
    if not rogue_proc:
        score += 0.4

    # Checkpoint 2: Is Nginx now the one holding Port 80? (+0.6)
    port_owner = _exec(container, "netstat -tulpn | grep :80 | grep nginx || echo 'NONE'")
    if "nginx" in port_owner:
        score += 0.6

    return max(0.0, min(1.0, round(score, 2)))


def _grade_disk_pressure(container) -> float:
    """
    Task 5 (Hard): Emergency Disk Clearance.

    Checkpoints:
      - The 10MB rogue file is gone                  -> +0.5
      - rsyslog service is running                   -> +0.5

    Penalties:
      - Deleted entire /var/log/app directory         -> -0.4
    """
    score = 0.0

    # Checkpoint 1: Is the 10MB file gone? (+0.5)
    file_check = _exec(container, "[ -f /var/log/app/debug.log.1 ] && echo EXISTS || echo GONE")
    if file_check == "GONE":
        score += 0.5

    # Checkpoint 2: Is rsyslog service running? (+0.5)
    service_status = _exec(container, "service rsyslog status | grep 'running' || echo 'DOWN'")
    if "running" in service_status:
        score += 0.5

    # Penalty: Deleting the entire /var/log/app directory instead of the file (-0.4)
    dir_check = _exec(container, "[ -d /var/log/app ] && echo OK || echo DELETED")
    if dir_check == "DELETED":
        score -= 0.4

    return max(0.0, min(1.0, round(score, 2)))


def _grade_dns_poisoning(container) -> float:
    """
    Task 6 (Hard): Fix Local Service Discovery.

    Checkpoints:
      - db.local resolves to 127.0.0.1 / ::1         -> 1.0
      - Bad IP removed but not pointed to localhost   -> 0.4

    Penalties:
      - More than 5 commands for a single file edit   -> -0.2
    """
    score = 0.0

    # Checkpoint 1: Does db.local resolve to 127.0.0.1 or localhost? (+1.0)
    resolution = _exec(container, "getent hosts db.local")
    if "127.0.0.1" in resolution or "::1" in resolution:
        score = 1.0
    # Partial Reward: Bad IP removed but not pointed to localhost (+0.4)
    elif "10.255.255.255" not in _exec(container, "cat /etc/hosts"):
        score = 0.4

    # Penalty: Using more than 5 commands for a single file edit (-0.2)
    history = _get_history(container).splitlines()
    if len(history) > 5:
        score -= 0.2

    return max(0.0, min(1.0, round(score, 2)))
