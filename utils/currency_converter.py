import requests

class CurrencyConverter:
    def __init__(self, api_key: str):
        self.api_key = api_key
        if api_key and api_key.strip():
            self.base_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest"
        else:
            self.base_url = None
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert the amount from one currency to another with fallback safety"""
        from_curr = from_currency.upper().strip()
        to_curr = to_currency.upper().strip()

        # Direct conversion if currencies are the same
        if from_curr == to_curr:
            return amount

        # Try to use API if available
        if self.base_url:
            try:
                url = f"{self.base_url}/{from_curr}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    rates = response.json().get("conversion_rates", {})
                    if to_curr in rates:
                        return amount * float(rates[to_curr])
            except Exception as e:
                print(f"Currency API call failed: {e}. Falling back to standard rates.")

        # Hardcoded fallback rates relative to USD (approximate rates for travel budget estimation)
        rates_to_usd = {
            "USD": 1.0,
            "INR": 83.5,
            "EUR": 0.92,
            "GBP": 0.78,
            "JPY": 157.0,
            "AUD": 1.51,
            "CAD": 1.37,
            "SGD": 1.35,
            "AED": 3.67,
            "CHF": 0.89,
            "CNY": 7.25,
            "HKD": 7.81,
            "NZD": 1.63,
            "KRW": 1380.0,
        }

        if from_curr in rates_to_usd and to_curr in rates_to_usd:
            # Convert from_curr to USD, then USD to to_curr
            usd_amount = amount / rates_to_usd[from_curr]
            return usd_amount * rates_to_usd[to_curr]

        # If one or both currencies are not in fallback list, just return 1:1 with warning
        print(f"Warning: Exchange rate from {from_curr} to {to_curr} not available in fallback. Returning amount as-is.")
        return amount
