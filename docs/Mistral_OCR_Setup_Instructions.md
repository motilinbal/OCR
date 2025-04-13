# 🚀 Mistral OCR App Setup: Free Tier & Paid Usage Guide

Welcome! This guide will help you set up your Mistral AI account and API key to use the Mistral OCR (`mistral-ocr-latest`) model with your application.  
You can experiment with the OCR model using the free API tier, but **billing activation is required** even for free usage.

---

## 1. **Create or Access Your Mistral AI Account**

1. **Go to the Mistral AI Console:**  
   👉 [https://console.mistral.ai/](https://console.mistral.ai/)

2. **Sign Up or Log In:**  
   - Use **Google**, **Microsoft**, **Apple**, or your **Email & Password**.
   - _New user?_ Click "Sign up" and follow the prompts (email verification, workspace name, etc.).
   - _Already have an account?_ Just log in with your chosen method.

---

## 2. **Activate Billing (Required for Free Tier)**

> **Why?**  
> Mistral requires billing activation for all API usage, including the free tier.  
> As of early 2025, the free tier allows you to experiment with certain models and features (including OCR, if available in your workspace) without initial charges, but you must still add payment details.

1. In the console, go to **Workspace** > **Billing**.
2. Click **Add Payment Method** or **Activate Payments**.
3. Enter your payment details (credit card, etc.) and follow the instructions.
4. Once billing is active, you’re ready for the next step!

---

## 3. **Check Free Tier Availability for OCR**

- The free tier's available models and features can vary by workspace.
- To confirm if you can use `mistral-ocr-latest` for free:
  1. Go to the [Usage & Limits page in your console](https://console.mistral.ai/usage).
  2. Look for "mistral-ocr-latest" or "OCR" in the list of available models/features.
  3. If it is listed under your free tier, you can use it within the free tier's limits (see below).

**Free Tier Limits (as of early 2025):**
- **Requests Per Second (RPS):** 1
- **Tokens Per Minute (TPM):** 500,000
- **Tokens Per Month:** 1,000,000,000 (1 Billion)
- **OCR Pricing:** About $1 per 1,000 pages (see [Mistral Pricing Page](https://mistral.ai/products/la-plateforme#pricing) for details).

> **Note:** If you use features or models not included in your free tier, or exceed the free tier limits, you will be charged according to the pricing page.

---

## 4. **Generate Your API Key**

1. In the console, find **API Keys** (usually under Workspace or in the main menu).
2. Click **Create new key**.
3. (Optional) Give your key a name (e.g., "My OCR App Key") and set an expiry date for extra security.
4. **Copy your API key immediately!**  
   - You’ll only see it once.  
   - Click the copy button or select and copy the key string.

> ⚠️ **Keep your API key safe!**  
> Anyone with this key can use your account and spend your credits.

---

## 5. **Store Your API Key Securely**

- **Best options:**  
  - Password manager (Bitwarden, 1Password, etc.)  
  - Secure, encrypted note app  
  - Private, encrypted file

- **Never:**  
  - Save in plain text on a shared computer  
  - Email or message it unencrypted  
  - Paste into public/shared code or documents

---

## 6. **Connect the API Key to Your OCR App**

- Your Python OCR app will ask for the API key (in a config file, environment variable, or prompt).
- Paste your key where instructed.
- The app will use this key to securely access Mistral OCR on your behalf.

---

## ✅ **Setup Checklist**

- [ ] Created/logged into Mistral AI account
- [ ] Activated billing (required for free and paid usage)
- [ ] Checked if `mistral-ocr-latest` is available in your free tier ([console usage page](https://console.mistral.ai/usage))
- [ ] Generated and copied API key
- [ ] Stored API key securely
- [ ] Added API key to your OCR app

---

## 🎉 **You’re Ready!**

Your Python OCR application is now set up to use Mistral AI’s powerful OCR service.  
**Enjoy fast, accurate text extraction—and remember to keep your API key safe!**

---

**Useful Links:**
- [Mistral Pricing Page](https://mistral.ai/products/la-plateforme#pricing)
- [Usage & Limits in Console](https://console.mistral.ai/usage)