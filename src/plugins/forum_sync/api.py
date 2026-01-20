import httpx
from nonebot.log import logger
from .config import Config


async def post_to_forum(content: str, config: Config) -> bool:
    """
    Posts the summarized content to the forum.
    """
    if not config.forum_api_url:
        logger.warning("Forum API URL not set.")
        return False

    # Simple logic to split title and body if needed, assuming the LLM output Markdown with a # Header
    title = "群聊同步信息"
    body = content

    first_line = content.split("\n")[0]
    if first_line.startswith("# "):
        title = first_line.replace("# ", "").strip()
        body = "\n".join(content.split("\n")[1:]).strip()

    payload = {
        "title": title,
        "content": body,
        "category": "marketplace",  # Example category
    }

    headers = {"Authorization": f"Bearer {config.forum_api_token}"}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                config.forum_api_url, json=payload, headers=headers
            )
            if resp.status_code in [200, 201]:
                logger.success(f"Successfully posted to forum: {title}")
                return True
            else:
                logger.error(f"Forum API Error: {resp.status_code} {resp.text}")
                return False
    except Exception as e:
        logger.error(f"Error posting to forum: {e}")
        return False
