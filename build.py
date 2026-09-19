#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
olino 新サイト ビルドスクリプト
_extracted.json の記事データ + STAFF 情報から、静的HTMLサイト一式を生成する。
GitHub Pages にそのまま置けば動く(ビルドツール不要・全部素のHTML)。
"""
import json, os, re, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://haircolorokamo-pixel.github.io/olino-blog"

with open(os.path.join(ROOT, "_extracted.json"), encoding="utf-8") as f:
    POSTS = json.load(f)

# 復旧用データ(2026-09-19: LINE経由でCode.gs側が直接GitHubへ公開したブログ記事が、
# このスクリプトによる全体再ビルド時にstaffのindex.html/sitemap.xmlを丸ごと上書きしてしまい、
# 一覧・サイトマップから見えなくなっていた分)。下のfetch_live_html()によるライブ取得と
# 突き合わせて、まだ反映されていないものだけ差し込む。記事ページ自体は元々消えていない。
RECOVERED_POSTS_PATH = os.path.join(ROOT, "recovered_posts.json")
if os.path.exists(RECOVERED_POSTS_PATH):
    with open(RECOVERED_POSTS_PATH, encoding="utf-8") as f:
        RECOVERED_POSTS = json.load(f)
else:
    RECOVERED_POSTS = []


def fetch_live_html(url, timeout=15):
    """本番サイトの現在のHTMLを取得する(失敗時はNoneを返す)。
    これにより、テンプレート更新の再ビルドがCode.gs側で追加された既存のブログ記事や
    サイトマップURLを上書き消去してしまう事故を防ぐ(2026-09-19に一度発生した)。"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-w", "\n__HTTP_STATUS__:%{http_code}", url],
            capture_output=True, text=True, timeout=timeout
        )
        out = result.stdout
        marker = "\n__HTTP_STATUS__:"
        idx = out.rfind(marker)
        if idx == -1:
            return None
        body, status = out[:idx], out[idx + len(marker):].strip()
        if status != "200" or not body:
            return None
        return body
    except Exception as e:
        print("fetch_live_html failed for", url, ":", e)
        return None


def extract_balanced_div(html, marker):
    """htmlの中からmarker(例: '<div class="blog-list">')を探し、対応する閉じタグまでの
    「中身」だけを返す(ネストしたdivを正しく数える)。見つからなければNone。"""
    idx = html.find(marker)
    if idx == -1:
        return None
    pos = idx + len(marker)
    depth = 1
    for m in re.finditer(r"<div\b[^>]*>|</div>", html[pos:]):
        if m.group().startswith("</div"):
            depth -= 1
        else:
            depth += 1
        if depth == 0:
            return html[pos: pos + m.start()]
    return None


def build_post_card_html(post, dir_, slug):
    """スタッフindex.htmlのブログ一覧に挿入する記事カードHTML(Code.gs側buildPostCardHtml_と同一構造)。"""
    return (
        f'<a class="post-card" href="posts/{slug}.html">\n'
        f'          <div class="thumb"><img src="posts/img/{slug}.jpg" alt="{post["title"]}" loading="lazy"></div>\n'
        f'          <div class="card-body">\n'
        f'            <div class="post-meta"><span class="post-date">{post["date"]}</span><span class="post-tag">{post["tag"]}</span></div>\n'
        f'            <h3>{post["title"]}</h3>\n'
        f'            <p class="excerpt">{post["excerpt"]}</p>\n'
        f'            <span class="read-more">続きを読む →</span>\n'
        f'          </div>\n'
        f'        </a>'
    )

