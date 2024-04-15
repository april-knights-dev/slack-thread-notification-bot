# settings.py
import json
import re

from slack_sdk import WebClient

from config import SLACK_BOT_TOKEN

client = WebClient(token=SLACK_BOT_TOKEN)


def load_thread_settings():
    thread_settings = {}
    try:
        # ページネーションを処理するためのカーソル初期化
        next_cursor = ""
        while True:
            response = client.conversations_list(
                types="public_channel,private_channel",
                cursor=next_cursor
            )
            channels = response["channels"]
            next_cursor = response["response_metadata"]["next_cursor"]

            pattern = r'\{.*?"auto_expand".*?:.*?,.*?"threshold".*?:.*?\}'
            for channel in channels:
                channel_id = channel["id"]
                try:
                    topic_value = channel.get("topic", {}).get("value", "")
                    match = re.search(pattern, topic_value)
                    if match:
                        settings = json.loads(match.group())
                        if "auto_expand" in settings and "threshold" in settings:
                            thread_settings[channel_id] = settings
                except (KeyError, json.JSONDecodeError) as e:
                    print(
                        f"Error parsing settings for channel {channel_id}: {e}")

            # カーソルが空の場合、すべてのページを取得したことを意味する
            if not next_cursor:
                break
    except Exception as e:
        print(f"Error retrieving channel list: {e}")

    return thread_settings


def save_thread_settings(thread_settings):
    for channel_id, settings in thread_settings.items():
        # 既存のトピックを取得
        existing_topic = client.conversations_info(channel=channel_id)[
            "channel"]["topic"]["value"]

        # 既存のトピックからJSON形式の設定部分を探して取り除く
        # JSON形式の設定部分を識別するための正規表現パターン
        pattern = r'\{.*?"auto_expand".*?:.*?,.*?"threshold".*?:.*?\}'
        existing_topic = re.sub(pattern, '', existing_topic).strip()

        # 新しい設定をJSON形式で追加
        new_topic = f"{existing_topic} {json.dumps(settings)}".strip(
        ) if existing_topic else json.dumps(settings)

        # トピックを更新
        client.conversations_setTopic(channel=channel_id, topic=new_topic)