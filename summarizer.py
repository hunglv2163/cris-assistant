import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def summarize_messages(messages, group_type="default"):
    """
    messages: list of tuples (username, content, timestamp)
    group_type: 'default' (or 'mkt'), 'bd'
    """
    if not messages:
        return "No messages to summarize today."
    
    # Check if API key is present
    if not os.getenv("OPENAI_API_KEY"):
        return "⚠️ OpenAI API Key is missing. Please set OPENAI_API_KEY in .env file to enable summarization.\n\nHere are the raw messages count: " + str(len(messages))

    conversation_text = ""
    for username, content, timestamp in messages:
        conversation_text += f"[{timestamp}] {username}: {content}\n"

    print(f"DEBUG: Input text to OpenAI ({len(conversation_text)} chars):\n{conversation_text}...")

    # Define format instructions based on group_type
    format_instruction = ""
    if group_type == 'bd':
        format_instruction = """
        - Format per user (STRICTLY FOR BD GROUP):
          <b>@Username</b>:
          - ✅ <b>Đã làm</b>: [Tóm tắt ngắn gọn các việc đã xong]
          - ⚠️ <b>Vướng mắc</b>: [Nếu có, không có thì bỏ qua dòng này]
          (DO NOT include 'Hôm nay' / 'Today's Plan' section for this group)
        """
    else:
        format_instruction = """
        - Format per user:
          <b>@Username</b>:
          - ✅ <b>Đã làm</b>: [Tóm tắt ngắn gọn các việc đã xong]
          - 📅 <b>Hôm nay</b>: [Tóm tắt ngắn gọn các việc sẽ làm]
          - ⚠️ <b>Vướng mắc</b>: [Nếu có, không có thì bỏ qua dòng này]
        """

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini", # or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a professional secretary. Your task is to **summarize and translate** daily work reports from a Telegram group into **concise Vietnamese**. "
                 "Even if users report in English, you MUST output the final summary in **Vietnamese**. "
                 "\n\nOBJECTIVE:\n"
                 "- Condense long lists of tasks into short, actionable summaries.\n"
                 "- Do NOT copy-paste the original English text. Translate and summarize.\n"
                 "- Focus on: What was done yesterday/completed, What is the plan for today, and Any blockers.\n"
                 "- Group related tasks (e.g., instead of listing 5 sub-tasks for 'Newsletter', just say 'Làm newsletter (nghiên cứu, lên lịch)').\n"
                 "\n\nCRITICAL FILTERS (STRICTLY ENFORCE):\n"
                 "1. REMOVE all casual chit-chat, jokes, teasing, and social banter.\n"
                 "2. REMOVE all comments about personal appearance, vanity, or flirting.\n"
                 "3. REMOVE all insults, vulgarity, and rude language.\n"
                 "4. REMOVE all meta-comments abusing or mocking the bot.\n"
                 "5. ONLY include conflicts if they are professional disagreements about work strategy.\n"
                 "\nEnsure that legitimate work reports from EVERY user are included."
                 "\nSTYLE GUIDELINES:\n"
                 "- Start directly with the report content. Do NOT use introductory headings.\n"
                 "- ALWAYS use usernames with '@' prefix (e.g., '@HoangTrang233').\n"
                 + format_instruction +
                 "\n- At the END of the report, add a new section called '📝 <b>Summary Conversation</b>':\n"
                 "  - Summarize work-related discussions, ideas, or feedback exchanged in the group (excluding the daily reports).\n"
                 "  - **Crucial**: You MUST attribute key points to specific users (e.g., '@UserA nói về vấn đề X', '@UserB đề xuất giải pháp Y').\n"
                 "  - Keep sentences short and concise.\n"
                 "  - Output in Vietnamese.\n"
                 "  - If absolutely no discussion occurred, omit this section.\n"
                 "\nIMPORTANT: Telegram HTML formatting is VERY STRICT. \n"
                 "- Allowed tags: <b>, <i>, <u>, <a>, <code>, <pre>.\n"
                 "- FORBIDDEN tags: <p>, <ul>, <ol>, <li>, <br>, <div>, <span>, <h1>..<h6>.\n"
                 "- Use newlines for paragraphs.\n"
                 "- Use hyphens (-) or emojis for bullet points.\n"
                 "- Do NOT use Markdown (like **bold**). Only use the allowed HTML tags."},
                {"role": "user", "content": conversation_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {str(e)}"
