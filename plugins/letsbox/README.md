# Lets Box plugin

Lets Boxの契約中ワークフローを、1つのOAuth接続から利用するCodexプラグインです。顧客が個別のローカルスキルフォルダを管理する必要はありません。eBay ResearchとRestockは同じRemote MCP、同じ判定ミッション、同じEPS書込ゲートを利用します。

## URLからの導入

```bash
codex plugin marketplace add https://github.com/sorashiba11/letsbox-plugin
codex plugin add letsbox@letsbox
```

Restockを使う前に一度だけ、顧客Macのローカル永続設定へEPSメールとSerpApiキーを保存します。入力値は表示されません。未設定でもLets Boxへの接続と既存Researchは起動できますが、`start_restock`は資格情報不足として閉じます。

```bash
python3 scripts/configure_credentials.py
```

保存先は`$CODEX_HOME/plugin-data/letsbox/credentials.json`（未設定時は`~/.codex/plugin-data/letsbox/credentials.json`）で、ファイルは`0600`、親ディレクトリは`0700`です。プラグイン更新では削除されず、GitやサーバーDBには入りません。その後、新しいCodexタスクを開始してLets Box OAuthを完了します。

## Remoteリサーチの起動

Codexでは、次のようにLets Plugin内のRemote専用スキルを明示して起動します。`@`はChatGPT用で、Codexのスキル指定には`$`を使います。

```text
$letsbox:run-ebay-profit-research Lets PluginのRemote MCP版でeBay利益リサーチを最後まで実行して。ローカル版は使用しないで。
```

件数を指定しなければ15件です。1〜15件の範囲で明示した場合は、その件数を優先します。

## Remote在庫戻しの起動

```text
$letsbox:run-ebay-restock Lets PluginのRemote MCP版でeBay在庫戻しを最後まで実行して。readモードと最安値更新は使用しないで。
```

Restockの開始ツールにはreadモードがありません。アクティブ出品と登録仕入先URLの在庫状態から全URL売り切れの商品だけをOOSとして選び、Researchと同じ仕入先探索・画像判定・競合判定・利益計算を使います。復活対象はサーバー側で事前アーカイブを残した後、EPS仕入先登録、Restockが決めた価格、数量1の順で処理します。未確定商品は書き込まず、出品削除と単独の最安値更新は行いません。

## 境界

- MCPは認証、権限、カタログ、ワークフロー状態、最小限の履歴を扱います。
- EPSメールとSerpApiキーはローカルブリッジが実行時ヘッダーとしてHTTPS送信します。ツール引数、OAuth情報、サーバーDBには保存しません。Workflowへ渡す必要がある間だけ暗号化された封筒を使い、平文を永続化しません。
- `local_only`の成果物は顧客端末だけへ保存します。
- 現時点のRemote本番対応はeBay利益リサーチとeBay在庫戻しです。ほかのカードは共通Local Capability Brokerの移行完了まで`legacy_fallback`として明示し、MCPが実行済みを装うことはありません。

Webカタログと導入案内: <https://app.letsai.team>