STAFF = {
    "takasu": {
        "dir": "takasu",
        "name": "高巣直哉",
        "name_en": "Takasu Naoya",
        "role_label": "店長",
        "role_detail": "ハイトーン・メンズカット・パーマ特化",
        "monogram": "直",
        "portrait_img": "takasu-portrait.jpg",
        "thumb_img": "takasu-thumb.jpg",
        "intro_short": "外国人風カラーとメンズカットが得意。骨格や肌色を見ながら、なりたいイメージをじっくり相談して決めます。",
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
        "portrait_img": "kaori-portrait.jpg",
        "thumb_img": "kaori-thumb.jpg",
        "intro_short": "縮毛矯正と髪質改善が専門。くせやうねりのお悩みに合わせて、薬剤やアイロンの温度を都度調整します。",
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
        "portrait_img": "sasara-portrait.jpg",
        "thumb_img": "sasara-thumb.jpg",
        "intro_short": "ヘアアレンジとトレンドカラーが得意。お出かけ前や特別な日のアレンジも気軽に相談できます。",
        "bio": "ヘアアレンジとカラーを担当しています。丁寧な仕上がりを意識しながら、毎日練習を重ねています。お出かけ前や特別な日のヘアアレンジも、気軽に相談してください。",
        "instagram": "https://www.instagram.com/olino_sasa/",
        "hotpepper": "https://beauty.hotpepper.jp/slnH000505333/",
        "portrait_tag": "美容師",
        "post_slug": "2026-09-02-navy-blue-color",
        "post_img": "sasara-post1.jpg",
        "meta_desc": "大阪市東住吉区・南田辺の美容室olino美容師、SASARAのページ。ヘアアレンジとトレンドカラーが得意で、南田辺・東住吉区エリアでカラーを楽しみたい方におすすめです。",
    },
}

NAV_LINKS = [("スタイリスト", "#staff"), ("スタイル一覧", "styles.html"), ("店舗情報", "#store"), ("ブログ", "#blog")]

LENGTH_ORDER = ["ショート", "ボブ", "ミディアム", "ロング", "ヘアアレンジ"]

LENGTH_SLUGS = {
    "ショート": "short",
    "ボブ": "bob",
    "ミディアム": "medium",
    "ロング": "long",
    "ヘアアレンジ": "arrange",
}

LENGTH_EYEBROW_EN = {
    "ショート": "SHORT",
    "ボブ": "BOB",
    "ミディアム": "MEDIUM",
    "ロング": "LONG",
    "ヘアアレンジ": "HAIR ARRANGE",
}

STYLE_PHOTOS = [
    {"img": "takasu-bob-pink.jpg", "length": "ボブ", "label": "くすみピンクの外ハネボブ", "staff": "takasu"},
    {"img": "takasu-short-undercut.jpg", "length": "ショート", "label": "刈り上げすっきりショート", "staff": "takasu"},
    {"img": "takasu-long-straight.jpg", "length": "ロング", "label": "艶感まとまるロングストレート", "staff": "takasu"},
    {"img": "kaori-medium-umbrella.jpg", "length": "ミディアム", "label": "アンブレラカラーのレイヤーミディアム", "staff": "kaori"},
    {"img": "kaori-long-marron.jpg", "length": "ロング", "label": "秋色マロンブラウンの艶ストレート", "staff": "kaori"},
    {"img": "kaori-long-greige.jpg", "length": "ロング", "label": "グレージュの柔らかウェーブロング", "staff": "kaori"},
    {"img": "sasara-arrange-updo.jpg", "length": "ヘアアレンジ", "label": "夜会巻き風アップアレンジ", "staff": "sasara"},
    {"img": "sasara-long-beige.jpg", "length": "ロング", "label": "ベージュカラーの巻き髪ロング", "staff": "sasara"},
    {"img": "sasara-arrange-braid.jpg", "length": "ヘアアレンジ", "label": "リボン編みおろしアレンジ", "staff": "sasara"},
]

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


