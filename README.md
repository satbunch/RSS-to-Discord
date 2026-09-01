# rss-to-discord

Feedlyの代わりに、登録したRSSフィードの新着記事をDiscordに自動投稿するスクリプト。
GitHub Actionsが15分おきに各フィードをチェックし、新着があればDiscord Webhookに投稿する。

## セットアップ

1. Discordで通知したいチャンネルの「チャンネルの編集 > 連携サービス > ウェブフック」から
   Webhookを作成し、URLをコピーする。
2. このディレクトリの内容でGitHubリポジトリを作成する（Privateでよい）。
   ```
   cd rss-to-discord
   git init
   git add .
   git commit -m "init"
   git remote add origin <あなたのリポジトリURL>
   git push -u origin main
   ```
3. GitHubリポジトリの Settings > Secrets and variables > Actions で
   `DISCORD_WEBHOOK_URL` という名前のSecretを作成し、1でコピーしたURLを設定する。
4. Settings > Actions > General > Workflow permissions を
   「Read and write permissions」にする（状態ファイルをコミットし直すために必要）。
5. Actions タブから `RSS to Discord` を選び、`Run workflow` で手動実行する。
   - 初回実行では通知は送られず、既存記事を「既読」として記録するだけ（過去記事が
     大量に流れてくるのを防ぐため）。
6. 以降は15分おきに自動実行され、新着記事だけがDiscordに届く。

## フィードの追加・削除

`feeds.txt` に1行1URLで追加/削除して、コミット・pushするだけ。
新しく追加したフィードは次回実行時に初回扱い（既読化のみ）になる。

## 通知間隔・件数を変える

- 実行間隔: `.github/workflows/notify.yml` の `cron` を変更（GitHub Actionsの
  スケジュール実行は数分〜十数分程度の遅延が出ることがある）。
- 1回のチェックで投稿する最大件数: `scripts/rss_to_discord.py` の
  `MAX_ENTRIES_PER_RUN` を変更。
