import csv
import json

from conftest import FakePage, fixture

import ad_ui_check
import gbp_watch
import lead_enrich
import listing_audit
import lp_qa

# --- ad_ui_check ------------------------------------------------------------


def test_ad_ui_detects_login_and_stops_target(run):
    page = FakePage(
        {"https://ads.google.com/aw/overview": fixture("google_login.html")},
        redirects={"https://ads.google.com/aw/overview": "https://accounts.google.com/v3/signin/identifier"},
    )
    res = ad_ui_check.check_target(page, {"name": "G", "url": "https://ads.google.com/aw/overview"}, run)
    assert res["status"] == "needs_login"
    assert "policy" not in res
    assert page.visited == ["https://ads.google.com/aw/overview"]


def test_ad_ui_login_detected_from_text_alone():
    text = "Sign in\nto continue to Google Ads\nEmail or phone"
    assert ad_ui_check.is_login_page("https://ads.google.com/aw/overview", text)


def test_ad_ui_extracts_policy_billing_and_status(run):
    url = "https://ads.google.com/aw/overview"
    page = FakePage({url: fixture("ads_overview.html")})
    res = ad_ui_check.check_target(page, {"name": "G", "url": url, "platform": "google_ads"}, run)
    assert res["status"] == "warn"
    assert any("Disapproved" in ln for ln in res["policy"])
    assert any("Limited by policy" in ln for ln in res["policy"])
    assert any("payment was declined" in ln for ln in res["billing"])
    assert "suspended" in res["account_status"].lower()
    assert (run.out_dir / res["screenshot"]).exists()


def test_ad_ui_clean_account_is_ok():
    sig = ad_ui_check.extract_signals("Overview\nCampaigns\nAccount status: Active\nAll ads eligible")
    assert sig == {"policy": [], "billing": [], "account_status": "Account status: Active"}


# --- gbp_watch --------------------------------------------------------------


def _panel_page():
    return FakePage({"https://www.google.com/search*": fixture("gbp_panel.html")})


def test_gbp_parses_panel():
    page = _panel_page()
    page.goto("https://www.google.com/search?q=x")
    data = gbp_watch.parse_panel(page.content(), page.inner_text("body"))
    assert data["rating"] == 4.6 and data["review_count"] == 1234
    assert data["phone"] == "(555) 010-0100"
    assert data["website"] == "https://example.com/"
    assert data["address"].startswith("123 Main St")
    assert data["hours"]["monday"] == "7 AM–6 PM" and data["hours"]["sunday"] == "Closed"
    assert data["suggest_an_edit"] and data["claim_prompt"] and data["panel_found"]


def test_gbp_review_count_with_k_suffix():
    data = gbp_watch.parse_panel("", "Example\n4.8 ★★★★★ 2.1K Google reviews")
    assert data["rating"] == 4.8 and data["review_count"] == 2100


def test_gbp_diffs_against_previous_receipt(run, tmp_path):
    target = {"name": "Example Bakery", "city": "Springfield, IL"}
    first = gbp_watch.check_target(_panel_page(), target, run, previous={})
    assert first["status"] == "ok" and first["first_run"]

    old = dict(first, review_count=1200, phone="(555) 010-0999")
    prior_dir = run.out_root / gbp_watch.AGENT / "2000-01-01"
    prior_dir.mkdir(parents=True)
    (prior_dir / "receipt-000000.json").write_text(
        json.dumps({"results": [{"target": "Example Bakery", **old}]})
    )
    previous = gbp_watch.latest_previous(run.out_root, tmp_path / "current.json")
    second = gbp_watch.check_target(_panel_page(), target, run, previous)
    assert second["status"] == "changed"
    changed = {c["field"]: (c["before"], c["after"]) for c in second["changes"]}
    assert changed == {"review_count": (1200, 1234), "phone": ("(555) 010-0999", "(555) 010-0100")}


def test_gbp_no_panel_is_warn(run):
    page = FakePage({"https://www.google.com/search*": "<html><body>No results</body></html>"})
    res = gbp_watch.check_target(page, {"name": "Nobody", "city": "Nowhere"}, run, {})
    assert res["status"] == "warn" and not res["panel_found"]


# --- lp_qa ------------------------------------------------------------------


def test_lp_qa_passes_good_page(run):
    url = "https://example.com/landing"
    page = FakePage(
        {url: fixture("landing.html")},
        metrics={"overflow_px": 0, "small_tap_targets": 0, "broken_images": []},
    )
    res = lp_qa.check_target(page, {"name": "LP", "url": url}, run, lp_qa.Collector())
    assert res["status"] == "ok", res["failed"]
    assert [v["width"] for v in page.viewports] == [390, 768, 1440]
    assert len(res["screenshots"]) == 3
    assert "tap_targets_44px" not in res["widths"][1440]
    assert res["checks"]["tel_link"]["detail"] == "tel:+15550100100"


