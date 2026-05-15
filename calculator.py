import json
import threading
import tkinter as tk
from tkinter import ttk
from urllib.error import URLError
from urllib.request import urlopen


DEFAULT_RATES = {
    "PYG": 7300.0,
    "BRL": 5.0,
}
EXCHANGE_RATE_API_URL = "https://open.er-api.com/v6/latest/USD"


def convert_to_usd(amount, currency, rates):
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    if currency == "USD":
        return amount

    rate = rates[currency]
    if rate <= 0:
        raise ValueError("Exchange rate must be greater than zero")
    return amount / rate


def convert_from_usd(amount_usd, currency, rates):
    if amount_usd < 0:
        raise ValueError("Amount cannot be negative")
    if currency == "USD":
        return amount_usd

    rate = rates[currency]
    if rate <= 0:
        raise ValueError("Exchange rate must be greater than zero")
    return amount_usd * rate


def convert_guaranies_to_usd(amount_guaranies, exchange_rate):
    return convert_to_usd(amount_guaranies, "PYG", {"PYG": exchange_rate})


def fetch_rates_per_usd(urlopen_func=urlopen):
    with urlopen_func(EXCHANGE_RATE_API_URL, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))

    if data.get("result") != "success":
        raise ValueError("Exchange rate API did not return success")

    rates = {
        "PYG": float(data["rates"]["PYG"]),
        "BRL": float(data["rates"]["BRL"]),
    }

    if any(rate <= 0 for rate in rates.values()):
        raise ValueError("Exchange rate API returned an invalid rate")
    return rates


def fetch_pyg_per_usd_rate(urlopen_func=urlopen):
    return fetch_rates_per_usd(urlopen_func)["PYG"]


def draw_paraguay_flag(canvas):
    canvas.create_rectangle(0, 0, 150, 30, fill="#d52b1e", width=0)
    canvas.create_rectangle(0, 30, 150, 60, fill="#ffffff", width=0)
    canvas.create_rectangle(0, 60, 150, 90, fill="#0038a8", width=0)
    canvas.create_oval(63, 28, 87, 52, fill="#f7d116", outline="#25408f", width=2)
    canvas.create_text(75, 40, text="PY", fill="#25408f", font=("Segoe UI", 8, "bold"))


def draw_usa_flag(canvas):
    stripe_height = 90 / 13
    for stripe in range(13):
        color = "#b22234" if stripe % 2 == 0 else "#ffffff"
        y1 = stripe * stripe_height
        y2 = y1 + stripe_height
        canvas.create_rectangle(0, y1, 150, y2, fill=color, width=0)

    canvas.create_rectangle(0, 0, 60, stripe_height * 7, fill="#3c3b6e", width=0)

    for row in range(5):
        for col in range(6):
            x = 6 + col * 9
            y = 6 + row * 8
            canvas.create_text(x, y, text="*", fill="#ffffff", font=("Segoe UI", 6, "bold"))


def draw_brazil_flag(canvas):
    canvas.create_rectangle(0, 0, 150, 90, fill="#009b3a", width=0)
    canvas.create_polygon(75, 13, 132, 45, 75, 77, 18, 45, fill="#f7d116", width=0)
    canvas.create_oval(54, 24, 96, 66, fill="#002776", outline="#002776")
    canvas.create_text(75, 45, text="BR", fill="#ffffff", font=("Segoe UI", 10, "bold"))