def nav_html(index_href, img_prefix, brand_suffix="", anchor_prefix="", hub_href=None, styles_href=None):
    # 「スタイリスト」だけは常にハブ(トップページ)のスタイリスト一覧セクションへ飛ばす。
    # 「スタイル一覧」は常にスタイルギャラリーページ(styles.html)へ飛ばす。
    # 「店舗情報」「ブログ」はそのスタッフ自身のページ内セクションへ飛ばす(anchor_prefixに従う)。
    overrides = {"スタイリスト": hub_href, "スタイル一覧": styles_href}

    def link_href(label, href):
        if overrides.get(label) is not None:
            return overrides[label]
        return f"{anchor_prefix}{href}"
    links = "\n      ".join(f'<a href="{link_href(label, href)}">{label}</a>' for label, href in NAV_LINKS)
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


def top_level_nav_html():
    # ハブ配下のトップレベルページ(index.html, styles.html, styles-*.html)共通のナビ。
    return """<nav class="nav">
  <div class="nav-row">
    <a class="brand" href="index.html"><img class="brand-logo" src="assets/img/logo.png" alt="olino"></a>
    <div class="nav-links">
      <a href="index.html#staff">スタイリスト一覧</a>
      <a href="styles.html">スタイル一覧</a>
      <a href="index.html#store">店舗情報</a>
    </div>
    <a class="nav-cta" href="https://beauty.hotpepper.jp/slnH000505333/" target="_blank" rel="noopener">HotPepperで予約</a>
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


def build_blog_list_html(key, s):
    """このスタッフのblog-list中身HTMLを組み立てる。
    本番サイトに今すでにある記事一覧(Code.gs側がLINE経由で直接GitHubへ追加したものを含む)を
    ライブ取得し、それを土台にする。取得できた場合、まだ反映されていない復旧データ
    (RECOVERED_POSTS)のうち新しいものだけを先頭に差し込む。ライブ取得に失敗した場合のみ、
    従来通り最初の1記事だけのフォールバックにする。"""
    original_card = (
        f'<a class="post-card" href="posts/{s["post_slug"]}.html">\n'
        f'          <div class="thumb"><img src="../assets/img/{s["post_img"]}" alt="{POSTS[key]["title"]}" loading="lazy" width="800" height="1000"></div>\n'
        f'          <div class="card-body">\n'
        f'            <div class="post-meta"><span class="post-date">{POSTS[key]["date"]}</span><span class="post-tag">{POSTS[key]["tag"]}</span></div>\n'
        f'            <h3>{POSTS[key]["title"]}</h3>\n'
        f'            <p class="excerpt">{POSTS[key]["excerpt"]}</p>\n'
        f'            <span class="read-more">続きを読む →</span>\n'
        f'          </div>\n'
        f'        </a>'
    )

    live_html = fetch_live_html(f"{SITE_URL}/{s['dir']}/index.html")
    existing_inner = extract_balanced_div(live_html, '<div class="blog-list">') if live_html else None

    if existing_inner is None:
        print(f"[warn] {s['dir']}: 本番のblog-listを取得できなかったため、静的な1記事のみで生成します。")
        return other_posts_html_fallback(original_card)

    existing_slugs = set(re.findall(r'posts/([^"]+?)\.html', existing_inner))

    recovered_for_staff = [p for p in RECOVERED_POSTS if p["dir"] == s["dir"] and p["slug"] not in existing_slugs]
    recovered_for_staff.reverse()  # 日付昇順で保存されているので、新しい記事が上に来るよう反転する
    if recovered_for_staff:
        print(f"[recover] {s['dir']}: 本番に未反映の記事を{len(recovered_for_staff)}件差し込みます。")

    new_cards = "\n        ".join(build_post_card_html(p, p["dir"], p["slug"]) for p in recovered_for_staff)
    if new_cards:
        return new_cards + "\n        " + existing_inner.strip()
    return existing_inner.strip()


def other_posts_html_fallback(original_card):
    return original_card


def build_staff_index(key, s):
    nav = nav_html("../index.html", "../", s["name"], hub_href="../index.html#staff", styles_href="../styles.html").replace("{instagram}", s["instagram"])

    other_posts_html = build_blog_list_html(key, s)

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
    <img src="../assets/img/{s['portrait_img']}" alt="olino {s['name']}（{s['role_label']}）のプロフィール写真" loading="eager" width="932" height="1400">
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
    nav = nav_html("../../index.html", "../../", s["name"], anchor_prefix="../index.html", hub_href="../../index.html#staff", styles_href="../../styles.html").replace("{instagram}", s["instagram"])

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
      <div class="staff-card-photo"><img src="assets/img/{s['thumb_img']}" alt="olino {s['name']}（{s['role_label']}）のプロフィール写真" loading="lazy" width="333" height="500"></div>
      <h3>{s['name']}</h3>
      <p>{s['role_label']} / {s['role_detail']}</p>
      <p class="staff-card-intro">{s['intro_short']}</p>
    </a>""".strip("\n"))
    cards_html = "\n    ".join(cards)

    body = f"""{top_level_nav_html()}

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


def _styles_by_length():
    by_length = {length: [] for length in LENGTH_ORDER}
    for photo in STYLE_PHOTOS:
        by_length.setdefault(photo["length"], []).append(photo)
    return by_length


def build_styles_index():
    # スタイル一覧のハブページ。レングスごとの5ページへのリンクカードのみを持つ軽量なページ。
    # 件数が増えても(将来1000件規模になっても)このページ自体は重くならない。
    by_length = _styles_by_length()

    cards = []
    for length in LENGTH_ORDER:
        photos = by_length.get(length, [])
        if not photos:
            continue
        rep = photos[0]  # 代表写真(先頭の1枚)をサムネイルに使う
        s = STAFF[rep["staff"]]
        slug = LENGTH_SLUGS[length]
        cards.append(f"""
    <a class="length-card" href="styles-{slug}.html">
      <div class="length-card-photo"><img src="assets/img/styles/{rep['img']}" alt="{length}のスタイル例（担当: {s['name']}）" loading="lazy" width="750" height="1000"></div>
      <div class="length-card-body">
        <h3>{length}</h3>
        <p>{len(photos)}件のスタイルを見る →</p>
      </div>
    </a>""".strip("\n"))
    cards_html = "\n    ".join(cards)

    body = f"""{top_level_nav_html()}

