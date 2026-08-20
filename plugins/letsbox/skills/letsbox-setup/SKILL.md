---
name: letsbox-setup
description: LetsBoxの初回セットアップをご案内します。ログインの確認と、eBayスキルに必要な認証情報（EPSメールとSerpApiキー）の一度きりの登録を、この場で完了させます。
---

# LetsBox 初回セットアップ

## 目的

LetsBoxを使い始めるときの準備を、対話で一度に済ませるスキルです。登録は一度きりで、次回からは何も聞かれません。

## ルール

- 使ってよいのは、プラグインが登録済みのMCPサーバー「letsbox」のツールだけです。
- `https://mcp.letsai.team` への直接アクセス、MCPサーバーの新規登録・設定変更、OAuth認証の代行は禁止します。
- 認証情報（EPSメール・SerpApiキー）は `set_runtime_credentials` に渡す以外の場所（ファイル・ログ・要約）に書き残さないでください。
- 利用者への説明では専門用語を避け、やさしい言葉で案内してください。

## 手順

1. ツール一覧に「letsbox」のツールが見えるか確認する。見えない場合は「Codexを再起動して、新しいスレッドでもう一度お試しください」と案内して終了する。
2. `get_connection_status` を呼び、ログイン中のアカウントを利用者に伝える。
   - 認証エラーの場合は「ターミナルで `codex mcp logout letsbox` → `codex mcp login letsbox` を実行してください。ブラウザが一瞬開いて自動で完了します」と案内して終了する。
3. 応答で認証情報が未登録（`runtime_credentials_configured: false`）の場合:
   - エラー扱いにせず、「初回のみ、EPSアカウントのメールアドレスとSerpApiキーの登録が必要です。2つの値を教えていただければ、この場で登録します（次回からは不要です）」と優しく案内する。
   - 受け取ったら `set_runtime_credentials` を1回呼んで登録する。
   - `get_runtime_credentials_status` で `source: tenant_store` になったことを確認して報告する。
4. 登録済みの場合は「セットアップは完了しています。そのままスキルを実行できます」と伝える。
5. 最後に、利用できるスキル一覧（`list_skills`）を確認して、何ができるかを一言で紹介する。

## キーの差し替え・削除

利用者がキーを変えたい・消したいと言った場合は、`clear_runtime_credentials` → 必要なら `set_runtime_credentials` で再登録する。
