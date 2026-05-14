const DEFAULT_EXCHANGE_RATE = 7300;
const EXCHANGE_RATE_API_URL = "https://open.er-api.com/v6/latest/USD";

let exchangeRate = DEFAULT_EXCHANGE_RATE;

const guaraniesInput = document.querySelector("#guaraniesInput");
const usdOutput = document.querySelector("#usdOutput");
const rateStatus = document.querySelector("#rateStatus");
const errorMessage = document.querySelector("#errorMessage");

function convertGuaraniesToUsd(amountGuaranies, pygPerUsd) {
  if (pygPerUsd <= 0) {
    throw new Error("Exchange rate must be greater than zero");
  }

  if (amountGuaranies < 0) {
    throw new Error("Amount cannot be negative");
  }

  return amountGuaranies / pygPerUsd;
}

function cleanNumber(value) {
  return value.replace(/,/g, "").trim();
}

function formatUsd(value) {
  return value.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function updateConversion() {
  errorMessage.textContent = "";
  const rawAmount = cleanNumber(guaraniesInput.value);

  if (!rawAmount) {
    usdOutput.value = "0.00";
    return;
  }

  const amount = Number(rawAmount);

  if (!Number.isFinite(amount)) {
    usdOutput.value = "0.00";
    errorMessage.textContent = "Enter a valid number";
    return;
  }

  try {
    usdOutput.value = formatUsd(convertGuaraniesToUsd(amount, exchangeRate));
  } catch (error) {
    usdOutput.value = "0.00";
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

    if (data.result !== "success" || !data.rates || !data.rates.PYG) {
      throw new Error("Exchange rate API returned an invalid response");
    }

    exchangeRate = Number(data.rates.PYG);
    rateStatus.textContent = `Live rate: 1 USD = ${exchangeRate.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} PYG`;
  } catch (error) {
    exchangeRate = DEFAULT_EXCHANGE_RATE;
    rateStatus.textContent = `Using fallback rate: 1 USD = ${DEFAULT_EXCHANGE_RATE.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} PYG`;
  }

  updateConversion();
}

guaraniesInput.addEventListener("input", updateConversion);
loadExchangeRate();
