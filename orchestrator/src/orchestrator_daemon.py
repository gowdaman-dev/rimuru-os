#!/usr/bin/env python3
"""
Rimuru OS — Orchestrator Daemon (rimuru-orchestratord)
The Kernel-Adjacent Multi-Agent Parallel Task Scheduler & Syscall Harness
"""

import os
import sys
import json
import time
import uuid
import socket
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor

SOCKET_PATH = "/tmp/rimuru_orchestrator.sock"
MAX_WORKERS = 4


class SyscallHarness:
    """Provides sandboxed, snapshot-aware operating system calls for agents."""

    @staticmethod
    def syscall_shell(command, timeout=60, sandboxed=True):
        """Executes a command inside Bubblewrap sandbox or isolated subshell."""
        if sandboxed and subprocess.run(["which", "bwrap"], capture_output=True).returncode == 0:
            # Bubblewrap containment
            cmd = [
                "bwrap",
                "--ro-bind", "/usr", "/usr",
                "--ro-bind", "/lib", "/lib",
                "--ro-bind", "/lib64", "/lib64",
                "--ro-bind", "/bin", "/bin",
                "--ro-bind", "/etc", "/etc",
                "--bind", "/tmp", "/tmp",
                "--bind", os.getcwd(), os.getcwd(),
                "--dev", "/dev",
                "--proc", "/proc",
                "--unshare-pid",
                "--die-with-parent",
                "bash", "-c", command
            ]
        else:
            cmd = ["bash", "-c", command]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return {"exit_code": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            return {"exit_code": -1, "stdout": "", "stderr": "Command timed out."}
        except Exception as e:
            return {"exit_code": -1, "stdout": "", "stderr": str(e)}

    @staticmethod
    def syscall_snapshot(label):
        """Creates an atomic system snapshot via Snapper prior to mutating state."""
        try:
            res = subprocess.run(["rimuru-snapshot", "create", label], capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False

    @staticmethod
    def syscall_hyprland(command):
        """Sends commands to the Hyprland Wayland compositor."""
        try:
            res = subprocess.run(["hyprctl", "dispatch", command], capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False


class TaskNode:
    """A single sub-problem node in the execution DAG."""

    def __init__(self, node_id, goal, dependencies=None):
        self.node_id = node_id
        self.goal = goal
        self.dependencies = dependencies or []
        self.status = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
        self.result = None
        self.started_at = None
        self.completed_at = None

    def to_dict(self):
        return {
            "id": self.node_id,
            "goal": self.goal,
            "status": self.status,
            "dependencies": self.dependencies,
            "result": self.result,
        }


class RimuruOrchestrator:
    """The central orchestrator managing parallel agents and task graphs."""

    def __init__(self):
        self.tasks = {}
        self.pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.lock = threading.Lock()

    def decompose_goal(self, high_level_goal):
        """Deconstructs high-level goal into a parallel DAG of sub-tasks."""
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        nodes = []

        # Built-in heuristic decomposition (extensible with local Ollama or cloud model)
        nodes.append(TaskNode(f"{plan_id}_1", f"Inspect system & environment for: '{high_level_goal}'"))
        nodes.append(TaskNode(f"{plan_id}_2", f"Prepare dependencies and sandboxed workspace", dependencies=[f"{plan_id}_1"]))
        nodes.append(TaskNode(f"{plan_id}_3", f"Execute core implementation for: '{high_level_goal}'", dependencies=[f"{plan_id}_2"]))
        nodes.append(TaskNode(f"{plan_id}_4", f"Verify artifacts and validate execution state", dependencies=[f"{plan_id}_3"]))

        with self.lock:
            self.tasks[plan_id] = {
                "id": plan_id,
                "goal": high_level_goal,
                "nodes": {n.node_id: n for n in nodes},
                "status": "RUNNING",
                "created_at": time.time(),
            }

        # Submit ready nodes to the threadpool
        self._schedule_ready_nodes(plan_id)
        return plan_id

    def _schedule_ready_nodes(self, plan_id):
        with self.lock:
            plan = self.tasks.get(plan_id)
            if not plan:
                return

            completed_ids = {nid for nid, node in plan["nodes"].items() if node.status == "COMPLETED"}

            for nid, node in plan["nodes"].items():
                if node.status == "PENDING":
                    # Check if all dependencies are satisfied
                    if all(dep in completed_ids for dep in node.dependencies):
                        node.status = "RUNNING"
                        node.started_at = time.time()
                        self.pool.submit(self._worker_execute, plan_id, node)

    def _worker_execute(self, plan_id, node):
        print(f"[Orchestrator Worker] Executing node {node.node_id}: {node.goal}")
        # Run sub-task using Syscall Harness
        time.sleep(1.0)  # Simulated execution slice
        result = SyscallHarness.syscall_shell("uname -r && echo 'Sub-task completed successfully'")

        with self.lock:
            node.status = "COMPLETED"
            node.result = result.get("stdout", "").strip()
            node.completed_at = time.time()

        # Check if new nodes are now unblocked
        self._schedule_ready_nodes(plan_id)

    def get_status(self):
        with self.lock:
            return {
                "active_plans": len(self.tasks),
                "plans": {
                    pid: {
                        "goal": p["goal"],
                        "status": p["status"],
                        "nodes": [n.to_dict() for n in p["nodes"].values()],
                    }
                    for pid, p in self.tasks.items()
                },
            }


def run_socket_server(orchestrator):
    if os.path.exists(SOCKET_PATH):
        try:
            os.remove(SOCKET_PATH)
        except OSError:
            pass

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(10)
    print(f"[rimuru-orchestratord] Listening on {SOCKET_PATH}...")

    while True:
        conn, _ = server.accept()
        try:
            data = conn.recv(4096)
            if not data:
                conn.close()
                continue
            req = json.loads(data.decode("utf-8"))
            action = req.get("action")

            if action == "dispatch":
                goal = req.get("goal", "")
                plan_id = orchestrator.decompose_goal(goal)
                conn.sendall(json.dumps({"status": "ok", "plan_id": plan_id}).encode("utf-8"))
            elif action == "status":
                status = orchestrator.get_status()
                conn.sendall(json.dumps({"status": "ok", "data": status}).encode("utf-8"))
            else:
                conn.sendall(json.dumps({"status": "error", "message": "Unknown action"}).encode("utf-8"))
        except Exception as e:
            conn.sendall(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
        finally:
            conn.close()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--dispatch":
        # Client mode: send goal to running daemon or local test
        goal = " ".join(sys.argv[2:])
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(SOCKET_PATH)
            client.sendall(json.dumps({"action": "dispatch", "goal": goal}).encode("utf-8"))
            resp = json.loads(client.recv(4096).decode("utf-8"))
            print(f"[rimuru] Orchestrator response: {resp}")
        except FileNotFoundError:
            print("[rimuru] Daemon is starting in background...")
        return

    orchestrator = RimuruOrchestrator()
    print("[rimuru-orchestratord] Initializing OS Orchestrator Engine...")
    run_socket_server(orchestrator)


if __name__ == "__main__":
    main()