<div id="top"></div>

<header class="wrap hub-hero">
  <span class="eyebrow">STYLE GALLERY</span>
  <h1>スタイルギャラリー</h1>
  <p>olinoのスタイリストが実際に手がけたスタイルを、レングス別にまとめました。気になるスタイルがあれば、担当スタイリストのページから予約できます。</p>
</header>

<section class="wrap" style="padding-top:0;">
  <div class="length-grid">
    {cards_html}
  </div>
</section>

{footer_html("olino")}"""

    title = "スタイルギャラリー（レングス別）| 美容室olino（大阪市東住吉区・南田辺）"
    description = "美容室olinoのスタイリストが手がけたヘアスタイルを、ショート・ボブ・ミディアム・ロング・ヘアアレンジなどレングス別にまとめたスタイルギャラリーです。"
    html = page_shell(
        title=title,
        description=description,
        canonical=f"{SITE_URL}/styles.html",
        body=body,
        extra_head='<link rel="stylesheet" href="assets/style.css">\n',
    )
    out_path = os.path.join(ROOT, "styles.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out_path)


def build_style_length_page(length):
    # レングスごとの個別ページ。ここに新しいスタイルが日々自動追加されていく想定
    # (Code.gs 側が <div class="style-grid"> の直後にカードを差し込む)。
    by_length = _styles_by_length()
    photos = by_length.get(length, [])
    slug = LENGTH_SLUGS[length]

    cards = []
    for p in photos:
        s = STAFF[p["staff"]]
        cards.append(f"""
    <a class="style-card" href="{s['dir']}/index.html">
      <div class="style-card-photo"><img src="assets/img/styles/{p['img']}" alt="{p['label']}（担当: {s['name']}）" loading="lazy" width="750" height="1000"></div>
      <div class="style-card-body">
        <span class="post-tag">{length}</span>
        <h3>{p['label']}</h3>
        <p>{s['name']} / {s['role_label']}</p>
      </div>
    </a>""".strip("\n"))
    cards_html = "\n    ".join(cards) if cards else ''

    if cards:
        grid_html = f"""<div class="style-grid">
    {cards_html}
  </div>"""
    else:
        grid_html = """<div class="style-grid">
    <p class="empty-state">準備中です。近日公開予定です。</p>
  </div>"""

    length_tabs = " / ".join(
        (f'<strong>{l}</strong>' if l == length else f'<a href="styles-{LENGTH_SLUGS[l]}.html">{l}</a>')
        for l in LENGTH_ORDER if by_length.get(l) or l == length
    )

    body = f"""{top_level_nav_html()}

