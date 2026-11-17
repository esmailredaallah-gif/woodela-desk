"""Regenerate the static product pages and sitemap after changing storefront data."""
import html
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
STORE_URL = "https://woodela.com"
source = (ROOT / "index.html").read_text(encoding="utf-8")


def storefront_constant(name):
    return re.search(rf"^const {name}\s*=\s*(.*?);", source, re.MULTILINE | re.DOTALL)[1]


products = json.loads(storefront_constant("PRODUCTS"))
dimensions = {
    sku: json.loads(value)
    for sku, value in re.findall(
        r"'([\w-]+)': (\[\[.*?\]\])", storefront_constant("PRODUCT_DIMENSIONS")
    )
}
shipping_fee = int(storefront_constant("SHIPPING_FEE"))
free_shipping_from = int(storefront_constant("FREE_SHIPPING_FROM"))
e = html.escape
PRODUCT_COPY = {
    "leaf-duo": "لو بتجهّز ضيافة فيها مشروبات وحلوى، طقم الصواني الخشب بنقشة الأوراق يديك مساحتين للتقديم. استخدم الصينية الكبيرة لتجميع الفناجين والأكواب، وقدّم البسكويت أو قطع الحلوى في الصينية الصغيرة بجانبها. الطقم مكوّن من صينيتين بإطار من خشب الزان الروماني، والمقاسان موضحان بالأعلى عشان تقدر تقارنهم بمساحة طاولة الضيافة عندك.",
    "metal-duo": "طقم صواني خشب بمقابض معدنية للمائدة أو ركن القهوة. يتكوّن من صينيتين بإطار من خشب الزان الروماني. المقابض على طرفَي كل صينية مناسبة للإمساك بها أثناء التقديم. في ضيافة القهوة، ممكن ترتّب الفناجين على الصينية الكبيرة وتستخدم الصغيرة لأطباق الحلوى، أو تختار صينية واحدة حسب عدد الضيوف ومساحة المكان.",
    "woodgrain-duo": "التفاصيل اللي بتحاكي عروق الخشب هي اللي بتميّز الطقم ده. فيه صينيتان من خشب الزان الروماني بمقاسين مختلفين. ممكن تستعمل الكبيرة لتقديم الفطور على المائدة، وتسيب الصغيرة في ركن القهوة للفناجين أو الملاعق. ولو بتختار هدية للبيت، هتلاقي صور الطقم والمقاسين في الصفحة عشان تختار على أساس الشكل والمساحة.",
    "melamine-ornate": "زخارف الأرابيسك المفرغة بتدي طقم الصواني طابع شرقي واضح عند التقديم. الطقم قطعتين، وكل صينية بإطار من خشب الزان الروماني. جرّب تستخدم الكبيرة لصواني الضيافة اللي فيها أطباق صغيرة متعددة، وتخصص الصغيرة للتمر أو البسكويت في طبق منفصل. راجع المقاسين لو الطاولة الجانبية عندك مساحتها محدودة.",
    "rope-handle": "اللي بيميّز طقم صواني الخشب ده هو تفاصيل الحبل في المقابض مع إطار خشب الزان الروماني. الطقم فيه صينيتان تقدر تستخدمهما مع بعض أو كل واحدة لوحدها. مثلًا، قدّم أكواب الشاي في الكبيرة وحط أطباق الضيافة الخفيفة في الصغيرة. شوف الصورة لو شكل المقابض جزء مهم في اختيارك.",
    "steel-pattern": "نقشة هندسية واضحة في إطار من خشب الزان الروماني. الطقم مكوّن من صينيتين، فتقدر تعرض واحدة على طاولة جانبية كقطعة ديكور وتستخدم الثانية لتقديم المشروبات. لو هتستخدم الاتنين في نفس الزيارة، وزّع الأكواب والأطباق الصغيرة بين المقاسين على حسب المساحة المتاحة عندك.",
    "breakfast-mosaic": "صينية تقديم واحدة بتفاصيل موزاييك خشبية وإطار من خشب الزان الروماني. شكل الموزاييك مناسب لو بتحب تخلي الصينية جزء من شكل المائدة وهي عليها أكواب الفطور أو أطباق صغيرة. راجع طولها وعرضها قبل الطلب، خصوصًا لو ناوي تستخدمها باستمرار على طاولة جانبية أو في مكان تخزين محدد.",
    "breakfast-metal": "لو بتدور على صينية فطار خشب بمقابض معدنية، ده موديل من قطعة واحدة من خشب الزان الروماني. تقدر ترتّب عليها طبق الفطور وكوب الشاي في نفس التقديم، أو تستخدمها للمشروبات لما يكون عندك ضيوف. قارن المقاس الموضح بمساحة المائدة، وشوف صورة المقابض عشان تتخيل طريقة حملها.",
    "snack-four": "علبة تسالي خشب بغطاء أكريليك شفاف مستورد وأربع خانات، في قطعة واحدة من خشب الزان الروماني. الخانات تساعدك تفصل الأنواع وقت الضيافة، مثل المكسرات والحلوى والفواكه المجففة والبسكويت، والغطاء الشفاف يخلّيك تشوف المحتويات. راجع المقاس المربع الموضح بالأعلى لو ناوي تحطها في وسط طاولة القهوة.",
    "snack-small": "علبة تسالي خشب صغيرة من قطعة واحدة بثلاثة أقسام وغطاء أكريليك شفاف مستورد بيتفتح بالانزلاق. ممكن تخصص قسم للمكسرات وقسم للحلوى وقسم لتحلية خفيفة مع القهوة. مقاسها المستطيل الموضح في الصفحة يساعدك تعرف لو تناسب المكان اللي هتحطها فيه، خصوصًا لو بتقدم التسالي بجوار الأكواب على نفس الطاولة.",
    "tissues": "حامل واحد لرول المناديل من خشب الزان الروماني، وفيه تفصيلة على شكل زهرة خشبية. ممكن تحطه بجوار أدوات القهوة عشان المناديل تفضل قريبة وقت التقديم، أو تستخدمه للمناولة اليومية في المطبخ. صورة المنتج بتوضح شكل الحامل وتفصيلة الزهرة، ولو عندك مكان محدد له فالمقاس غير مذكور حاليًا على الصفحة."
}


