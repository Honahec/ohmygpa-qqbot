from datetime import datetime
from nonebot.log import logger
from openai import AsyncOpenAI
from .config import Config


async def analyze_and_summarize(
    text: str, user_id: int | str, config: Config
) -> str | None:
    """
    Analyzes the text using API.
    Returns a summarized forum post content if relevant, or None if irrelevant.
    """
    if not config.api_key or config.api_key == "YOUR_API_KEY":
        logger.warning(f" API Key is not set or invalid: {config.api_key[:5]}...")
        return None

    logger.info(
        f"Starting analysis for text: {text[:20]}... using model {config.model}"
    )

    current_date = datetime.now().strftime("%Y年%m月%d日")

    system_prompt = (
        f"你是一个论坛助手。当前日期是：{current_date}。\n"
        "你的任务是分析群聊消息，判断是否包含'二手交易'或'求课/换课'等需求信息。\n"
        "注意：不是所有疑问都符合要求，只有明确的交易或换课请求才算。\n"
        "如果消息不包含此类信息，请直接回复 'FALSE'。\n"
        "如果包含，请将其改写为一篇简洁明了的论坛帖子格式。\n"
        "包含标题（Title）和正文（Body）。 Markdown格式。\n"
        "请根据当前日期处理'今年'、'明年'、'今天'等时间描述。\n"
        f"发布者的 QQ 号是：{user_id}，请将其填入联系方式中，例如 QQ: {user_id}。\n\n"
        "例如：\n"
        "# [出售] 99新 Macbook Pro \n"
        "价格：5000元 \n"
        f"联系方式：QQ {user_id} \n"
        "详细描述：..."
    )

    try:
        base = config.base_url.rstrip("/")
        if base.endswith("/chat/completions"):
            base = base[:-17]  # remove /chat/completions

        client = AsyncOpenAI(api_key=config.api_key, base_url=base)

        response = await client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"分析这条消息：{text}"},
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content
        if not content:
            return None

        content = content.strip()

        if content == "FALSE":
            return None

        return content

    except Exception as e:
        import traceback

        logger.error(f"Error calling LLM: {repr(e)}")
        logger.error(traceback.format_exc())
        return None