def test_lp_qa_flags_every_problem(run):
    url = "https://example.com/bad"
    metrics = {
        390: {
            "overflow_px": 37,
            "small_tap_targets": 2,
            "small_samples": [{"tag": "a", "w": 20, "h": 18}],
            "broken_images": ["/x.png"],
        },
        768: {"overflow_px": 0, "small_tap_targets": 0, "broken_images": []},
        1440: {"overflow_px": 0, "small_tap_targets": 9, "broken_images": []},
    }
    page = FakePage({url: (500, fixture("landing_bad.html"))}, metrics=lambda w: metrics[w])
    collector = lp_qa.Collector()
    collector.console_errors.append("stale")  # reset per width must clear this
    res = lp_qa.check_target(page, {"name": "Bad", "url": url}, run, collector)
    assert res["status"] == "fail"
    for name in (
        "http_status",
        "broken_images",
        "title",
        "meta_description",
        "form_present",
        "tel_link",
        "no_horizontal_overflow@390",
        "tap_targets_44px@390",
    ):
        assert name in res["failed"], name
    assert "console_errors" not in res["failed"]
    assert "mailto_link" not in res["failed"]  # advisory only
    assert res["checks"]["mailto_link"]["pass"] is False


def test_lp_qa_collector_records_console_and_image_failures():
    c = lp_qa.Collector()
    page = FakePage({})
    c.attach(page)
    msg = type("M", (), {"type": "error", "text": "Uncaught TypeError"})()
    resp = type(
        "R",
        (),
        {
            "status": 404,
            "url": "https://example.com/a.png",
            "request": type("Q", (), {"resource_type": "image"})(),
        },
    )()
    favicon = type("M", (), {"type": "error", "text": "404", "location": {"url": "http://x/favicon.ico"}})()
    page.handlers["console"][0](msg)
    page.handlers["console"][0](favicon)
    page.handlers["response"][0](resp)
    assert c.console_errors == ["Uncaught TypeError"]
    assert c.failed_images == ["https://example.com/a.png"]


# --- lead_enrich ------------------------------------------------------------


