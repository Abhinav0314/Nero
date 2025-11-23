# API Keys Setup Instructions

## Required API Keys

To run the Coffee Shop Barista Voice Agent, you need to obtain and configure the following API keys:

### 1. Murf Falcon API Key (Required)

**What it does:** Powers the ultra-fast text-to-speech (TTS) for the agent's voice.

**How to get it:**
1. Go to [https://murf.ai/api](https://murf.ai/api)
2. Sign up or log in to your Murf account
3. Navigate to the API section
4. Generate a new API key
5. Copy the key

**Where to add it:**
- Open `backend\.env.local`
- Replace `your_murf_api_key_here` with your actual key:
  ```env
  MURF_API_KEY=marf_1234567890abcdefghijklmnop
  ```

---

### 2. Google Gemini API Key (Required)

**What it does:** Powers the LLM (Large Language Model) brain of the agent for understanding and responding to orders.

**How to get it:**
1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Select or create a Google Cloud project
5. Copy the generated API key

**Where to add it:**
- Open `backend\.env.local`
- Replace `your_google_api_key_here` with your actual key:
  ```env
  GOOGLE_API_KEY=AIzaSy...
  ```

---

### 3. Deepgram API Key (Required)

**What it does:** Powers the speech-to-text (STT) for understanding customer voice orders.

**How to get it:**
1. Go to [https://console.deepgram.com/](https://console.deepgram.com/)
2. Sign up or log in
3. Navigate to the "API Keys" section
4. Create a new API key
5. Copy the key

**Where to add it:**
- Open `backend\.env.local`
- Replace `your_deepgram_api_key_here` with your actual key:
  ```env
  DEEPGRAM_API_KEY=1234567890abcdefghijklmnop
  ```

---

## Verifying Your Configuration

After adding all three API keys, your `backend\.env.local` should look like this:

```env
# LiveKit Configuration (defaults for local dev)
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# API Keys - FILLED IN
MURF_API_KEY=marf_actual_key_here
GOOGLE_API_KEY=AIzaSy_actual_key_here
DEEPGRAM_API_KEY=actual_deepgram_key_here
```

---

## Security Best Practices

⚠️ **IMPORTANT:**
- **Never commit `.env.local` to git** - it's already in `.gitignore`
- **Don't share your API keys** publicly or in screenshots
- **Use environment variables or secrets** for production deployments
- **Rotate keys** if they're accidentally exposed

---

## Testing Your Keys

Once you've added all keys, test the setup:

```powershell
# Run the agent in console mode (voice in terminal)
cd backend
uv run python src/agent.py console
```

If you see errors about authentication or API keys, double-check that:
1. All three keys are present in `.env.local`
2. No extra spaces or quotes around the keys
3. The keys are valid and not expired

---

## Cost Considerations

- **Murf Falcon**: Check pricing at [murf.ai/pricing](https://murf.ai/pricing)
- **Google Gemini**: Generous free tier available - see [ai.google.dev/pricing](https://ai.google.dev/pricing)
- **Deepgram**: Free tier with credits - see [deepgram.com/pricing](https://deepgram.com/pricing)

Most testing and development can be done within free tiers!

---

## Troubleshooting

### "Invalid API Key" Errors
- Verify the key is copied correctly (no extra spaces)
- Check if the key has expired or been revoked
- Ensure you're using the right key type (e.g., not a restricted key)

### "Authentication Failed"
- For Google: Make sure the API key has the Gemini API enabled
- For Deepgram: Verify your account is active
- For Murf: Check that your account has API access enabled

### Rate Limit Errors
- You may be hitting free tier limits
- Consider upgrading or spacing out requests
- Check your usage dashboard for each service

---

## Next Steps

Once your keys are configured:
1. Download models: `cd backend; uv run python src/agent.py download-files`
2. Start the services: `.\start_app.ps1` (Windows) or `./start_app.sh` (Linux/Mac)
3. Open http://localhost:3000 and test!

---

## Support

If you encounter issues:
- Check the [SETUP_GUIDE.md](SETUP_GUIDE.md) for full setup instructions
- Review the [Challenge Repository](https://github.com/murf-ai/ten-days-of-voice-agents-2025)
- Join the [LiveKit Community Slack](https://livekit.io/join-slack)
