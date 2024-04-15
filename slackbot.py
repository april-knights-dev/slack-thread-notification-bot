# slackbot.py
import settings
from threadstate import ThreadState


class SlackBot:
    def __init__(self, app):
        self.app = app
        self.load_settings()
        self.thread_state = ThreadState("thread_state.json")

    def load_settings(self):
        self.thread_settings = settings.load_thread_settings()

    def save_settings(self):
        settings.save_thread_settings(self.thread_settings)

    def handle_app_mention(self, body, say):
        user = body["event"]["user"]
        channel = body["event"]["channel"]
        say(f"<@{user}> こんにちは！スレッド自動展開の設定は `/thread_settings` コマンドから行ってください。")

    def handle_message(self, body):
        event = body["event"]
        if "thread_ts" in event:
            channel_id = event["channel"]
            thread_ts = event["thread_ts"]

            # 現在のメッセージがチャンネルに投稿されたものかどうかを判断
            if self.is_thread_message_posted_to_channel(event):
                # チャンネルに投稿されたメッセージのタイムスタンプを取得（例として、現在のメッセージのタイムスタンプを使用）
                last_broadcast_ts = event["ts"]
                # カウントをリセットし、最後にチャンネルに投稿されたメッセージのタイムスタンプを更新
                self.thread_state.reset_message_count(thread_ts, last_broadcast_ts)
            else:
                # メッセージ数をインクリメント
                self.thread_state.increment_message_count(thread_ts)

            # 現在のメッセージカウントを取得
            reply_count = self.thread_state.get_message_count(thread_ts)
            if self.is_thread_expandable(channel_id, event, reply_count):
                self.expand_thread(channel_id, thread_ts, reply_count)

    def is_thread_message_posted_to_channel(self, message):
        # メッセージがチャンネルに投稿されたものかどうかを判断
        if message.get("subtype") == "thread_broadcast":
            return True
        return False

    def reset_reply_count(self, channel_id, thread_ts):
        # スレッド内のメッセージを取得
        replies = self.app.client.conversations_replies(
            channel=channel_id, ts=thread_ts)
        # チャンネルに投稿されたメッセージがある場合、そのメッセージ数からカウントを再開する
        count = 0
        for message in replies["messages"]:
            if message.get("parent_user_id") is None:
                # チャンネルに投稿されたメッセージを見つけたらカウントをリセット
                count = 0
            else:
                count += 1
        return count

    def is_thread_expandable(self, channel_id, event, reply_count):
        if "thread_ts" in event and channel_id in self.thread_settings:
            threshold = self.thread_settings[channel_id]["threshold"]
            return self.thread_settings[channel_id]["auto_expand"] and reply_count % threshold == 0
        return False

    def get_thread_reply_count(self, channel_id, thread_ts):
        replies = self.app.client.conversations_replies(
            channel=channel_id, ts=thread_ts)
        return len(replies["messages"]) - 1

    def expand_thread(self, channel_id, thread_ts, reply_count):
        threshold = self.thread_settings[channel_id]["threshold"]
        if reply_count % threshold == 0:
            latest_reply = self.app.client.conversations_replies(
                channel=channel_id, ts=thread_ts)["messages"][-1]
            latest_reply_ts = latest_reply["ts"]
            permalink = self.app.client.chat_getPermalink(
                channel=channel_id, message_ts=latest_reply_ts)["permalink"]
            self.app.client.chat_postMessage(
                channel=channel_id,
                text=f"このスレッドで会話が進んでます。最新のコメントは<{permalink}|こちら>"
            )

    def open_settings_modal(self, client, body):
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "thread_settings_view",
                "title": {"type": "plain_text", "text": "スレッド自動展開の設定"},
                "submit": {"type": "plain_text", "text": "保存"},
                "close": {"type": "plain_text", "text": "キャンセル"},
                "private_metadata": body["channel_id"],
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "auto_expand_block",
                        "element": {
                            "type": "radio_buttons",
                            "options": [
                                {
                                    "text": {"type": "plain_text", "text": "有効"},
                                    "value": "true",
                                },
                                {
                                    "text": {"type": "plain_text", "text": "無効"},
                                    "value": "false",
                                },
                            ],
                            "initial_option": {
                                "text": {"type": "plain_text", "text": "有効" if self.thread_settings.get(body["channel_id"], {}).get("auto_expand", False) else "無効"},
                                "value": "true" if self.thread_settings.get(body["channel_id"], {}).get("auto_expand", False) else "false",
                            },
                            "action_id": "auto_expand_action",
                        },
                        "label": {"type": "plain_text", "text": "スレッド自動展開"},
                    },
                    {
                        "type": "input",
                        "block_id": "threshold_block",
                        "element": {
                            "type": "plain_text_input",
                            "initial_value": str(self.thread_settings.get(body["channel_id"], {}).get("threshold", 10)),
                            "action_id": "threshold_action",
                        },
                        "label": {"type": "plain_text", "text": "自動展開のしきい値"},
                    },
                ],
            },
        )

    def update_thread_settings(self, client, body, view):
        channel_id = body["view"]["private_metadata"]
        auto_expand = view["state"]["values"]["auto_expand_block"]["auto_expand_action"]["selected_option"]["value"] == "true"
        threshold = int(view["state"]["values"]
                        ["threshold_block"]["threshold_action"]["value"])

        self.thread_settings[channel_id] = {
            "auto_expand": auto_expand,
            "threshold": threshold,
        }
        self.save_settings()

        client.chat_postMessage(channel=channel_id, text="スレッド自動展開の設定を更新しました。")
