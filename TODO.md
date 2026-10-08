# TODO（未確定項目）

| # | 項目 | 現状 | 変更箇所 |
|---|---|---|---|
| 1 | MINARY専用のLINE URL | ミンティーズ公式LINE（`https://line.me/ti/p/@luy1644d`、gym.mintea.jp に掲載されているもの）を暫定使用 | `js/main.js` の `CONFIG.LINE_URL` → `python3 scripts/verify.py --sync` |
| 2 | 公開URL（ドメイン・パス） | `https://TODO-SITE-URL.example/` | `index.html` を一括置換（README参照） |
| 3 | FAQ「男性スタッフですか？」の回答 | 「LINEでお問い合わせください」と記載 | `index.html` の `TODO(STAFF)` コメント箇所。確定したら構造化データ(FAQPage)にも追加 |
| 4 | 提供場所 | 「愛知県安城市（パーソナルジム ミンティーズ）」と記載。ミンティーズ店内で提供される前提 | `index.html` の `TODO(ADDRESS)`。住所（三河安城南町1-20-4）を出すかどうかも判断 |
| 5 | 営業時間・定休日 | 未記載（「LINEで空き状況を確認」に誘導） | サービス概要に「営業時間」行を追加 |
| 6 | サブスクプランの内容（月何回か・最低契約期間など） | 「5つのケアを続けやすい月額制」とだけ記載 | 料金セクションの `.plan__points` |
| 7 | 各ケアの施術方法（脱毛方式・ホワイトニングの種類など） | 一般的な説明のみ | ケア紹介カード・FAQ |
| 8 | 実写真（店舗・施術風景） | Pexelsの仮画像（人物1枚） | `images/` と `index.html` の `<picture>` |
| 9 | GA4 / GTM | 未導入（dataLayer への送信は実装済み） | `index.html` の `ANALYTICS` コメント位置 |
| 10 | 正式ロゴ | テキストロゴ＋仮のfavicon | `images/favicon.svg` / `apple-touch-icon.png` |
