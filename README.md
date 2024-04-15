# README.md

# スレッド展開通知SlackBot

このSlackBotは、Slack内の複数チャンネルで動作し、スレッドで一定数以上の会話が行われた場合に、そのスレッドをメッセージリストに自動展開し、指定件数ごとに通知します。また、スラッシュコマンドから設定モーダルを呼び出して、チャンネルごとにスレッド自動展開のON/OFFや通知件数のしきい値を設定できます。

## 機能

- 複数のSlackチャンネルで動作可能
- 各チャンネルごとに、スレッド内で指定件数（デフォルト10件）以上の会話が発生した場合、そのスレッドをメッセージリストに自動で展開
- 展開後、そのスレッド内でさらに指定件数の新しい会話が追加されるごとに通知
- ただし、展開されたスレッド内に「以下にも投稿する」機能で投稿されたコメントが含まれる場合、そこから指定件数ごとにカウントをリセット
- スラッシュコマンド `/thread_settings` で設定モーダルを呼び出し可能
- 設定モーダルでは、チャンネルごとにスレッド自動展開のON/OFFと通知件数のしきい値を設定可能

## 必要環境

- Python 3.6以上
- SlackアプリとBotユーザートークン、SocketModeトークン

## インストール方法

1. このリポジトリをクローンします。

   ```
   git clone https://github.com/youraccount/slack-thread-notification-bot.git
   ```

2. 必要なPythonパッケージをインストールします。

   ```
   cd slack-thread-notification-bot
   pip install -r requirements.txt
   ```

3. プロジェクトのルートディレクトリに`.env`ファイルを作成し、`SLACK_BOT_TOKEN`と`SLACK_APP_TOKEN`を設定します。

   ```
   # .env
   SLACK_BOT_TOKEN=<your_bot_token>
   SLACK_APP_TOKEN=<your_app_token>
   ```

4. Botを起動します。

   ```
   python main.py
   ```

## 設定

- スラッシュコマンド `/thread_settings` から設定モーダルを呼び出します。
- 設定モーダルでは、以下の項目を設定できます。
  - スレッド自動展開: ON/OFF
  - 自動展開のしきい値: 整数値（デフォルト: 10）
- 設定はチャンネルごとに保存され、各チャンネルで個別の設定が可能です。

## ファイル構成

- `main.py`: メインのプログラムファイル。Slackイベントのリスニングとハンドリングを行います。
- `slackbot.py`: SlackBot関連の処理を記述。スレッドの自動展開や設定モーダルの表示などを担当します。
- `settings.py`: 設定関連の処理を記述。チャンネルの設定を読み込み、保存します。
- `config.py`: 環境変数を読み込むためのファイル。Slackのトークン情報を管理します。
- `threadstate.py`: スレッドの状態（メッセージ数、最後にチャンネルに投稿されたメッセージのタイムスタンプ）を管理するためのファイル。スレッドの状態をJSONファイルに保存し、読み込みます。
- requirements.txt: 必要なPythonライブラリを記述
- README.md: プロジェクトの説明や使用方法などを記述

## 注意事項

- このBotはSlackのSocket Modeを使用しています。そのため、Slack APIの設定でSocket Modeを有効にし、適切なトークンを取得する必要があります。
- `.env` ファイルに設定するトークンは、Slack APIから取得したものを使用してください。
- スレッドの自動展開機能は、チャンネル内の全てのメンバーに影響します。設定を変更する際は、チャンネルのメンバーと相談の上、適切に行ってください。

## ライセンス

This project is licensed under the MIT License - see the LICENSE file for details.
