import unittest

from calculator import (
    EXCHANGE_RATE_API_URL,
    convert_from_usd,
    convert_guaranies_to_usd,
    convert_to_usd,
    fetch_pyg_per_usd_rate,
    fetch_rates_per_usd,
)


class FakeApiResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return b'{"result": "success", "rates": {"PYG": 7300.5, "BRL": 5.25}}'


class TestCurrencyConverter(unittest.TestCase):
    def test_convert_guaranies_to_usd(self):
        self.assertEqual(convert_guaranies_to_usd(7300, 7300), 1)

    def test_convert_larger_amount(self):
        self.assertAlmostEqual(convert_guaranies_to_usd(36500, 7300), 5)

    def test_convert_brl_to_usd(self):
        self.assertAlmostEqual(convert_to_usd(10.5, "BRL", {"BRL": 5.25}), 2)

    def test_convert_usd_to_brl(self):
        self.assertAlmostEqual(convert_from_usd(2, "BRL", {"BRL": 5.25}), 10.5)

    def test_rejects_zero_exchange_rate(self):
        with self.assertRaises(ValueError):
            convert_guaranies_to_usd(10000, 0)

    def test_rejects_negative_exchange_rate(self):
        with self.assertRaises(ValueError):
            convert_guaranies_to_usd(10000, -7300)

    def test_rejects_negative_amount(self):
        with self.assertRaises(ValueError):
            convert_guaranies_to_usd(-10000, 7300)

    def test_fetch_pyg_per_usd_rate_from_api_response(self):
        calls = []

        def fake_urlopen(url, timeout):
            calls.append((url, timeout))
            return FakeApiResponse()

        self.assertEqual(fetch_pyg_per_usd_rate(fake_urlopen), 7300.5)
        self.assertEqual(calls, [(EXCHANGE_RATE_API_URL, 8)])

    def test_fetch_rates_per_usd_from_api_response(self):
        calls = []

        def fake_urlopen(url, timeout):
            calls.append((url, timeout))
            return FakeApiResponse()

        self.assertEqual(fetch_rates_per_usd(fake_urlopen), {"PYG": 7300.5, "BRL": 5.25})
        self.assertEqual(calls, [(EXCHANGE_RATE_API_URL, 8)])


if __name__ == "__main__":
    unittest.main()
