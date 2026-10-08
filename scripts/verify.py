#!/usr/bin/env python3
"""MINARY LP の公開前チェック（標準ライブラリのみ）。

  python3 scripts/verify.py          # チェックのみ
  python3 scripts/verify.py --sync   # js/main.js の CONFIG に合わせて index.html の LINE URL・価格を書き換える

チェック内容:
  - CONFIG(LINE_URL / PRICES) と index.html の初期値・構造化データが一致しているか
  - ページ内リンク(#id)の飛び先が存在するか / ローカル画像・CSS・JSが存在するか
  - 全imgにalt・width・heightがあるか / h1が1つだけか
  - title・description・canonical・OGP・viewport・favicon があるか
  - 構造化データ(JSON-LD)がパースできるか
  - 禁止表現（誇大・断定・コンプレックスを煽る表現）が含まれていないか
  - 未設定のTODO（公開URLなど）が残っていないか（警告）
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(ROOT, "index.html")
JS_PATH = os.path.join(ROOT, "js", "main.js")

BANNED = ["最先端", "人生が変わる", "絶対", "必ず効果", "モテる", "モテ", "若返", "不潔", "汚い", "老けて", "老け顔", "完全脱毛", "永久脱毛", "治療", "治る"]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_config(js):
    line = re.search(r'LINE_URL:\s*"([^"]+)"', js).group(1)
    prices = {k: int(v) for k, v in re.findall(r"(\w+):\s*(\d+),\s*//", js)}
    return line, prices


def yen(n):
    return f"{n:,}"


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.imgs, self.srcs = set(), [], [], []
        self.line_links, self.prices, self.h1 = [], [], 0
        self.meta, self.links, self.jsonld = {}, [], []
        self._price_key, self._in_jsonld = None, False
        self.text_chunks, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
            if "data-line" in a:
                self.line_links.append(a["href"])
        if tag == "img":
            self.imgs.append(a)
            self.srcs.append(a.get("src", ""))
        if tag == "source" and "srcset" in a:
            self.srcs += [s.strip().split(" ")[0] for s in a["srcset"].split(",")]
        if tag == "link":
            self.links.append(a)
            if a.get("rel") in ("stylesheet", "icon", "apple-touch-icon") and not a["href"].startswith("http"):
                self.srcs.append(a["href"].split("?")[0])
        if tag == "script" and a.get("src"):
            self.srcs.append(a["src"].split("?")[0])
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key] = a.get("content", "")
        if tag == "h1":
            self.h1 += 1
        if "data-price" in a:
            self._price_key = a["data-price"]
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_jsonld = True
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1
            self._in_jsonld = False

    def handle_data(self, data):
        if self._in_jsonld:
            self.jsonld.append(data)
        elif not self._skip:
            self.text_chunks.append(data)
        if self._price_key:
            self.prices.append((self._price_key, data.strip()))
            self._price_key = None


def sync(html, line, prices):
    html = re.sub(r'(<a\b[^>]*?href=")[^"]*("[^>]*\bdata-line\b)', lambda m: m.group(1) + line + m.group(2), html)
    for key, val in prices.items():
        html = re.sub(r'(data-price="%s">)[^<]*(<)' % key, lambda m: m.group(1) + yen(val) + m.group(2), html)
    return html


def main():
    js = read(JS_PATH)
    html = read(HTML_PATH)
    line, prices = load_config(js)

    if "--sync" in sys.argv:
        new = sync(html, line, prices)
        if new != html:
            with open(HTML_PATH, "w", encoding="utf-8") as f:
                f.write(new)
            print("index.html を CONFIG に同期しました。構造化データ(JSON-LD)の price は手動で確認してください。")
        html = new

    p = Collector()
    p.feed(html)
    errors, warnings = [], []

    # CONFIG と HTML の一致
    for href in p.line_links:
        if href != line:
            errors.append(f"LINEリンクがCONFIGと不一致: {href}（--sync で修正可）")
    for key, text in p.prices:
        if key not in prices:
            errors.append(f"未定義の data-price: {key}")
        elif text != yen(prices[key]):
            errors.append(f"価格表示がCONFIGと不一致: {key}={text}（--sync で修正可）")
    if not p.line_links:
        errors.append("data-line のCTAが見つかりません")

    # JSON-LD
    for raw in p.jsonld:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            errors.append(f"JSON-LDのパースに失敗: {e}")
            continue
        ld_prices = {int(x) for x in re.findall(r'"price":\s*"(\d+)"', raw)}
        if ld_prices and ld_prices != set(prices.values()):
            errors.append(f"JSON-LDの価格 {sorted(ld_prices)} がCONFIG {sorted(prices.values())} と不一致")

    # リンク・アセット
    for href in p.hrefs:
        if href.startswith("#") and href[1:] and href[1:] not in p.ids:
            errors.append(f"ページ内リンク切れ: {href}")
    for src in set(p.srcs):
        if src and not src.startswith(("http", "data:")) and not os.path.exists(os.path.join(ROOT, src)):
            errors.append(f"ファイルが存在しません: {src}")
    for img in p.imgs:
        for attr in ("alt", "width", "height"):
            if attr not in img:
                errors.append(f"img に {attr} がありません: {img.get('src')}")
    if p.h1 != 1:
        errors.append(f"h1 は1つにしてください（現在 {p.h1}）")

    # SEO
    for key in ("description", "viewport", "og:title", "og:description", "og:image", "og:url", "twitter:card"):
        if not p.meta.get(key):
            errors.append(f"meta {key} がありません")
    rels = {l.get("rel") for l in p.links}
    for rel in ("canonical", "icon", "apple-touch-icon"):
        if rel not in rels:
            errors.append(f"link rel={rel} がありません")
    if "<title>" not in html:
        errors.append("title がありません")

    # 表現チェック（本文テキストのみ）
    text = "".join(p.text_chunks)
    for word in BANNED:
        if word in text:
            errors.append(f"禁止表現が含まれています: 「{word}」")

    # 公開前TODO
    if "TODO-SITE-URL" in html:
        warnings.append("公開URLが未設定です（canonical / og:url / og:image / JSON-LD の TODO-SITE-URL）")

    print(f"LINE_URL: {line}")
    print("PRICES : " + " / ".join(f"{k}={yen(v)}" for k, v in prices.items()))
    print(f"CTA(data-line): {len(p.line_links)}件 / 画像: {len(p.imgs)}件 / ページ内ID: {len(p.ids)}件")
    for w in warnings:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    if errors:
        sys.exit(1)
    print("OK: エラーはありません")


if __name__ == "__main__":
    main()
