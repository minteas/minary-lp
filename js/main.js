/* ==========================================================================
   MINARY — main.js
   ・CONFIG の一元管理（LINE URL / 料金）
   ・CTAクリック計測（dataLayer）
   ・スマホ固定CTAの表示制御 / 紹介用シェア / 控えめなreveal
   ========================================================================== */
(function () {
  "use strict";

  /* ---------------------------------------------------------------------
   * CONFIG: ここを書き換えるとページ内の全CTA・全価格表示に反映されます。
   * HTML側にも同じ値を初期値（JS無効時・検索エンジン向け）として記載しているため、
   * 変更後は `python3 scripts/verify.py --sync` を実行してHTMLも揃えてください。
   * ------------------------------------------------------------------- */
  var CONFIG = {
    // TODO(LINE_URL): 現在はミンティーズ公式LINE。MINARY専用アカウントができたら差し替え
    LINE_URL: "https://line.me/ti/p/@luy1644d",
    PRICES: {
      regular: 22000, // 通常価格（5つのケアを単発で受けた場合・税込）
      trial: 5500, // 初回お試し（税込）
      subscription: 11000, // サブスク月額（税込）
    },
  };

  function formatYen(n) {
    return Number(n).toLocaleString("ja-JP");
  }

  function applyConfig() {
    document.querySelectorAll("a[data-line]").forEach(function (a) {
      a.href = CONFIG.LINE_URL;
    });
    document.querySelectorAll("[data-price]").forEach(function (el) {
      var key = el.getAttribute("data-price");
      if (CONFIG.PRICES[key] != null) el.textContent = formatYen(CONFIG.PRICES[key]);
    });
  }

  function pushDataLayer(payload) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(payload);
  }

  // data-cta の付いた要素のクリックを計測（GA4/GTM導入後はトリガー「cta_click」で拾える）
  function wireCtaTracking() {
    document.addEventListener("click", function (e) {
      var el = e.target.closest("[data-cta]");
      if (!el) return;
      var payload = { event: "cta_click", cta: el.getAttribute("data-cta"), link_url: el.href || "" };
      pushDataLayer(payload);
      if (typeof window.gtag === "function") {
        window.gtag("event", "cta_click", { cta: payload.cta, link_url: payload.link_url });
      }
    });
  }

  function wireHeader() {
    var header = document.querySelector(".header");
    if (!header) return;
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 4);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // ヒーローのCTAが見えている間・最終CTAが見えている間は固定CTAを隠す
  function wireStickyCta() {
    var sticky = document.getElementById("sticky-cta");
    var hero = document.querySelector(".hero__actions");
    var final = document.getElementById("final");
    if (!sticky || !hero || !final || !("IntersectionObserver" in window)) {
      if (sticky) setSticky(sticky, true);
      return;
    }
    var state = { hero: true, final: false };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.target === hero) state.hero = entry.isIntersecting || entry.boundingClientRect.top > 0;
        if (entry.target === final) state.final = entry.isIntersecting;
      });
      setSticky(sticky, !state.hero && !state.final);
    });
    io.observe(hero);
    io.observe(final);
  }

  function setSticky(sticky, visible) {
    sticky.classList.toggle("is-visible", visible);
    sticky.setAttribute("aria-hidden", visible ? "false" : "true");
    var link = sticky.querySelector("a");
    if (link) link.tabIndex = visible ? 0 : -1;
  }

  function shareUrl() {
    var canonical = document.querySelector('link[rel="canonical"]');
    var href = canonical && canonical.href;
    // 公開URLが未設定（TODO）の間は、表示中のURLをそのまま使う
    if (!href || /todo-site-url/i.test(href)) href = location.href.split("#")[0];
    return href;
  }

  function wireShare() {
    var url = shareUrl();
    var lineBtn = document.getElementById("share-line");
    var copyBtn = document.getElementById("share-copy");
    var status = document.getElementById("share-status");
    var text = "60分で5つの美容ケアがまとめて受けられるみたい。初回5,500円だって。";

    if (lineBtn) {
      lineBtn.href = "https://social-plugins.line.me/lineit/share?url=" + encodeURIComponent(url);
    }
    if (!copyBtn) return;

    // スマホでは端末の共有メニューを優先
    if (navigator.share) copyBtn.textContent = "このページを共有する";

    copyBtn.addEventListener("click", function () {
      if (navigator.share) {
        navigator.share({ title: document.title, text: text, url: url }).catch(function () {});
        return;
      }
      copyText(url).then(
        function () { status.textContent = "URLをコピーしました。LINEやメールに貼り付けて送れます。"; },
        function () { status.textContent = "コピーできませんでした。お手数ですがアドレスバーのURLをコピーしてください。"; }
      );
    });
  }

  function copyText(value) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(value);
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = value;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      ok ? resolve() : reject();
    });
  }

  function wireReveal() {
    var targets = document.querySelectorAll(".reveal");
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || !("IntersectionObserver" in window)) {
      targets.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }
    // JSが動いたときだけ非表示→フェードインにする（JSが読めなくても本文は必ず表示される）
    document.documentElement.classList.add("js");
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px" }
    );
    targets.forEach(function (el) { io.observe(el); });
  }

  applyConfig();
  wireCtaTracking();
  wireHeader();
  wireStickyCta();
  wireShare();
  wireReveal();
})();
