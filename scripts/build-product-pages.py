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
        <p class="description">{e(description)}</p>
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