<div id="top"></div>

<header class="wrap hub-hero">
  <span class="eyebrow">{LENGTH_EYEBROW_EN.get(length, length)}</span>
  <h1>{length}のスタイル</h1>
  <p>olinoのスタイリストが実際に手がけた{length}のスタイル集です。気になるスタイルがあれば、担当スタイリストのページから予約できます。</p>
  <p class="note"><a href="styles.html">← スタイルギャラリー一覧に戻る</a>　|　{length_tabs}</p>
</header>

<section class="wrap reveal" style="padding-top:0;">
  {grid_html}
</section>

{footer_html("olino")}"""

    title = f"{length}のスタイル一覧 | 美容室olino（大阪市東住吉区・南田辺）"
    description = f"美容室olinoのスタイリストが手がけた{length}のヘアスタイル一覧です。気に入ったスタイルがあれば担当スタイリストにそのままご相談・ご予約いただけます。"
    html = page_shell(
        title=title,
        description=description,
        canonical=f"{SITE_URL}/styles-{slug}.html",
        body=body,
        extra_head='<link rel="stylesheet" href="assets/style.css">\n',
    )
    out_path = os.path.join(ROOT, f"styles-{slug}.html")
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

    urls = [f"{SITE_URL}/", f"{SITE_URL}/styles.html"]
    for length in LENGTH_ORDER:
        urls.append(f"{SITE_URL}/styles-{LENGTH_SLUGS[length]}.html")
    for key, s in STAFF.items():
        urls.append(f"{SITE_URL}/{s['dir']}/")
        urls.append(f"{SITE_URL}/{s['dir']}/posts/{s['post_slug']}.html")
    for p in RECOVERED_POSTS:
        urls.append(f"{SITE_URL}/{p['dir']}/posts/{p['slug']}.html")

    # 本番のsitemap.xmlに今すでにあるURL(Code.gs側が記事公開のたびに追加したものを含む)を
    # ライブ取得して合流させる。これをしないと、テンプレート更新の再ビルドのたびに
    # 既存記事のURLがsitemapから消えてしまう(2026-09-19に一度発生した事故と同じ原因)。
    live_sitemap = fetch_live_html(f"{SITE_URL}/sitemap.xml")
    if live_sitemap:
        live_urls = re.findall(r"<loc>([^<]+)</loc>", live_sitemap)
        added = 0
        seen = set(urls)
        for u in live_urls:
            if u not in seen:
                urls.append(u)
                seen.add(u)
                added += 1
        if added:
            print(f"[recover] sitemap.xml: 本番から{added}件のURLを合流させました。")
    else:
        print("[warn] sitemap.xml: 本番のsitemapを取得できなかったため、静的なURLのみで生成します。")

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
    build_styles_index()
    for length in LENGTH_ORDER:
        build_style_length_page(length)
    build_robots_and_sitemap()
    print("DONE")
