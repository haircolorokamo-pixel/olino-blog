#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
olino 新サイト ビルドスクリプト
_extracted.json の記事データ + STAFF 情報から、静的HTMLサイト一式を生成する。
GitHub Pages にそのまま置けば動く(ビルドツール不要・全部素のHTML)。
"""
import json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://haircolorokamo-pixel.github.io/olino-blog"

with open(os.path.join(ROOT, "_extracted.json"), encoding="utf-8") as f:
    POSTS = json.load(f)

STAFF = {
    "takasu": {
        "dir": "takasu",
        "name": "高巣直哉",
        "name_en": "Takasu Naoya",
        "role_label": "店長",
        "role_detail": "ハイトーン・メンズカット・パーマ特化",
        "monogram": "直",
        "bio": "店長をやっています。休日はライブやフェス巡りが趣味です。ハイトーンからナチュラルなグラデーションカラーまで、外国人風カラーを中心に担当しています。メンズカット・パーマも得意なので、気になる方は気軽に相談してください。骨格や肌色、なりたいイメージをしっかり聞いてから決めています。",
        "instagram": "https://www.instagram.com/tikesuu/",
        "hotpepper": "https://beauty.hotpepper.jp/slnH000505333/",
        "portrait_tag": "店長",
        "post_slug": "2026-09-03-ash-beige-hightone",
        "post_img": "takasu-post1.jpg",
        "meta_desc": "大阪市東住吉区・南田辺の美容室olino店長、高巣直哉のスタイリストページ。ハイトーンカラー・メンズカット・パーマを得意とし、外国人風カラーのご提案が得意です。",
    },
    "kaori": {
        "dir": "kaori",
        "name": "KAORI",
        "name_en": "Kaori",
        "role_label": "スタイリスト",
        "role_detail": "縮毛矯正・髪質改善特化",
        "monogram": "華",
        "bio": "縮毛矯正・髪質改善を専門にしています。くせやうねり、広がりに悩んでいる方は、一度相談してください。薬剤の選定からアイロンの温度まで、髪の状態を見ながらその都度調整しています。扱いやすくてまとまる髪、一緒に目指しましょう。",
        "instagram": "https://www.instagram.com/kaori___11o1/",
        "hotpepper": "https://beauty.hotpepper.jp/slnH000505333/",
        "portrait_tag": "スタイリスト",
        "post_slug": "2026-09-03-hair-quality-treatment",
        "post_img": "kaori-post1.jpg",
        "meta_desc": "大阪市東住吉区・南田辺の美容室olinoスタイリスト、KAORIのページ。縮毛矯正・髪質改善が専門で、くせ毛やうねりのお悩みに合わせた施術を得意としています。",
    },
    "sasara": {
        "dir": "sasara",
        "name": "SASARA",
        "name_en": "Sasara",
        "role_label": "美容師",
        "role_detail": "ヘアアレンジ・カラー特化",
        "monogram": "紗",
        "bio": "ヘアアレンジとカラーを担当しています。丁寧な仕上がりを意識しながら、毎日練習を重ねています。お出かけ前や特別な日のヘアアレンジも、気軽に相談してください。",
        "instagram": "https://www.instagram.com/olino_sasa/",
        "hotpepper": "https://beauty.hotpepper.jp/slnH000505333/",
        "portrait_tag": "美容師",
        "post_slug": "2026-09-02-navy-blue-color",
        "post_img": "sasara-post1.jpg",
        "meta_desc": "大阪市東住吉区・南田辺の美容室olino美容師、SASARAのページ。ヘアアレンジとトレンドカラーが得意で、南田辺・東住吉区エリアでカラーを楽しみたい方におすすめです。",
    },
}

NAV_LINKS = [("スタイリスト", "#staff"), ("店舗情報", "#store"), ("ブログ", "#blog")]

STORE_SECTION_TMPL = """
<section class="wrap reveal" id="store">
  <div class="section-head">
    <span class="eyebrow">STORE INFO</span>
    <h2>ハイトーン・縮毛矯正・髪質改善専門 olino</h2>
    <p>大阪市東住吉区、南田辺・西田辺エリアの美容室。ハイトーンカラーと縮毛矯正・髪質改善を軸に、一人ひとりの髪質に合わせた施術をご提案しています。</p>
  </div>

  <div class="store-gallery">
    <figure class="store-photo store-photo-wide">
      <img src="{img_prefix}assets/img/store-exterior.jpg" alt="olino 店舗外観(大阪市東住吉区南田辺)" loading="lazy" width="1600" height="1200">
    </figure>
    <figure class="store-photo">
      <img src="{img_prefix}assets/img/store-interior.jpg" alt="olino 店内の様子" loading="lazy" width="1400" height="1050">
    </figure>
  </div>

  <div class="store-grid">
    <div class="card">
      <h3>ACCESS &amp; CONTACT</h3>
      <dl>
        <div class="info-row"><dt>店名</dt><dd>olino(オリノ)</dd></div>
        <div class="info-row"><dt>住所</dt><dd>〒546-0033<br>大阪府大阪市東住吉区南田辺1-10-39 1階</dd></div>
        <div class="info-row"><dt>電話</dt><dd><a href="tel:0666249860">06-6624-9860</a></dd></div>
        <div class="info-row"><dt>アクセス</dt><dd>大阪メトロ御堂筋線 西田辺駅 / JR阪和線 南田辺駅</dd></div>
      </dl>
    </div>

    <div class="card">
      <h3>OPENING HOURS</h3>
      <table class="hours">
        <tr><td>火・金・土</td><td>9:00 - 22:00</td></tr>
        <tr><td>水・木・日</td><td>9:00 - 18:00</td></tr>
        <tr><td>月曜日</td><td class="closed">定休日</td></tr>
        <tr><td>第3火曜日</td><td class="closed">定休日</td></tr>
      </table>
      <p class="note">※ 火曜日は第3週のみお休みです。ご予約はInstagramのプロフィールリンクより承っています。</p>
    </div>
  </div>
