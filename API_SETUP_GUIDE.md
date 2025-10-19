# 🔑 API Setup Guide for QaderiChat

This guide will help you get API keys for either Claude (Anthropic) or ChatGPT (OpenAI) to power your QaderiChat conversations.

## 🎯 **Which AI Should You Choose?**

### **Claude (Anthropic) - Recommended for Social Chat** 🌟
- **Excellent for conversations**: More natural, engaging dialogue
- **Better context understanding**: Remembers conversation flow better
- **Social intelligence**: Great at asking follow-up questions
- **Cost-effective**: Generally more affordable than GPT-4
- **Safety-focused**: Built with strong safety guidelines

### **ChatGPT (OpenAI) - Great All-Rounder** 🚀
- **Widely known**: Most popular AI assistant
- **Versatile**: Good at many different tasks
- **Large ecosystem**: Lots of community support
- **Multiple models**: Choose from GPT-3.5-turbo or GPT-4

## 🔧 **Getting Your Claude API Key (Recommended)**

### **Step 1: Create Anthropic Account**
1. Go to https://console.anthropic.com/
2. Click "Sign Up" or "Get Started"
3. Create your account with email and password
4. Verify your email address

### **Step 2: Add Billing Information**
1. Go to "Billing" in the console
2. Add a payment method (credit card)
3. Note: Claude has very reasonable pricing, often under $1 for hundreds of conversations

### **Step 3: Generate API Key**
1. Go to "API Keys" section
2. Click "Create Key"
3. Give it a name like "QaderiChat"
4. Copy the key (starts with `sk-ant-`)
5. **Important**: Save this key securely - you won't see it again!

### **Step 4: Configure QaderiChat**
Add to your `.env` file:
```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
AI_PROVIDER=claude
```

## 🤖 **Getting Your OpenAI API Key (Alternative)**

### **Step 1: Create OpenAI Account**
1. Go to https://platform.openai.com/
2. Click "Sign up" 
3. Create account or sign in with Google/Microsoft
4. Verify your phone number

### **Step 2: Add Billing**
1. Go to "Billing" → "Payment methods"
2. Add a credit card
3. Set usage limits if desired
4. Note: OpenAI pricing varies by model

### **Step 3: Generate API Key**
1. Go to "API keys" section
2. Click "Create new secret key"
3. Name it "QaderiChat"
4. Copy the key (starts with `sk-`)
5. **Important**: Store securely!

### **Step 4: Configure QaderiChat**
Add to your `.env` file:
```env
OPENAI_API_KEY=sk-your-actual-key-here
AI_PROVIDER=openai
```

## 💰 **Pricing Comparison**

### **Claude Pricing (Anthropic)**
- **Claude 3 Haiku**: ~$0.25 per million input tokens
- **Very affordable**: Typical conversation costs under $0.01
- **Great value**: Excellent quality for the price

### **OpenAI Pricing**
- **GPT-3.5-turbo**: ~$0.50 per million input tokens
- **GPT-4**: ~$10-30 per million input tokens
- **Variable costs**: Depends on model choice

## 🚀 **Quick Setup Commands**

Once you have your API key, run these commands:

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit the .env file with your API key
# (Use your text editor to add the key)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Start the server
python manage.py runserver
```

## 🔒 **Security Best Practices**

1. **Never commit API keys**: Keep `.env` in your `.gitignore`
2. **Use environment variables**: Never hardcode keys in your code
3. **Set usage limits**: Configure spending limits in your AI provider console
4. **Monitor usage**: Check your usage regularly
5. **Rotate keys**: Generate new keys periodically

## 🆘 **Troubleshooting**

### **"Authentication failed" error:**
- Double-check your API key is correct
- Make sure there are no extra spaces
- Verify your account has billing set up

### **"Rate limit exceeded" error:**
- You're making too many requests
- Wait a few minutes and try again
- Consider upgrading your plan

### **"Insufficient credits" error:**
- Add more funds to your account
- Check your billing settings

## 🎉 **You're Ready!**

Once you've added your API key to the `.env` file and restarted the server, your QaderiChat will be powered by real AI and ready for amazing conversations!

**Test it out with:**
- "Hello! How are you today?"
- "Tell me something interesting about life"
- "What's your favorite type of music?"

Enjoy your new AI-powered social companion! 🤖💬

## 📸 **Customizing the Developer Image**

The developer section currently shows placeholder initials "FQ". To add the actual developer photo:

1. **Save your image** as `static/images/developer.jpg`
2. **Recommended specs**: 400x400px, square format, professional headshot
3. **The image will automatically** replace the placeholder initials
4. **Make sure** the image is optimized for web (under 500KB recommended)

The placeholder will automatically switch to show your actual photo once the image file is added!