class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("640x540")
        self.root.resizable(False, False)

        self.rates = dict(DEFAULT_RATES)
        self.guaranies_var = tk.StringVar()
        self.usd_var = tk.StringVar()
        self.brl_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.rate_status_var = tk.StringVar(value="Loading live exchange rate...")
        self.active_currency = "PYG"
        self.is_updating_fields = False

        self.guaranies_var.trace_add("write", lambda *args: self.convert("PYG"))
        self.usd_var.trace_add("write", lambda *args: self.convert("USD"))
        self.brl_var.trace_add("write", lambda *args: self.convert("BRL"))

        self.build_interface()
        self.load_exchange_rate()

    def build_interface(self):
        self.root.configure(bg="#f4f7fb")

        main = ttk.Frame(self.root, padding=24)
        main.pack(fill="both", expand=True)

        title = ttk.Label(
            main,
            text="Currency Converter",
            font=("Segoe UI", 20, "bold"),
        )
        title.pack(anchor="center", pady=(0, 18))

        flags = ttk.Frame(main)
        flags.pack(fill="x", pady=(0, 20))

        paraguay_frame = ttk.Frame(flags)
        paraguay_frame.pack(side="left", expand=True)
        paraguay_canvas = tk.Canvas(paraguay_frame, width=150, height=90, highlightthickness=1)
        paraguay_canvas.pack()
        draw_paraguay_flag(paraguay_canvas)
        ttk.Label(paraguay_frame, text="Paraguay - PYG").pack(pady=(8, 0))

        arrow = ttk.Label(flags, text="to", font=("Segoe UI", 13, "bold"))
        arrow.pack(side="left", padx=18)

        usa_frame = ttk.Frame(flags)
        usa_frame.pack(side="left", expand=True)
        usa_canvas = tk.Canvas(usa_frame, width=150, height=90, highlightthickness=1)
        usa_canvas.pack()
        draw_usa_flag(usa_canvas)
        ttk.Label(usa_frame, text="United States - USD").pack(pady=(8, 0))

        brazil_frame = ttk.Frame(flags)
        brazil_frame.pack(side="left", expand=True)
        brazil_canvas = tk.Canvas(brazil_frame, width=150, height=90, highlightthickness=1)
        brazil_canvas.pack()
        draw_brazil_flag(brazil_canvas)
        ttk.Label(brazil_frame, text="Brazil - BRL").pack(pady=(8, 0))

        form = ttk.Frame(main)
        form.pack(fill="x", pady=(4, 18))

        ttk.Label(form, text="Amount in Guaranies (PYG)").grid(row=0, column=0, sticky="w")
        amount_entry = ttk.Entry(form, textvariable=self.guaranies_var, font=("Segoe UI", 12))
        amount_entry.grid(row=1, column=0, sticky="ew", pady=(5, 12))

        ttk.Label(form, text="Amount in USD").grid(row=2, column=0, sticky="w")
        usd_entry = ttk.Entry(form, textvariable=self.usd_var, font=("Segoe UI", 12))
        usd_entry.grid(row=3, column=0, sticky="ew", pady=(5, 12))

        ttk.Label(form, text="Amount in Brazilian Reais (BRL)").grid(row=4, column=0, sticky="w")
        brl_entry = ttk.Entry(form, textvariable=self.brl_var, font=("Segoe UI", 12))
        brl_entry.grid(row=5, column=0, sticky="ew", pady=(5, 12))

        form.columnconfigure(0, weight=1)

        rate_status = ttk.Label(
            main,
            textvariable=self.rate_status_var,
            font=("Segoe UI", 10),
        )
        rate_status.pack(pady=(2, 6))

        error = ttk.Label(main, textvariable=self.error_var, foreground="#b00020")
        error.pack()

        attribution = ttk.Label(
            main,
            text="Exchange rates by ExchangeRate-API",
            font=("Segoe UI", 9),
        )
        attribution.pack(side="bottom", pady=(10, 0))

        amount_entry.focus()

    def load_exchange_rate(self):
        thread = threading.Thread(target=self.update_exchange_rate_from_api, daemon=True)
        thread.start()

    def update_exchange_rate_from_api(self):
        try:
            rates = fetch_rates_per_usd()
        except (KeyError, TypeError, ValueError, URLError, TimeoutError):
            self.root.after(0, self.show_fallback_exchange_rate)
            return

        self.root.after(0, lambda: self.show_live_exchange_rate(rates))

    def show_live_exchange_rate(self, rates):
        self.rates = rates
        self.rate_status_var.set(
            f"Live rates: 1 USD = {rates['PYG']:,.2f} PYG / {rates['BRL']:,.2f} BRL"
        )
        self.convert(self.active_currency)

    def show_fallback_exchange_rate(self):
        self.rates = dict(DEFAULT_RATES)
        self.rate_status_var.set(
            f"Using fallback rates: 1 USD = {DEFAULT_RATES['PYG']:,.2f} PYG / "
            f"{DEFAULT_RATES['BRL']:,.2f} BRL"
        )
        self.convert(self.active_currency)

    def convert(self, currency):
        if self.is_updating_fields:
            return

        self.active_currency = currency
        self.error_var.set("")

        try:
            source_var = {
                "PYG": self.guaranies_var,
                "USD": self.usd_var,
                "BRL": self.brl_var,
            }[currency]
            amount_text = source_var.get().replace(",", "").strip()

            if not amount_text:
                self.set_other_fields(currency, "", "")
                return

            amount = float(amount_text)
            usd_amount = convert_to_usd(amount, currency, self.rates)
        except ValueError as error:
            self.error_var.set(str(error) if str(error) else "Enter valid numbers")
            return

        self.set_converted_fields(currency, usd_amount)

    def set_other_fields(self, source_currency, pyg_value, usd_value, brl_value=""):
        self.is_updating_fields = True
        if source_currency != "PYG":
            self.guaranies_var.set(pyg_value)
        if source_currency != "USD":
            self.usd_var.set(usd_value)
        if source_currency != "BRL":
            self.brl_var.set(brl_value)
        self.is_updating_fields = False

    def set_converted_fields(self, source_currency, usd_amount):
        self.set_other_fields(
            source_currency,
            f"{convert_from_usd(usd_amount, 'PYG', self.rates):,.0f}",
            f"{convert_from_usd(usd_amount, 'USD', self.rates):,.2f}",
            f"{convert_from_usd(usd_amount, 'BRL', self.rates):,.2f}",
        )


def main():
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
