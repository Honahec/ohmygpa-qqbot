from nonebot import get_plugin_config, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.rule import Rule
from nonebot.plugin import PluginMetadata
from .config import Config
from .llm import analyze_and_summarize
from .api import post_to_forum

__plugin_meta__ = PluginMetadata(
    name="论坛同步助手",
    description="自动识别群聊交易/选课信息并同步到论坛",
    usage="自动运行",
    config=Config,
)

plugin_config = get_plugin_config(Config)


def check_group_rule(event: GroupMessageEvent) -> bool:
    if not plugin_config.target_group_ids:
        # allow all
        return True
    return event.group_id in plugin_config.target_group_ids


# Rule to check if message text contains relevant keywords to save token usage
def keyword_check(event: GroupMessageEvent) -> bool:
    text = event.get_plaintext()
    if not plugin_config.sync_keywords:
        return True
    return any(keyword in text for keyword in plugin_config.sync_keywords)


# Matcher
message_syncer = on_message(
    rule=Rule(check_group_rule) & Rule(keyword_check), priority=10, block=False
)


@message_syncer.handle()
async def handle_message(bot: Bot, event: GroupMessageEvent):
    text = event.get_plaintext()
    user_id = event.user_id

    # 1. Analyze with LLM
    summary = await analyze_and_summarize(text, user_id, plugin_config)

    # if summary:
    #     # 2. Upload to Forum
    #     success = await post_to_forum(summary, plugin_config)

    #     if success:
    #         await message_syncer.finish(f"检测到交易/求助信息，已自动同步至论坛！\n摘要：{summary.splitlines()[0]}")
    #     else:
    #         # Silent fail or log
    #         pass

    if summary:
        await message_syncer.finish(f"检测到交易/求助信息，总结为：\n{summary}")
