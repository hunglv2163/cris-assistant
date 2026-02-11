# Telegram Assistant Bot

This bot joins your Telegram groups, listens to messages, and provides a daily summary report using OpenAI.

## Features
- **Message Logging**: Automatically saves all messages in the group to a local database.
- **/reminder**: Sends a reminder to the group to post updates.
- **/report**: Generates a summary of the day's conversation using an LLM.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**:
   The `.env` file is already created with your Telegram Bot Token.
   **Important**: You must add your OpenAI API Key to the `.env` file for the summary feature to work.
   
   Open `.env` and edit:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **Run the Bot**:
   ```bash
   python bot.py
   ```

## Usage
1. Add the bot to your Telegram group (Sales, Marketing, etc.).
2. Make sure to give the bot **Admin rights** or disable **Group Privacy** in BotFather so it can read all messages (otherwise it only sees commands and replies to it).
   - Go to @BotFather -> /mybots -> Select Bot -> Bot Settings -> Group Privacy -> Turn off.
3. Use `/reminder` to remind users.
4. Use `/report` to get a summary of the day.
