import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "vpngate_manager.py"
README = ROOT / "README.md"
INSTALL = ROOT / "install.sh"


def read_index_html() -> str:
    text = SOURCE.read_text(encoding="utf-8")
    match = re.search(r'INDEX_HTML = r"""(.*?)"""', text, re.S)
    if not match:
        raise AssertionError("INDEX_HTML template not found")
    return match.group(1)


class IndexTemplateTests(unittest.TestCase):
    def test_theme_toggle_is_available_and_persistent(self):
        html = read_index_html()

        self.assertIn('id="theme_toggle"', html)
        self.assertIn("applyTheme", html)
        self.assertIn("localStorage.setItem", html)
        self.assertIn('data-theme="light"', html)

    def test_vps_promo_entry_points_are_removed(self):
        html = read_index_html()

        self.assertNotIn("vps-promo-tab", html)
        self.assertNotIn("ad_modal", html)
        self.assertNotIn("openAdModal", html)
        self.assertNotIn("closeAdModal", html)
        self.assertNotIn("racknerd.com/aff", html.lower())
        self.assertNotIn("vmiss.com/aff", html.lower())
        self.assertNotIn("bandwagonhost.com/aff", html.lower())
        self.assertNotRegex(html, r"https://t\.me/[A-Za-z0-9_]+")
        self.assertNotRegex(html, r"github\.com/(?!Pretic/aimili-vpngate-pre)[^\"']+")
        self.assertIn("github.com/Pretic/aimili-vpngate-pre", html)

    def test_table_filters_and_default_page_size(self):
        html = read_index_html()

        self.assertIn('id="status_filter"', html)
        self.assertIn('id="quality_filter"', html)
        self.assertIn('id="ip_type_filter"', html)
        self.assertIn('<option value="residential" selected>', html)
        self.assertIn("const pageSize = 20;", html)
        self.assertIn('const selectedStatus = $("status_filter").value;', html)
        self.assertIn('const selectedQuality = $("quality_filter").value;', html)
        self.assertIn('const selectedIpType = $("ip_type_filter").value;', html)

    def test_page_and_bulk_test_buttons_are_concurrency_limited(self):
        html = read_index_html()

        self.assertIn('id="btn_batch_test"', html)
        self.assertIn("测试本页", html)
        self.assertIn('id="btn_test_all"', html)
        self.assertIn("测试全部", html)
        self.assertIn("const bulkTestConcurrency = 5;", html)
        self.assertIn("const filteredNodes = getFilteredNodes();", html)
        self.assertNotIn("maxBulkTestNodes", html)
        self.assertNotIn(".slice(0, maxBulkTestNodes)", html)
        self.assertIn("runNodeTests", html)

    def test_public_files_do_not_include_original_identity_or_fixed_secret(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in (SOURCE, README, INSTALL)
        )

        blocked_tokens = [
            "EJsW2EeBo9lY",
            "random.choices",
        ]
        for token in blocked_tokens:
            self.assertNotIn(token, combined)

        self.assertNotRegex(combined, r"https://t\.me/[A-Za-z0-9_]+")
        self.assertNotRegex(combined, r"mailto:[^)\s]+")
        self.assertNotRegex(combined, r"raw\.githubusercontent\.com/(?!Pretic/aimili-vpngate-pre)")
        self.assertIsNone(re.search(r"0x[A-Fa-f0-9]{40}", combined))
        self.assertIsNone(re.search(r"\bT[A-Za-z0-9]{33}\b", combined))
        self.assertIn("DEFAULT_USER=\"Pretic\"", combined)
        self.assertIn("DEFAULT_REPO=\"aimili-vpngate-pre\"", combined)

    def test_status_bar_escapes_dynamic_text(self):
        html = read_index_html()

        self.assertIn("${esc(localProxy)}", html)
        self.assertIn("${esc(statusMessage)}", html)


if __name__ == "__main__":
    unittest.main()