def product_path(product):
    return f"/products/{product['id']}.html"


def original_image(product):
    return f'<img src="/{e(product["image"])}" alt="{e(product["name"])}" width="{product["width"]}" height="{product["height"]}"'


def render_dimensions(product):
    sizes = dimensions.get(product["id"], [])
    if not sizes:
        return '<p class="muted">المقاس غير مذكور حاليًا.</p>'
    labels = ["الكبيرة", "الصغيرة"] if len(sizes) == 2 else ["المقاس"]
    entries = "".join(
        f"<div><dt>{label}</dt><dd><bdi>{length} × {width}</bdi> سم</dd></div>"
        for label, (length, width) in zip(labels, sizes, strict=True)
    )
    return f'<dl class="measurements" aria-label="مقاسات المنتج">{entries}</dl>'


def render_page(product):
    name = product["name"]
    description = product["description"]
    detail = PRODUCT_COPY[product["id"]]
    count = product["product_count"]
    price = product["price"]
    url = STORE_URL + product_path(product)
    image = f'{STORE_URL}/{product["image"]}'
    title = f"{name} | WOODELA"
    meta = f"{description} {count} بسعر {price:,} جنيه مصري. الدفع عند الاستلام."
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
        "description": description,
        "image": [image],
        "url": url,
        "sku": product["id"],
        "offers": {
            "@type": "Offer",
            "url": url,
            "price": price,
            "priceCurrency": "EGP",
        },
    }
    schema_json = json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c")
    related = sorted(
        (item for item in products if item["id"] != product["id"]),
        key=lambda item: (item["category"] != product["category"], abs(item["price"] - price)),
    )[:3]
    links = "\n".join(
        f'<a class="related-card" href="{product_path(item)}">'
        f'{original_image(item)} loading="lazy" decoding="async">'
        f'<span>{e(item["name"])}</span><strong>{item["price"]:,} جنيه</strong></a>'
        for item in related
    )
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(meta)}">
  <meta name="theme-color" content="#30261f">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="product">
  <meta property="og:site_name" content="WOODELA">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(meta)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{image}">
  <meta property="og:image:alt" content="{e(name)}">
  <script type="application/ld+json">{schema_json}</script>
  <link rel="stylesheet" href="/products/product.css">
</head>
<body>
  <header class="site-header"><div class="header-inner">
    <a class="brand" href="/">WOODELA<small>Crafted for Elegant Living</small></a>
    <nav aria-label="المتجر">
      <a href="/#products">المتجر</a>
      <a class="cart-link" href="/#cart">السلة</a>
    </nav>
  </div></header>
  <main>
    <a class="back" href="/#products">العودة لكل المنتجات</a>
    <article class="product">
      <div class="product-photo">{original_image(product)} fetchpriority="high"></div>
      <div class="product-info">
        <p class="category">{e(product["category"])}</p>
        <h1>{e(name)}</h1>
        <p class="price">{price:,} <span>جنيه</span></p>
        <p class="count">{e(count)}</p>
        {render_dimensions(product)}
        <p class="description">{e(detail)}</p>
        <a class="buy" href="/?add={product["id"]}#cart">أضف للسلة</a>
        <p class="shipping">الدفع عند الاستلام. الشحن {shipping_fee} جنيه، ومجاني للطلبات من {free_shipping_from:,} جنيه.</p>
      </div>
    </article>
    <section class="related" aria-labelledby="related-title">
      <h2 id="related-title">منتجات قد تعجبك</h2>
      <div class="related-grid">{links}</div>
    </section>
  </main>
</body>
</html>
'''


def main():
    directory = ROOT / "products"
    directory.mkdir(exist_ok=True)
    for product in products:
        (ROOT / product_path(product).lstrip("/")).write_text(render_page(product), encoding="utf-8")
    links = "\n".join(
        f'  <li><a href="{product_path(product)}">{e(product["name"])}</a></li>'
        for product in products
    )
    updated_source, replacements = re.subn(
        r'(<!-- product-links:start -->).*?(<!-- product-links:end -->)',
        lambda match: f"{match[1]}\n<ul>\n{links}\n</ul>\n{match[2]}",
        source,
        flags=re.DOTALL,
    )
    if replacements != 1:
        raise ValueError("Expected one storefront product-link block")
    if updated_source != source:
        (ROOT / "index.html").write_text(updated_source, encoding="utf-8")
    urls = [STORE_URL + "/"] + [STORE_URL + product_path(product) for product in products]
    entries = "\n".join(f"  <url><loc>{xml_escape(url)}</loc></url>" for url in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n</urlset>\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