</section>
""".strip("\n")


def store_section(img_prefix):
    return STORE_SECTION_TMPL.format(img_prefix=img_prefix)


def nav_html(index_href, img_prefix, brand_suffix="", anchor_prefix=""):
    links = "\n      ".join(f'<a href="{anchor_prefix}{href}">{label}</a>' for label, href in NAV_LINKS)
    suffix_html = f"<span>— {brand_suffix}</span>" if brand_suffix else ""
    return f"""<nav class="nav">
  <div class="nav-row">
    <a class="brand" href="{index_href}"><img class="brand-logo" src="{img_prefix}assets/img/logo.png" alt="olino">{suffix_html}</a>
    <div class="nav-links">
      {links}
    </div>
    <a class="nav-cta" href="{{instagram}}" target="_blank" rel="noopener">Instagramで予約</a>
  </div>
</nav>"""


def footer_html(person_line):
    return f"""<footer>
  <div class="wrap foot-row">
    <span>&copy; olino — 大阪市東住吉区南田辺1-10-39</span>
    <span>{person_line}</span>
  </div>
</footer>"""


def page_shell(*, title, description, canonical, body, extra_head="", img_prefix=""):
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/png" href="{img_prefix}assets/img/logo.png">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/assets/img/store-exterior.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;700;800&family=Zen+Kaku+Gothic+New:wght@400;500;700;900&display=swap" rel="stylesheet">
{extra_head}</head>
<body>
{body}
</body>
</html>
"""


