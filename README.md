# MINARY（ミナリー）LP

ミンティーズのメンズ向け美容サービス「MINARY」のランディングページ。
美容初心者の男性が「これなら一回やってみてもいいかも」と思い、公式LINEを押すことをゴールに設計しています。

- 素のHTML / CSS / JavaScript（ビルド不要・外部ライブラリなし）。GitHub Pages 等にそのまま置けます。
- 前身の `~/minteas-menbeauty-lp`（4ケア版）は変更せず残しています。人物写真とデザインの語彙（アイスブルー×チャコール、Manrope）はそこから引き継いでいます。

## ファイル構成

```
index.html          LP本体（SEO・OGP・構造化データ含む）
css/style.css       スタイル（モバイルファースト）
js/main.js          CONFIG（LINE URL・料金）／CTA計測／固定CTA／シェア／reveal
images/             配信用画像（WebP + JPEGフォールバック）、OGP、favicon
scripts/verify.py   公開前チェック（リンク・価格の整合・SEO・禁止表現）
TODO.md             未確定項目の一覧
```

## ローカル確認

```bash
python3 -m http.server 8938 --directory /Users/ijiri/minary-lp
```

→ http://localhost:8938

## 公開前チェック（ビルドの代わり）

```bash
python3 scripts/verify.py
```

LINE URL・価格の不一致、ページ内リンク切れ、画像の欠落、alt漏れ、h1の数、title/description/OGP/canonical、
JSON-LDの構文、禁止表現（「絶対」「モテる」「若返る」「不潔」など）をチェックします。

## LINE URL・料金を変えるとき

1. `js/main.js` 冒頭の `CONFIG` を書き換える（全CTA・全価格表示にJSで反映されます）
2. `python3 scripts/verify.py --sync` を実行し、HTML側の初期値（JS無効時・検索エンジン向け）も揃える
3. 料金を変えた場合は `index.html` の構造化データ（JSON-LD）の `price` も手で直す（verify.py が不一致を検出します）

## 公開

GitHub Pages（`minteas/minary-lp` の main ブランチ直下）で公開しています。

- URL: https://minteas.github.io/minary-lp/
- `git push` すると数分で反映されます。
- 公開URLを変える場合は、`index.html`（canonical / og:url / og:image / JSON-LD / シェアURL）・`robots.txt`・`sitemap.xml` 内の `https://minteas.github.io/minary-lp/` を一括置換してください。

## CTA計測

`data-cta` の付いた要素がクリックされると `dataLayer.push({ event: "cta_click", cta: "<値>", link_url })` を送信します。
GA4（gtag）が導入されていれば `gtag("event", "cta_click", …)` も送信します。GTM/GA4のスニペットは `<head>` の `ANALYTICS` コメント位置に追加してください。

| data-cta | 位置 |
|---|---|
| header-line | ヘッダー（PCのみ） |
| hero-line | ファーストビュー |
| mid-line | 3つの特徴の後（中間CTA） |
| price-trial-line | 料金：初回お試し |
| price-sub-line | 料金：サブスク相談 |
| flow-line | 利用の流れの下 |
| share-line / share-copy | パートナー紹介（LINEで送る／URLコピー・共有） |
| footer-line | 最終CTA |
| sticky-line | スマホ下部固定CTA |

## 構成

midacy.jp（ミダシー）の構成・訴求の流れを参考にしています（文章・イラスト・デザインは独自）。

ファーストビュー（60分リング・75%OFF・CTA）→ 5つのケア → こんなことありませんか？ → MINARYとは＋3つの特徴
→ 特徴01 コスパ（料金比較バー）→ 特徴02 タイパ（通い方の比較）→ 特徴03 迷わない → 中間CTA
→ 料金プラン → 安心の5つのポイント → ご利用の流れ → パートナー紹介 → FAQ → サービス概要 → 最終CTA

実績・口コミ・ビフォーアフター・機器のこだわりなど、確認できていない情報は載せていません。用意できたら追加を検討してください。

## 画像

ページ内は写真を使わず、線画アイコンとCSSで構成しています（施術内容を誤解させないため）。
OGP画像（`images/ogp.jpg`）のみ Pexels の仮写真を使っています。実写真ができたら差し替えてください。
