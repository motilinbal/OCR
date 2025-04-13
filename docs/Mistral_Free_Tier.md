# 🆓 Your Guide to Using the Mistral AI Free API Tier

## Introduction: Exploring Mistral AI for Free

Mistral AI offers powerful large language models (LLMs) accessible through its API platform, "La Plateforme." To encourage experimentation and allow developers to explore its capabilities, Mistral introduced a free API tier in September 2024. This tier provides a way to test various models and features without initial financial commitment, making it ideal for learning, prototyping, and personal projects.

This guide provides a user-friendly overview of the Mistral AI free API tier. It explains what the free tier offers, its limitations, how to set up an account to access it (including the important billing activation step), and provides a basic example of how to make API calls.

---

## What is La Plateforme?

**La Plateforme** is Mistral AI's central hub for developers. Here you can:
- Access Mistral's various AI models (open-source and commercial)
- Manage your API keys
- Monitor usage
- Utilize tools for fine-tuning, creating embeddings, and building AI-powered applications

Access to the API, including the free tier, is managed through your account on La Plateforme, accessible via the [Mistral AI console](https://console.mistral.ai).

---

## Understanding the Free Tier

### Purpose: Testing and Exploration

The primary purpose of the free API tier is to allow developers and enthusiasts to experiment with Mistral's models and API functionalities without incurring costs. It's designed for:
- **Learning:** Understanding how the Mistral API works
- **Prototyping:** Building and testing initial versions of applications
- **Evaluation:** Comparing Mistral models against others for specific tasks
- **Personal Projects:** Using Mistral AI for non-commercial, small-scale projects

> **Note:** The free tier is not intended for production applications due to its inherent limitations.

### What's Included?

The free tier grants access to the Mistral API, allowing you to make calls to certain endpoints and use specific models within defined limits. Typically included:
- **Core API Endpoints:** Such as the Chat Completions endpoint (`/v1/chat/completions`) and the Embeddings endpoint (`/v1/embeddings`)
- **Certain Models:** Usually Mistral's "Free Models" (often those released under permissive licenses like Apache 2.0) and potentially some smaller or older commercial models. Examples sometimes use `mistral-large-latest` or `mistral-embed`, but access may vary.

> **Crucial:** The exact models available under the free tier can vary and depend on your specific workspace configuration. The definitive source for what is available to your account under the free tier is the **"Limits"** section within your La Plateforme workspace console.  
> [Check your limits here.](https://console.mistral.ai/usage)

### What's Likely Excluded?

Due to their resource intensity or separate pricing structures, certain models and features are likely not included within the free tier's usage limits and will incur costs if used:
- **Premier Models:** Mistral's most powerful commercial models (e.g., Mistral Large, Pixtral Large, Codestral, Saba, Ministrals) may require a paid plan.
- **Advanced Features:**
  - Fine-tuning (incurs storage fees)
  - Batch API (separate pricing, discounted for high-volume)
  - Mistral OCR (per-page pricing)
  - Agents (custom agent deployment may have costs)

> Using these excluded models or features will likely result in charges, even if your overall token usage remains within the free tier's monthly limit.

---

## Account Setup & Accessing the Free Tier

Accessing the Mistral API, including the free tier, requires creating an account and generating an API key. **Billing activation is required** even for free usage.

### Step-by-Step Account Setup

1. **Create Account/Sign In:**  
   Go to the [Mistral AI Console](https://console.mistral.ai). Sign up or log in.
2. **Set Up Workspace (if new):**  
   If creating a new account, set up a workspace, provide a name, and accept terms.
3. **Activate Billing:**  
   Go to the "Workspace" section, then "Billing". Add your payment information and activate payments for your account.
4. **Generate API Key:**  
   Go to the "API keys" page within your workspace. Click "Create new key". Optionally set a name and expiration.
5. **Copy and Secure Your Key:**  
   Your new API key will be displayed only once. Copy it immediately and store it securely.

#### Why is Billing Activation Required for the Free Tier?

- **Identity Verification:** Prevents abuse and multiple anonymous accounts.
- **Abuse Prevention:** Deters bots and malicious actors.
- **Seamless Upgrade Path:** Makes it easier to transition to a paid tier if needed.

> As long as your usage stays strictly within the defined free tier limits and you only use included models/features, you should not be charged.

---

## Free Tier Limits

The free tier comes with specific usage limits applied at the workspace level (as of late 2024 / early 2025):

- **Requests Per Second (RPS):** 1  
  (You can send, on average, only one API request every second.)
- **Tokens Per Minute (TPM):** 500,000  
  (Tokens are the basic units of text processed by the model.)
- **Tokens Per Month:** 1,000,000,000 (1 Billion)

These limits apply across all models compatible with the free tier within your workspace. The most significant constraint is often the 1 RPS limit, which prevents rapid testing or handling multiple requests simultaneously.

> For the most up-to-date pricing and limits, see the [Mistral Pricing Page](https://mistral.ai/products/la-plateforme#pricing).

---

## Using the Free Tier (Python Example)

Once you have your API key, you can start making calls. Here’s a basic Python example using the official mistralai library.

### 1. Install the Library

```bash
pip install mistralai
```

### 2. Python Code Example

Save your API key as an environment variable named `MISTRAL_API_KEY` for security.

```python
import os
from mistralai.client import Mistral
from mistralai.models.chat_completion import ChatMessage

# Ensure your API key is set as an environment variable
api_key = os.environ.get("MISTRAL_API_KEY")

# --- CHOOSE A MODEL ---
# Check your workspace limits page to confirm which models are available on the free tier for you.
# Examples (availability on free tier not guaranteed for all):
# model = "mistral-small-latest" # Often a good candidate for free tier
model = "mistral-embed"        # Dedicated embedding model

if not api_key:
    print("Error: MISTRAL_API_KEY environment variable not set.")
else:
    client = Mistral(api_key=api_key)
    print(f"Using API Key: {'*' * (len(api_key) - 4)}{api_key[-4:]}") # Mask key for printing

    # --- Example 1: Chat Completion (if model supports it) ---
    if model != "mistral-embed": # Embeddings model cannot be used for chat
        try:
            print(f"\nAttempting chat completion with model: {model}")
            chat_response = client.chat(
                model=model,
                messages=[ChatMessage(role="user", content="What is the best French cheese?")]
            )
            print("\nChat Completion Response:")
            print(chat_response.choices.message.content)
            print(f"Token Usage: Prompt={chat_response.usage.prompt_tokens}, Completion={chat_response.usage.completion_tokens}, Total={chat_response.usage.total_tokens}")
        except Exception as e:
            print(f"Error during chat completion with {model}: {e}")
            print("Check if this model is enabled for chat in your workspace limits or try a different model.")

    # --- Example 2: Embeddings ---
    try:
        print(f"\nAttempting embeddings with model: mistral-embed")
        embeddings_response = client.embeddings(
            model="mistral-embed",
            input=["Embed this sentence.", "As well as this one."]
        )
        print("\nEmbeddings Response:")
        print(f"Generated {len(embeddings_response.data)} embeddings.")
        print(f"Length of first embedding vector: {len(embeddings_response.data.embedding)}")
        print(f"Token Usage: Prompt={embeddings_response.usage.prompt_tokens}, Total={embeddings_response.usage.total_tokens}")
    except Exception as e:
        print(f"Error during embeddings: {e}")
        print("Check if the mistral-embed model is enabled in your workspace limits.")
```

---

## Important Considerations & Limitations

- **Designed for Testing, Not Production:** The restrictive rate limits (especially 1 RPS) and potential lack of guaranteed service levels make the free tier unsuitable for live applications or services offered to end-users.
- **Restrictive Rate Limits:** The 1 request per second limit is a major bottleneck for anything beyond simple, sequential testing. The token limits (500k TPM, 1B/month) are generous for initial exploration but can be reached with sustained use or large tasks.
- **Potential Exclusions:** Not all models (especially premier ones like Mistral Large) or features (Fine-tuning, Batch API, OCR, Agents) are guaranteed to be usable within the free tier limits. Always verify compatibility and potential costs by checking the [Usage page in your console](https://console.mistral.ai/usage).

---

## Moving Beyond the Free Tier

If your needs exceed the free tier's limitations, or you plan to deploy an application to production, you will need to upgrade to a paid tier.

- **When to Upgrade:** Consider upgrading if you consistently hit rate limits, require access to premium models or features, or need the reliability and performance guarantees suitable for production environments.
- **Finding Pricing Information:** Mistral AI provides details about paid tiers and model-specific pricing on their [official pricing page](https://mistral.ai/products/la-plateforme#pricing).

---

## Conclusion

Mistral AI's free API tier offers a valuable opportunity for developers to explore its models and platform capabilities without upfront costs. It's an excellent resource for learning, experimentation, and prototyping.

**Key points:**
- **Billing Activation is Mandatory:** You must provide payment details and activate billing before generating an API key, even for free usage.
- **Strict Rate Limits:** The 1 RPS limit is the most significant constraint for testing.
- **Check Your Workspace:** The specific models and features available under the free tier can vary; always consult the [Usage page in your console](https://console.mistral.ai/usage) for the definitive list applicable to your account.
- **Not for Production:** The free tier is unsuitable for live applications due to its limitations.

By understanding these points, you can effectively leverage the Mistral AI free tier for its intended purpose – exploration and learning – before deciding if upgrading to a paid plan is necessary for your project.