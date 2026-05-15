const DEFAULT_RATES = {
  PYG: 7300,
  BRL: 5,
};
const EXCHANGE_RATE_API_URL = "https://open.er-api.com/v6/latest/USD";

let rates = { ...DEFAULT_RATES };
let isUpdatingFields = false;

const guaraniesInput = document.querySelector("#guaraniesInput");
const usdInput = document.querySelector("#usdInput");
const brlInput = document.querySelector("#brlInput");
const rateStatus = document.querySelector("#rateStatus");
const errorMessage = document.querySelector("#errorMessage");

function convertToUsd(amount, currency, currentRates) {
  if (amount < 0) {
    throw new Error("Amount cannot be negative");
  }

  if (currency === "USD") {
    return amount;
  }

  const rate = currentRates[currency];

  if (rate <= 0) {
    throw new Error("Exchange rate must be greater than zero");
  }

  return amount / rate;
}

function convertFromUsd(amountUsd, currency, currentRates) {
  if (amountUsd < 0) {
    throw new Error("Amount cannot be negative");
  }

  if (currency === "USD") {
    return amountUsd;
  }

  const rate = currentRates[currency];

  if (rate <= 0) {
    throw new Error("Exchange rate must be greater than zero");
  }

  return amountUsd * rate;
}

function cleanNumber(value) {
  return value.replace(/,/g, "").trim();
}

function formatEditableNumber(value) {
  const rawValue = cleanNumber(value);

  if (!rawValue) {
    return "";
  }

  const isNegative = rawValue.startsWith("-");
  const unsignedValue = rawValue.replace(/-/g, "");
  const hasDecimal = unsignedValue.includes(".");
  const [integerPart, ...decimalParts] = unsignedValue.split(".");
  const digitsOnlyInteger = integerPart.replace(/\D/g, "");
  const decimalPart = decimalParts.join("").replace(/\D/g, "");
  const groupedInteger = (digitsOnlyInteger || "0").replace(/\B(?=(\d{3})+(?!\d))/g, ",");

  return `${isNegative ? "-" : ""}${groupedInteger}${hasDecimal ? `.${decimalPart}` : ""}`;
}

function formatCurrency(value, currency) {
  const decimalPlaces = currency === "PYG" ? 0 : 2;

  return value.toLocaleString("en-US", {
    minimumFractionDigits: decimalPlaces,
    maximumFractionDigits: decimalPlaces,
  });
}

function formatSourceField(sourceInput) {
  const formattedValue = formatEditableNumber(sourceInput.value);
  sourceInput.value = formattedValue;
  sourceInput.setSelectionRange(formattedValue.length, formattedValue.length);
}

function setFieldValues(amountUsd, sourceInput) {
  isUpdatingFields = true;

  if (sourceInput !== guaraniesInput) {
    guaraniesInput.value = formatCurrency(convertFromUsd(amountUsd, "PYG", rates), "PYG");
  }

  if (sourceInput !== usdInput) {
    usdInput.value = formatCurrency(convertFromUsd(amountUsd, "USD", rates), "USD");
  }

  if (sourceInput !== brlInput) {
    brlInput.value = formatCurrency(convertFromUsd(amountUsd, "BRL", rates), "BRL");
  }

  isUpdatingFields = false;
}

function clearOtherFields(sourceInput) {
  isUpdatingFields = true;

  if (sourceInput !== guaraniesInput) {
    guaraniesInput.value = "";
  }

  if (sourceInput !== usdInput) {
    usdInput.value = "";
  }

  if (sourceInput !== brlInput) {
    brlInput.value = "";
  }

  isUpdatingFields = false;
}

function updateConversion(sourceInput, sourceCurrency) {
  if (isUpdatingFields) {
    return;
  }

  errorMessage.textContent = "";
  const rawAmount = cleanNumber(sourceInput.value);

  if (!rawAmount) {
    clearOtherFields(sourceInput);
    return;
  }

  const amount = Number(rawAmount);

  if (!Number.isFinite(amount)) {
    errorMessage.textContent = "Enter a valid number";
    return;
  }

  try {
    formatSourceField(sourceInput);
    setFieldValues(convertToUsd(amount, sourceCurrency, rates), sourceInput);
  } catch (error) {
    errorMessage.textContent = error.message;
  }
}

async function loadExchangeRate() {
  try {
    const response = await fetch(EXCHANGE_RATE_API_URL);

    if (!response.ok) {
      throw new Error("Could not load exchange rate");
    }

    const data = await response.json();

    if (data.result !== "success" || !data.rates || !data.rates.PYG || !data.rates.BRL) {
      throw new Error("Exchange rate API returned an invalid response");
    }

    rates = {
      PYG: Number(data.rates.PYG),
      BRL: Number(data.rates.BRL),
    };
    rateStatus.textContent = `Live rates: 1 USD = ${rates.PYG.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} PYG / ${rates.BRL.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} BRL`;
  } catch (error) {
    rates = { ...DEFAULT_RATES };
    rateStatus.textContent = `Using fallback rates: 1 USD = ${DEFAULT_RATES.PYG.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} PYG / ${DEFAULT_RATES.BRL.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} BRL`;
  }

  const activeInput = document.activeElement;

  if (activeInput === usdInput) {
    updateConversion(usdInput, "USD");
  } else if (activeInput === brlInput) {
    updateConversion(brlInput, "BRL");
  } else {
    updateConversion(guaraniesInput, "PYG");
  }
}

guaraniesInput.addEventListener("input", () => updateConversion(guaraniesInput, "PYG"));
usdInput.addEventListener("input", () => updateConversion(usdInput, "USD"));
brlInput.addEventListener("input", () => updateConversion(brlInput, "BRL"));
loadExchangeRate();
