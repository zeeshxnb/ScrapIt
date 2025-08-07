# Setting up OpenAI o1 API for ScrapIt

This guide explains how to set up the OpenAI o1 model API for the ScrapIt application.

## Steps to Set Up OpenAI API

### 1. Create an OpenAI Account

1. Go to [OpenAI's website](https://openai.com/)
2. Click on "Sign Up" to create a new account or "Log In" if you already have one
3. Complete the registration process

### 2. Get an API Key

1. Log in to your OpenAI account
2. Navigate to the [API keys page](https://platform.openai.com/api-keys)
3. Click on "Create new secret key"
4. Give your key a name (e.g., "ScrapIt App")
5. Copy the API key immediately (it won't be shown again)

### 3. Set Up Payment Method

1. Go to the [Billing section](https://platform.openai.com/account/billing/overview)
2. Add a payment method
3. Set up usage limits if desired to control costs

### 4. Configure ScrapIt Application

1. Create a `.env` file in the project root if it doesn't exist already
2. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=o1
   ```

### 5. Verify API Access

1. Run the application in development mode
2. Test the chat interface to ensure API calls are working correctly

## Code Changes Made

The following changes were made to the codebase to use OpenAI o1 model exclusively:

1. Removed Claude API imports and integration
2. Updated model configurations to include o1 model
3. Simplified client initialization to use OpenAI only
4. Updated chat interface to use OpenAI requests only
5. Created settings file for centralized configuration

## OpenAI o1 Model Information

- **Context Length**: 32,768 tokens
- **Cost**: $0.15 per 1K tokens (as of implementation)
- **Capabilities**: Advanced reasoning, task extraction, and natural language understanding

## Troubleshooting

If you encounter issues with the OpenAI API:

1. Verify your API key is correct
2. Check your billing status on the OpenAI platform
3. Ensure you have sufficient credits/payment method set up
4. Check the application logs for specific error messages

For more information, visit the [OpenAI API documentation](https://platform.openai.com/docs/api-reference).