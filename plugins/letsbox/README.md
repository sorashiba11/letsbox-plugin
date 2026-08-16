# Lets Box plugin

Lets Boxの契約中ワークフローを、1つのOAuth接続から利用するCodexプラグインです。個別のスキルフォルダは顧客PCへ配置しません。

## URLからの導入

```bash
codex plugin marketplace add https://github.com/sorashiba11/letsbox-plugin
codex plugin add letsbox@letsbox
```

導入後は新しいCodexタスクを開始し、表示されたLets Box OAuthを完了します。OpenAI Marketplaceの公開審査前でも、このGitHub URLを知っている利用者へ直接配布できます。

## 境界

- MCPは認証、権限、カタログ、ワークフロー状態、最小限の履歴を扱います。
- 顧客APIキーはLets Box MCPへ送信しません。
- `local_only`の成果物は顧客端末だけへ保存します。
- 現時点のRemote本番対応はeBay利益リサーチです。ほかのカードは共通Local Capability Brokerの移行完了まで`legacy_fallback`として明示し、MCPが実行済みを装うことはありません。

Webカタログと導入案内: <https://app.letsai.team>