class NoSleep:
    def __init__(self):
        self.t, self.slept = 0.0, []

    def clock(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def _robots(rules: dict):
    return lead_enrich.Robots(fetch=lambda url: rules.get(url, (404, "")))


def test_pick_website_skips_directories():
    site = lead_enrich.pick_website(fixture("ddg_results.html"))
    assert site == "https://example-plumbing.example.com/"


def test_directory_matching_uses_whole_labels():
    assert lead_enrich.is_directory("https://m.yelp.com/biz/x")
    assert lead_enrich.is_directory("https://x.com/someone")
    assert not lead_enrich.is_directory("https://example-plumbing.com/")
    assert not lead_enrich.is_directory("https://box.com/")


def test_extract_contacts_from_home_and_contact():
    home = fixture("biz_home.html")
    found = lead_enrich.extract_contacts(home, "", "https://example-plumbing.example.com/")
    assert found["phones"] == ["(555) 010-0100"]
    assert found["emails"] == []  # wixpress / image names are filtered
    assert found["socials"]["facebook"].startswith("https://www.facebook.com/")
    assert found["socials"]["x"] == "https://twitter.com/exampleplumb"
    assert found["contact_page"] == "https://example-plumbing.example.com/contact-us"


def test_robots_rules():
    robots = _robots(
        {
            "https://a.example/robots.txt": (200, "User-agent: *\nDisallow: /private"),
            "https://down.example/robots.txt": (503, ""),
        }
    )
    assert robots.allowed("https://a.example/")
    assert not robots.allowed("https://a.example/private/x")
    assert robots.allowed("https://missing.example/anything")  # 404 robots = allowed
    assert not robots.allowed("https://down.example/")  # 5xx = treat as disallowed


def test_rate_limiter_spaces_hits_per_host():
    t = NoSleep()
    rl = lead_enrich.RateLimiter(3.0, clock=t.clock, sleep=t.sleep)
    rl.wait("https://a.example/1")
    rl.wait("https://b.example/1")
    rl.wait("https://a.example/2")
    assert t.slept == [3.0]


def test_enricher_end_to_end(run):
    site = "https://example-plumbing.example.com/"
    page = FakePage(
        {
            "https://html.duckduckgo.com/html/*": fixture("ddg_results.html"),
            site: fixture("biz_home.html"),
            site + "contact-us": fixture("biz_contact.html"),
        }
    )
    t = NoSleep()
    enrich = lead_enrich.Enricher(page, run, _robots({}), lead_enrich.RateLimiter(0, t.clock, t.sleep))
    res = enrich({"business_name": "Example Plumbing", "city": "Riverton, WY", "website": ""})
    assert res["status"] == "ok"
    assert res["website"] == site and res["website_source"] == "search"
    assert res["phone"] == "(555) 010-0100"
    assert res["email"] == "office@example-plumbing.example.com"
    assert res["linkedin"].startswith("https://www.linkedin.com/")


def test_enricher_respects_robots(run):
    site = "https://blocked.example/"
    page = FakePage({site: "<html></html>"})
    robots = _robots({site + "robots.txt": (200, "User-agent: *\nDisallow: /")})
    res = lead_enrich.Enricher(page, run, robots, lead_enrich.RateLimiter(0))(
        {"business_name": "B", "city": "C", "website": site}
    )
    assert res["status"] == "robots_blocked" and page.visited == []


def test_lead_enrich_hard_cap_and_csv(tmp_path, monkeypatch):
    rows_in = tmp_path / "leads.csv"
    with open(rows_in, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["business_name", "city", "website"])
        for i in range(60):
            w.writerow([f"Biz {i}", "Town", f"https://biz{i}.example/"])

    def fake_run_agent(run, rows, check, local=False, setup=None, extra=None):
        run.each(rows, lambda row: {"status": "ok", **row, "phone": "(555) 010-0100"})
        return run.finish(extra())

    monkeypatch.setattr(lead_enrich.bb, "run_agent", fake_run_agent)
    out = tmp_path / "out"
    lead_enrich.main(["--csv", str(rows_in), "--max-targets", "500", "--out", str(out)])
    receipt = json.loads(next(out.glob("lead_enrich/*/receipt-*.json")).read_text())
    assert len(receipt["results"]) == 50 and "max targets reached (50)" in receipt["stopped_reason"]
    with open(receipt["enriched_csv"], newline="") as fh:
        enriched = list(csv.DictReader(fh))
    assert len(enriched) == 50 and enriched[0]["phone"] == "(555) 010-0100"
    assert "name" not in enriched[0]


# --- listing_audit ----------------------------------------------------------

TARGET = {
    "name": "Example Bakery",
    "address": "123 Main Street",
    "city": "Springfield, IL",
    "phone": "(555) 010-0100",
}


def test_nap_check_handles_abbreviations():
    nap = listing_audit.nap_check(TARGET, "The Example Bakery\n123 Main St\n(555) 010-0100")
    assert nap["mismatched"] == [] and all(nap["fields"].values())


def test_yelp_listing_url_matches_name():
    url = listing_audit.yelp_listing_url(fixture("yelp_search.html"), "Example Bakery")
    assert url == "https://www.yelp.com/biz/example-bakery-springfield-2"


def test_listing_audit_reports_consistent_inconsistent_and_claim_urls(run):
    page = FakePage(
        {
            "https://www.yelp.com/search*": fixture("yelp_search.html"),
            "https://www.yelp.com/biz/example-bakery-springfield-2": fixture("yelp_biz.html"),
            "https://maps.apple.com/*": fixture("apple_place.html"),
        }
    )
    res = listing_audit.check_target(page, TARGET, run)
    yelp, apple = res["listings"]["yelp"], res["listings"]["apple_maps"]
    assert yelp["state"] == "consistent"
    assert apple["state"] == "inconsistent" and set(apple["mismatched"]) == {"phone", "address"}
    assert apple["claim_url"] == "https://businessconnect.apple.com/"
    assert res["status"] == "warn"


def test_listing_audit_missing_and_isolated_failures(run, monkeypatch):
    page = FakePage({"https://www.yelp.com/search*": "<html><body>No results</body></html>"})

    def boom(*_):
        raise TimeoutError("apple timed out")

    monkeypatch.setitem(listing_audit.SOURCES, "apple_maps", boom)
    res = listing_audit.check_target(page, TARGET, run)
    assert res["listings"]["yelp"]["state"] == "missing"
    assert res["listings"]["yelp"]["claim_url"] == "https://biz.yelp.com/claim"
    assert res["listings"]["apple_maps"] == {
        "state": "unknown",
        "error": "TimeoutError: apple timed out",
        "claim_url": "https://businessconnect.apple.com/",
    }
