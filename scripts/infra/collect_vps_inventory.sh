#!/usr/bin/env bash
# NLE-INFRA-WO-001: strictly read-only VPS inventory.
# No installation, service changes, network probes, credential reads, or file writes.
set -u

section() { printf '\n## %s\n' "$1"; }

run() {
  local label="$1"; shift
  section "$label"
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'NOT_AVAILABLE\n'
    return 0
  fi
  "$@" 2>&1
  local rc=$?
  if [ "$rc" -ne 0 ]; then
    printf 'COMMAND_EXIT=%s\n' "$rc"
  fi
  return 0
}

os_release() {
  if [ -r /etc/os-release ]; then
    awk -F= '/^(ID|VERSION_ID|PRETTY_NAME)=/ {gsub(/^"|"$/, "", $2); print $1 "=" $2}' /etc/os-release
  else
    printf 'NOT_AVAILABLE\n'
  fi
}

cpu_summary() {
  if command -v lscpu >/dev/null 2>&1; then
    lscpu | awk -F: '/^(Architecture|CPU\(s\)|Model name|Socket\(s\)|Core\(s\) per socket|Thread\(s\) per core|Virtualization):/ {gsub(/^[ \t]+/, "", $2); print $1 "=" $2}'
  else
    printf 'NOT_AVAILABLE\n'
  fi
}

memory_summary() {
  if command -v free >/dev/null 2>&1; then free -h; else printf 'free: NOT_AVAILABLE\n'; fi
  if command -v swapon >/dev/null 2>&1; then
    printf '\nSwap devices (no secrets):\n'
    swapon --show --noheadings --bytes 2>&1 || true
  else
    printf '\nswapon: NOT_AVAILABLE\n'
  fi
}

storage_summary() {
  if command -v df >/dev/null 2>&1; then
    printf 'Filesystem capacity:\n'
    df -hT -x tmpfs -x devtmpfs 2>&1 || true
    printf '\nFilesystem inodes:\n'
    df -i -x tmpfs -x devtmpfs 2>&1 || true
  else
    printf 'df: NOT_AVAILABLE\n'
  fi
  if command -v lsblk >/dev/null 2>&1; then
    printf '\nBlock devices (no serial numbers):\n'
    lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS,ROTA 2>&1 || true
  else
    printf '\nlsblk: NOT_AVAILABLE\n'
  fi
}

docker_versions() {
  if command -v docker >/dev/null 2>&1; then
    docker version --format 'client={{.Client.Version}} server={{.Server.Version}}' 2>&1 || true
    docker compose version --short 2>&1 || true
  else
    printf 'NOT_AVAILABLE\n'
  fi
}

docker_containers() {
  if command -v docker >/dev/null 2>&1; then
    docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>&1 \
      | sed -E 's/([0-9]{1,3}\.){3}[0-9]{1,3}:/[IPv4]:/g; s/\[[0-9a-fA-F:]+\]:/[IPv6]:/g'
  else
    printf 'NOT_AVAILABLE\n'
  fi
}

docker_usage() {
  if command -v docker >/dev/null 2>&1; then
    docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}' 2>&1 || true
  else
    printf 'NOT_AVAILABLE\n'
  fi
}

listening_ports() {
  if command -v ss >/dev/null 2>&1; then
    ss -H -lnt 2>&1 | awk '{
      addr=$4; n=split(addr, parts, ":"); port=parts[n];
      if (addr ~ /^\*:/ || addr ~ /^0\.0\.0\.0:/ || addr ~ /^\[::\]:/) scope="WILDCARD";
      else if (addr ~ /^127\./ || addr ~ /^\[::1\]:/) scope="LOOPBACK";
      else scope="INTERFACE";
      print scope ":" port;
    }' | sort -u
  else
    printf 'NOT_AVAILABLE\n'
  fi
}

firewall_summary() {
  if command -v ufw >/dev/null 2>&1; then ufw status verbose 2>&1; else printf 'ufw: NOT_AVAILABLE (other firewall layers require separate read-back)\n'; fi
}

wireguard_summary() {
  if command -v wg >/dev/null 2>&1; then
    wg show interfaces 2>&1
  else
    printf 'NOT_AVAILABLE\n'
  fi
}

service_summary() {
  if command -v systemctl >/dev/null 2>&1; then
    printf 'docker='
    systemctl is-active docker 2>&1 || true
    printf 'containerd='
    systemctl is-active containerd 2>&1 || true
  else
    printf 'systemctl: NOT_AVAILABLE\n'
  fi
}

printf 'NLE-INFRA-WO-001 | VPS INVENTORY | READ_ONLY\n'
printf 'Collected UTC: '
date -u +'%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || printf 'UNKNOWN\n'
printf 'No files are created or modified by this collector.\n'
printf 'No environment variables, secret files, process arguments, credentials, or logs are read.\n'

run 'Kernel and architecture' uname -a
run 'Operating system' os_release
run 'GNU libc' getconf GNU_LIBC_VERSION
run 'CPU' cpu_summary
run 'Memory and swap' memory_summary
run 'Disk capacity, inodes and block devices' storage_summary
run 'Uptime' uptime
run 'Docker and Compose versions' docker_versions
run 'Running containers (addresses redacted; no inspect/env)' docker_containers
run 'Container resource usage' docker_usage
run 'Listening TCP ports (IP addresses omitted)' listening_ports
run 'Firewall status (UFW only; OCI rules not queried)' firewall_summary
run 'WireGuard interface names only' wireguard_summary
run 'Relevant service state' service_summary
run 'Network interface names only' ip -brief link
run 'OCI CLI presence only (no API call)' bash -c 'if command -v oci >/dev/null 2>&1; then echo PRESENT_NOT_QUERIED; else echo NOT_AVAILABLE; fi'

printf '\nEND NLE-INFRA-WO-001 | READ_ONLY | NO_CONFIGURATION_CHANGED\n'
