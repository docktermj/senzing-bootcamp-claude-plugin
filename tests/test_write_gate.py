"""Tests for the PreToolUse write-gate security control.

`plugins/senzing-bootcamp/scripts/write-gate.py` reads stdin at import time, so it
cannot be imported directly — each case runs it as a subprocess with synthetic
stdin and a temp project directory (holding `config/bootcamp_progress.json`, which
is what activates the gate), then asserts the exit code (0 allow, 2 block).

These tests live OUTSIDE `plugins/` on purpose: `propagate.sh` mirrors all of
`plugins/` into the public repo, so tests placed there would ship to bootcampers.

Run:  python3 -m unittest discover -s tests
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp", "scripts", "write-gate.py")

ALLOW, BLOCK = 0, 2


def run_gate(file_path=None, content="hello", cwd=None, activate=True,
             raw=None, env=None):
    """Invoke write-gate.py; return (exit_code, stderr)."""
    proj = cwd or tempfile.mkdtemp()
    if activate:
        os.makedirs(os.path.join(proj, "config"), exist_ok=True)
        with open(os.path.join(proj, "config", "bootcamp_progress.json"), "w") as fh:
            fh.write("{}")
    if raw is not None:
        payload = raw
    else:
        payload = json.dumps({"tool_input": {"file_path": file_path, "content": content}})
    run_env = dict(os.environ)
    if env:
        run_env.update(env)
    proc = subprocess.run([sys.executable, GATE], input=payload, cwd=proj,
                          capture_output=True, text=True, env=run_env)
    return proc.returncode, proc.stderr


class LocationChecks(unittest.TestCase):
    def test_project_relative_allowed(self):
        self.assertEqual(run_gate("config/prefs.yaml")[0], ALLOW)

    def test_absolute_in_project_allowed(self):
        proj = tempfile.mkdtemp()
        self.assertEqual(run_gate(os.path.join(proj, "config/x.yaml"), cwd=proj)[0], ALLOW)

    def test_system_tmp_blocked(self):
        self.assertEqual(run_gate("/tmp/scratch.txt")[0], BLOCK)
        self.assertEqual(run_gate("/var/tmp/scratch.txt")[0], BLOCK)

    def test_downloads_blocked(self):
        self.assertEqual(run_gate("/home/someone/Downloads/out.txt")[0], BLOCK)

    def test_windows_temp_env_blocked(self):
        self.assertEqual(run_gate(r"%TEMP%\out.txt")[0], BLOCK)
        self.assertEqual(run_gate(r"%Tmp%\out.txt")[0], BLOCK)  # case-insensitive

    def test_tmpdir_env_blocked(self):
        tmp = tempfile.mkdtemp()
        rc, _ = run_gate(os.path.join(tmp, "x.txt"), env={"TMPDIR": tmp})
        self.assertEqual(rc, BLOCK)

    def test_dotdot_escape_blocked(self):
        # config/../../etc/x resolves outside the project -> blocked as /etc is not
        # exempt and (when it lands in /tmp via cwd) as temp; use an explicit escape.
        proj = tempfile.mkdtemp()
        rc, _ = run_gate(os.path.join(proj, "config/../../..") + "/tmp/evil.txt", cwd=proj)
        self.assertEqual(rc, BLOCK)

    def test_project_under_tmp_path_allowed(self):
        # PreToolUseWriteError: a project living under a /tmp/-containing path must
        # not trip the gate for its own in-project writes.
        proj = tempfile.mkdtemp()  # e.g. /tmp/tmpXXXX
        self.assertEqual(run_gate(os.path.join(proj, "config/x.yaml"), cwd=proj)[0], ALLOW)

    def test_home_relative_downloads_blocked(self):
        self.assertEqual(run_gate("~/Downloads/out.txt")[0], BLOCK)

    def test_home_relative_windows_temp_blocked(self):
        self.assertEqual(run_gate("~/AppData/Local/Temp/x")[0], BLOCK)

    def test_home_personal_tmp_allowed(self):
        # ~/tmp is a personal dir named tmp, NOT system temp -> allowed.
        self.assertEqual(run_gate("~/tmp/scratch.txt")[0], ALLOW)

    def test_case_variant_in_project_allowed(self):
        proj = tempfile.mkdtemp()
        self.assertEqual(run_gate(proj.upper() + "/config/x.yaml", cwd=proj)[0], ALLOW)


class SecretChecks(unittest.TestCase):
    def test_pem_private_key_blocked(self):
        self.assertEqual(
            run_gate("config/k.pem", content="-----BEGIN RSA PRIVATE KEY-----\nabc")[0],
            BLOCK)

    def test_aws_key_blocked(self):
        self.assertEqual(run_gate("config/creds", content="AKIA" + "A" * 16)[0], BLOCK)

    def test_senzing_license_blob_blocked(self):
        self.assertEqual(
            run_gate("config/lic.txt", content="AQAAAD" + "abc123XYZ+/=" * 4)[0], BLOCK)

    def test_lic_path_without_key_allowed(self):
        self.assertEqual(
            run_gate("licenses/g2.lic", content="see the Senzing license portal")[0], ALLOW)

    def test_bare_aqaaad_word_allowed(self):
        self.assertEqual(
            run_gate("config/notes.md", content="mentions the AQAAAD prefix in prose")[0],
            ALLOW)


class GateActivation(unittest.TestCase):
    def test_disabled_without_progress_file(self):
        self.assertEqual(run_gate("/tmp/x", activate=False)[0], ALLOW)

    def test_fail_open_on_unparseable_payload(self):
        self.assertEqual(run_gate(raw="not json at all")[0], ALLOW)

    def test_secret_still_checked_even_with_bad_json(self):
        # Field-regex fallback still catches secrets when JSON parsing fails.
        rc, _ = run_gate(raw='garbage "file_path":"config/x" -----BEGIN PRIVATE KEY-----')
        self.assertEqual(rc, BLOCK)


if __name__ == "__main__":
    unittest.main()
