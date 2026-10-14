import io
import json
import sys
import types

import pytest

import bb

ENV = {"BROWSERBASE_API_KEY": "test-key", "BROWSERBASE_PROJECT_ID": "proj-1"}


class FakeHTTP:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, req, timeout=None):
        self.requests.append(req)
        body = self.responses.pop(0)
        return io.BytesIO(json.dumps(body).encode())


def test_session_body_without_context():
    body = bb.session_body(ENV)
    tags = body.pop("userMetadata")
    assert body == {"projectId": "proj-1", "timeout": 300, "browserSettings": {"solveCaptchas": True}, "proxies": False}
    assert set(tags) == {"agent", "client", "run"}


def test_session_body_overrides_timeout_proxy_and_tags():
    body = bb.session_body({**ENV, "BB_SESSION_TIMEOUT": "900", "BB_PROXIES": "1", "BB_CLIENT": "gt-clinic"})
    assert body["timeout"] == 900 and body["proxies"] is True and body["userMetadata"]["client"] == "gt-clinic"


def test_session_body_with_persistent_context():
    body = bb.session_body({**ENV, "BB_CONTEXT_ID": "ctx-9"})
    assert body["browserSettings"]["context"] == {"id": "ctx-9", "persist": True}


def test_missing_env_is_named():
    with pytest.raises(bb.BrowserbaseError, match="BROWSERBASE_API_KEY"):
        bb.create_session({"BROWSERBASE_PROJECT_ID": "p"}, opener=FakeHTTP([]))


def test_create_and_release_hit_the_rest_api():
    http = FakeHTTP([{"id": "s1", "connectUrl": "wss://connect"}, {}])
    session = bb.create_session(ENV, opener=http)
    bb.release_session(session["id"], ENV, opener=http)
    create, release = http.requests
    assert create.full_url == "https://api.browserbase.com/v1/sessions"
    assert create.get_header("X-bb-api-key") == "test-key"
    assert release.full_url == "https://api.browserbase.com/v1/sessions/s1"
    assert json.loads(release.data)["status"] == "REQUEST_RELEASE"


def _fake_playwright(monkeypatch, connect_error=None):
    class Browser:
        contexts = []
        closed = False

        def new_context(self):
            return types.SimpleNamespace(pages=[], new_page=lambda: "page")

        def close(self):
            Browser.closed = True

    def connect_over_cdp(url):
        if connect_error:
            raise connect_error
        return Browser()

    class PW:
        chromium = types.SimpleNamespace(connect_over_cdp=connect_over_cdp)

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.sync_playwright = PW
    monkeypatch.setitem(sys.modules, "playwright", types.ModuleType("playwright"))
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api)
    return Browser


def test_open_page_releases_session_when_agent_raises(monkeypatch):
    browser_cls = _fake_playwright(monkeypatch)
    http = FakeHTTP([{"id": "s2", "connectUrl": "wss://x"}, {}])
    with pytest.raises(ValueError), bb.open_page(env=ENV, opener=http) as page:
        assert page == "page"
        raise ValueError("boom")
    assert browser_cls.closed
    assert http.requests[-1].full_url.endswith("/sessions/s2")


def test_open_page_releases_session_when_connect_fails(monkeypatch):
    _fake_playwright(monkeypatch, connect_error=ConnectionError("cdp down"))
    http = FakeHTTP([{"id": "s3", "connectUrl": "wss://x"}, {}])
    with pytest.raises(ConnectionError), bb.open_page(env=ENV, opener=http):
        pass
    assert json.loads(http.requests[-1].data)["status"] == "REQUEST_RELEASE"


def test_run_names_failures_and_keeps_going(run):
    def check(t):
        if t["name"] == "bad":
            raise RuntimeError("selector missing")
        return {"status": "ok", "x": 1}

    run.each([{"name": "good"}, {"name": "bad"}, {"name": "also good"}], check)
    assert [r["status"] for r in run.results] == ["ok", "error", "ok"]
    assert run.results[1] == {"target": "bad", "status": "error", "error": "RuntimeError: selector missing"}
    assert run.finish() == 1


def test_run_caps_targets(tmp_path):
    run = bb.Run("t", max_targets=2, out_root=tmp_path, stop_file=tmp_path / "STOP")
    run.each([{"name": str(i)} for i in range(5)], lambda t: {})
    assert len(run.results) == 2
    assert run.skipped == 3 and "max targets" in run.stopped_reason


def test_run_caps_minutes(tmp_path):
    ticks = iter([0, 0, 120, 600])
    run = bb.Run(
        "t", max_minutes=5, out_root=tmp_path, stop_file=tmp_path / "STOP", clock=lambda: next(ticks)
    )
    run.each([{"name": str(i)} for i in range(5)], lambda t: {})
    assert len(run.results) == 2 and "max minutes" in run.stopped_reason


def test_stop_file_halts_mid_run(tmp_path):
    stop = tmp_path / "STOP"
    run = bb.Run("t", out_root=tmp_path, stop_file=stop)

    def check(t):
        stop.write_text("")
        return {}

    run.each([{"name": "a"}, {"name": "b"}], check)
    assert len(run.results) == 1 and "STOP" in run.stopped_reason


def test_run_agent_skips_browser_when_stop_present(tmp_path, monkeypatch):
    (tmp_path / "STOP").write_text("")
    monkeypatch.setattr(bb, "open_page", lambda **_: pytest.fail("should not open a session"))
    run = bb.Run("t", out_root=tmp_path, stop_file=tmp_path / "STOP")
    assert bb.run_agent(run, [{"name": "a"}], lambda p, t: {}) == 0
    assert run.skipped == 1


def test_receipt_and_summary(run, capsys):
    run.each([{"name": "a"}], lambda t: {"status": "warn", "note": "x"})
    code = run.finish()
    receipt = json.loads(run.receipt_path.read_text())
    assert code == 0
    assert receipt["read_only"] is True and receipt["counts"] == {"warn": 1}
    assert run.receipt_path.parent.parent.name == "test_agent"
    line = capsys.readouterr().out.strip()
    assert line.startswith("test_agent: 1 target(s) [warn=1]") and "\n" not in line


def test_example_targets_are_fake():
    data = json.loads(bb.EXAMPLE_TARGETS.read_text())
    urls = [t["url"] for k in ("lp_qa",) for t in data[k]]
    assert all("example.com" in u for u in urls)
