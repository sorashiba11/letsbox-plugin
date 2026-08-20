---
name: letsbox-switch-account
description: LetsBoxのアカウントを切り替えます。いまのアカウントを確認し、ログアウト→別アカウントでのログインまでを手順どおりにご案内して、切り替わったことを確認します。
---

# LetsBox アカウント切り替え

## 目的

「別のLetsBoxアカウントで使いたい」「間違ったアカウントでログインしてしまった」ときに、切り替えを最後まで見届けるスキルです。

## ルール

- 使ってよいのは、プラグインが登録済みのMCPサーバー「letsbox」のツールだけです。
- `https://mcp.letsai.team` への直接アクセス、MCPサーバーの新規登録・設定変更、OAuth認証の代行は禁止します。パスワードを聞き取ることも禁止です（入力は必ず利用者本人がブラウザで行う）。
- 利用者への説明では専門用語を避け、やさしい言葉で案内してください。

## 重要な背景（エージェント向け）

`codex mcp logout letsbox` だけではブラウザ側のセッションが2層（mcp.letsai.team と auth.letsai.team）残るため、再ログインすると**同じアカウントで自動的に認証されてしまう**。切り替えには、先に https://mcp.letsai.team/logout を開くこと（両層を一度に消すワンストップURL）が必須。auth.letsai.team/logout だけでは不十分。

## 手順

1. `get_connection_status` を呼び、「現在は ○○@…（会社名）のアカウントです」と伝えたうえで、切り替えでよいか確認する。
2. 利用者に次の2ステップを案内し、完了の返事を待つ:
   - 「①ブラウザで https://mcp.letsai.team/logout を開いてください。『ログアウトしました』と表示されたらOKです（このURLは接続用とログイン用の2つのセッションを一度に消します）」
   - 「②ターミナルで `codex mcp logout letsbox` を実行してください」
3. 続けて「③ターミナルで `codex mcp login letsbox` を実行すると、ブラウザにログイン画面が開きます。**切り替え先のアカウント**でログインしてください」と案内し、完了の返事を待つ。
   - ログインが issuer エラーで失敗する場合:「`npm install -g @openai/codex@latest` でCodexを更新してから、もう一度お試しください」
4. 完了の返事が来たら `get_connection_status` を呼び直し、`account_email` が切り替わったことを確認して「○○@… に切り替わりました」と報告する。
   - 切り替わっていない場合は、手順2の①が古いURL（auth側のみ）だった可能性が高い。責めずに https://mcp.letsai.team/logout からやり直しを案内する。
5. 切り替え先のアカウントでeBayスキルを使う場合、認証情報（EPSメール/SerpApiキー)はアカウントごとに別管理。未登録なら letsbox-setup の手順で登録を案内する。
