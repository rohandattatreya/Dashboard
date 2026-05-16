import unittest

from fastapi.testclient import TestClient

from main import app
from routers import fred, sec


class TestDashboardApiCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertIn("message", body)

    def test_overview_endpoint_shape(self):
        response = self.client.get("/api/overview")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("metrics", body)
        self.assertEqual(len(body["metrics"]), 6)
        for metric in body["metrics"]:
            self.assertTrue({"label", "value", "change", "positive"}.issubset(metric.keys()))

    def test_fred_search_empty_returns_full_catalog(self):
        response = self.client.get("/api/fred/search")
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), len(fred.SERIES_CATALOG))

    def test_fred_search_unknown_query_uses_fallback_subset(self):
        response = self.client.get("/api/fred/search", params={"q": "zzzz-not-found-zzzz"})
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), 5)

    def test_fred_series_known_id(self):
        response = self.client.get("/api/fred/series/GDP")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["metadata"]["id"], "GDP")
        self.assertIsInstance(body["data"], list)
        self.assertGreater(len(body["data"]), 0)
        self.assertTrue({"date", "value"}.issubset(body["data"][0].keys()))

    def test_fred_series_unknown_id_gets_custom_metadata_and_generic_data(self):
        response = self.client.get("/api/fred/series/unknown_series")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["metadata"]["id"], "UNKNOWN_SERIES")
        self.assertEqual(body["metadata"]["title"], "Series UNKNOWN_SERIES")
        self.assertEqual(body["metadata"]["frequency"], "Monthly")
        self.assertIsInstance(body["data"], list)
        self.assertGreater(len(body["data"]), 0)

    def test_sec_search_empty_returns_default_companies(self):
        response = self.client.get("/api/sec/search")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), len(sec.COMPANY_SEARCH))

    def test_sec_search_by_ticker(self):
        response = self.client.get("/api/sec/search", params={"q": "aapl"})
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["ticker"], "AAPL")

    def test_sec_search_unknown_returns_default_list(self):
        response = self.client.get("/api/sec/search", params={"q": "no-such-company"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), len(sec.COMPANY_SEARCH))

    def test_companyfacts_allows_zero_padded_cik(self):
        response = self.client.get("/api/sec/companyfacts/0000320193")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["cik"], "320193")
        self.assertEqual(body["entityName"], "Apple Inc.")
        us_gaap = body["facts"]["us-gaap"]
        self.assertIn("Revenues", us_gaap)
        self.assertIn("Assets", us_gaap)

    def test_companyfacts_not_found(self):
        response = self.client.get("/api/sec/companyfacts/9999999999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"].lower())

    def test_treasury_yield_curve_shape(self):
        response = self.client.get("/api/treasury/yield-curve")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["meta"]["total-count"], len(body["data"]))
        self.assertGreater(len(body["data"]), 0)
        self.assertTrue({"record_date", "d1_mo", "d10_yr", "d30_yr"}.issubset(body["data"][0].keys()))

    def test_treasury_latest_yield_curve_snapshot(self):
        response = self.client.get("/api/treasury/yield-curve/latest")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["date"], "2024-12-31")
        self.assertEqual(len(body["maturities"]), 12)
        self.assertEqual(body["maturities"][0]["label"], "1 Mo")
        self.assertEqual(body["maturities"][-1]["label"], "30 Yr")

    def test_treasury_proxy_routes_to_yield_curve(self):
        response = self.client.get("/api/treasury/data/yield")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("data", body)
        self.assertIn("meta", body)
        self.assertTrue({"record_date", "d2_yr"}.issubset(body["data"][0].keys()))

    def test_treasury_proxy_routes_to_debt(self):
        response = self.client.get("/api/treasury/data/debt_to_penny")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("data", body)
        self.assertIn("meta", body)
        self.assertLessEqual(len(body["data"]), 100)
        self.assertTrue({"record_date", "tot_pub_debt_out_amt"}.issubset(body["data"][0].keys()))

    def test_treasury_proxy_routes_to_exchange_rates(self):
        response = self.client.get("/api/treasury/data/rates_of_exchange")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("data", body)
        self.assertIn("meta", body)
        self.assertTrue({"country", "currency", "exchange_rate"}.issubset(body["data"][0].keys()))

    def test_treasury_proxy_defaults_to_auctions(self):
        response = self.client.get("/api/treasury/data/some_other_endpoint")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("data", body)
        self.assertIn("meta", body)
        self.assertEqual(body["meta"]["total-count"], 50)
        self.assertTrue({"security_type", "security_term", "high_yield"}.issubset(body["data"][0].keys()))


if __name__ == "__main__":
    unittest.main()