def build_staff_index(key, s):
    nav = nav_html("../index.html", "../", s["name"]).replace("{instagram}", s["instagram"])

    other_posts_html = f"""
        <a class="post-card" href="posts/{s['post_slug']}.html">
          <div class="thumb"><img src="../assets/img/{s['post_img']}" alt="{POSTS[key]['title']}" loading="lazy" width="800" height="1000"></div>
          <div class="card-body">
            <div class="post-meta"><span class="post-date">{POSTS[key]['date']}</span><span class="post-tag">{POSTS[key]['tag']}</span></div>
            <h3>{POSTS[key]['title']}</h3>
            <p class="excerpt">{POSTS[key]['excerpt']}</p>
            <span class="read-more">続きを読む →</span>
          </div>
        </a>
    """.strip("\n")

    body = f"""{nav}

<div id="top"></div>

<header class="wrap hero" id="staff">
  <div>
    <span class="eyebrow">OLINO STYLIST</span>
    <h1 class="name">{s['name']}</h1>
    <p class="role">{s['role_label']} / <span>{s['role_detail']}</span></p>
    <p class="bio">{s['bio']}</p>
    <div class="hero-actions">
      <a class="btn-primary" href="{s['instagram']}" target="_blank" rel="noopener">Instagramで予約する</a>
      <a class="btn-ghost" href="{s['hotpepper']}" target="_blank" rel="noopener">HotPepperで予約</a>
    </div>
  </div>
  <div class="portrait">
    <span class="monogram">{s['monogram']}</span>
    <div class="portrait-tag"><span>OLINO / 東住吉区</span><span>{s['portrait_tag']}</span></div>
  </div>
</header>

{store_section('../')}

<section class="wrap reveal" id="blog">
  <div class="section-head">
    <span class="eyebrow">BLOG</span>
    <h2>{s['name']}のブログ</h2>
    <p>施術の様子やヘアケアのポイントを綴っています。</p>
  </div>
  <div class="blog-list">
    {other_posts_html}
  </div>
</section>

<section class="cta-band">
  <div class="wrap">
    <h2>ご予約はこちらから</h2>
    <p>InstagramのDM、またはHotPepper Beautyからご予約いただけます。</p>
    <div class="cta-actions">
      <a class="btn-primary" href="{s['instagram']}" target="_blank" rel="noopener">Instagramで予約する</a>
      <a class="btn-ghost" href="{s['hotpepper']}" target="_blank" rel="noopener">HotPepperで予約</a>
    </div>
  </div>
</section>

{footer_html(f"{s['name']} / {s['role_label']}")}"""

    title = f"{s['name']}（{s['role_label']}）| ハイトーン・縮毛矯正専門 olino（南田辺・東住吉区）"
    html = page_shell(
        title=title,
        description=s["meta_desc"],
        canonical=f"{SITE_URL}/{s['dir']}/",
        body=body,
        extra_head='<link rel="stylesheet" href="../assets/style.css">\n',
        img_prefix="../",
    )
    out_path = os.path.join(ROOT, s["dir"], "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out_path)


def build_post_page(key, s):
    post = POSTS[key]
    nav = nav_html("../../index.html", "../../", s["name"], anchor_prefix="../index.html").replace("{instagram}", s["instagram"])

    body = f"""{nav}

<div id="top"></div>

<main class="wrap" style="padding-top:56px;">
  <a class="back-link" href="../index.html">&larr; {s['name']}のページに戻る</a>
  <article class="post-full">
    <div class="post-meta"><span class="post-date">{post['date']}</span><span class="post-tag">{post['tag']}</span></div>
    <h1>{post['title']}</h1>
    <img src="../../assets/img/{s['post_img']}" alt="{post['title']}" loading="lazy" width="900" height="1200" style="border-radius:14px;margin:0 0 24px;">
    <div class="post-body">
      {post['body_html']}
    </div>

    <div class="post-cta">
      <p class="post-cta-info">{s['name']}が担当した施術の記事です。気になる方はお気軽にご相談ください。</p>
      <div class="post-cta-actions">
        <a class="btn-primary btn-sm" href="{s['instagram']}" target="_blank" rel="noopener">Instagramで予約する</a>
        <a class="btn-ghost btn-sm" href="{s['hotpepper']}" target="_blank" rel="noopener">HotPepperで予約</a>
      </div>
    </div>
  </article>
</main>

{footer_html(f"{s['name']} / {s['role_label']}")}"""

    title = f"{post['title']} | {s['name']} | olino（大阪市東住吉区・南田辺）"
    canonical = f"{SITE_URL}/{s['dir']}/posts/{s['post_slug']}.html"
    html = page_shell(
        title=title,
        description=post["excerpt"],
        canonical=canonical,
        body=body,
        extra_head='<link rel="stylesheet" href="../../assets/style.css">\n',
        img_prefix="../../",
    )
    out_path = os.path.join(ROOT, s["dir"], "posts", f"{s['post_slug']}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out_path)


def build_hub_index():
    cards = []
    for key, s in STAFF.items():
        cards.append(f"""
    <a class="staff-card" href="{s['dir']}/index.html">
      <div class="monogram">{s['monogram']}</div>
      <h3>{s['name']}</h3>
      <p>{s['role_label']} / {s['role_detail']}</p>
    </a>""".strip("\n"))
    cards_html = "\n    ".join(cards)

    body = f"""<nav class="nav">
  <div class="nav-row">
    <a class="brand" href="index.html"><img class="brand-logo" src="assets/img/logo.png" alt="olino"></a>
    <div class="nav-links">
      <a href="#staff">スタイリスト一覧</a>
      <a href="#store">店舗情報</a>
    </div>
    <a class="nav-cta" href="https://beauty.hotpepper.jp/slnH000505333/" target="_blank" rel="noopener">HotPepperで予約</a>
  </div>
</nav>

<div id="top"></div>

<header class="wrap hero">
  <div>
    <span class="eyebrow">OSAKA HIGASHISUMIYOSHI</span>
    <h1 class="name">ハイトーン・縮毛矯正・髪質改善専門<br>美容室 olino</h1>
    <p class="bio">大阪市東住吉区・南田辺、西田辺エリアの美容室。3名のスタイリストがそれぞれの得意分野で、髪のお悩みやなりたいイメージに合わせた施術をご提案しています。</p>
    <div class="hero-actions">
      <a class="btn-primary" href="https://beauty.hotpepper.jp/slnH000505333/" target="_blank" rel="noopener">HotPepperで予約する</a>
      <a class="btn-ghost" href="#staff">スタイリストを見る</a>
    </div>
  </div>
  <figure class="hero-photo">
    <img src="assets/img/store-exterior.jpg" alt="olino 店舗外観(大阪市東住吉区南田辺)" loading="lazy" width="1600" height="1200">
  </figure>
</header>

<section class="wrap" id="staff" style="padding-top:0;">
  <div class="staff-grid">
    {cards_html}
  </div>
</section>

{store_section('')}

{footer_html("olino")}"""

    title = "美容室olino（オリノ）| 大阪市東住吉区・南田辺 ハイトーン・縮毛矯正・髪質改善専門"
    description = "大阪市東住吉区・南田辺、西田辺エリアの美容室olino公式サイト。ハイトーンカラー・縮毛矯正・髪質改善・ヘアアレンジを得意とする3名のスタイリストが在籍。各スタイリストのブログもこちらから。"
    html = page_shell(
        title=title,
        description=description,
        canonical=f"{SITE_URL}/",
        body=body,
        extra_head='<link rel="stylesheet" href="assets/style.css">\n',
    )
    out_path = os.path.join(ROOT, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out_path)


def build_robots_and_sitemap():
    robots = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    urls = [f"{SITE_URL}/"]
    for key, s in STAFF.items():
        urls.append(f"{SITE_URL}/{s['dir']}/")
        urls.append(f"{SITE_URL}/{s['dir']}/posts/{s['post_slug']}.html")

    entries = "\n".join(
        f"  <url><loc>{u}</loc></url>" for u in urls
    )
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    with open(os.path.join(ROOT, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")

    print("wrote robots.txt, sitemap.xml, .nojekyll")


if __name__ == "__main__":
    for key, s in STAFF.items():
        os.makedirs(os.path.join(ROOT, s["dir"], "posts"), exist_ok=True)
        build_staff_index(key, s)
        build_post_page(key, s)
    build_hub_index()
    build_robots_and_sitemap()
    print("DONE")
