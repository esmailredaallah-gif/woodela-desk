"""Apply search metadata without rebuilding or changing the approved storefront layout."""
from pathlib import Path
import html
import json
import re
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://woodela.com'
SEO = {
 'leaf-duo': ('طقم صواني خشب بنقشة أوراق، قطعتان | WOODELA', 'طقم صواني خشب بنقشة أوراق من صينيتين؛ الكبيرة 44 × 31 سم والصغيرة 35 × 24 سم. إطار زان روماني لتقديم المشروبات والحلوى. الدفع عند الاستلام.', 'طقم صينيتين خشب بنقشة أوراق ومقابض معدنية'),
 'metal-duo': ('طقم صواني خشب بمقابض معدنية، قطعتان | WOODELA', 'طقم صواني خشب بمقابض معدنية من صينيتين؛ الكبيرة 42 × 29 سم والصغيرة 33 × 22 سم. إطار زان روماني لضيافة القهوة والحلوى. الدفع عند الاستلام.', 'طقم صينيتين خشب بمقابض معدنية'),
 'woodgrain-duo': ('طقم صواني خشب بنقشة عروق الخشب | WOODELA', 'طقم صواني خشب بنقشة عروق الخشب، صينيتان بإطار زان روماني؛ الكبيرة 42 × 29 سم والصغيرة 33 × 22 سم. للتقديم والضيافة. الدفع عند الاستلام.', 'طقم صينيتين بإطار خشبي ونقشة عروق الخشب'),
 'melamine-ornate': ('طقم صواني خشب أرابيسك، قطعتان | WOODELA', 'طقم صواني خشب أرابيسك من صينيتين بإطار زان روماني؛ الكبيرة 44 × 31 سم والصغيرة 35 × 24 سم. زخارف مفرغة لضيافة المشروبات والحلوى.', 'طقم صينيتين خشب بزخارف أرابيسك مفرغة'),
 'rope-handle': ('طقم صواني خشب بمقابض حبل، قطعتان | WOODELA', 'طقم صواني خشب بمقابض حبل وإطار زان روماني؛ صينيتان، الكبيرة 42 × 29 سم والصغيرة 33 × 22 سم. لتقديم الفطار وضيافة المنزل. الدفع عند الاستلام.', 'طقم صينيتين خشب بمقابض حبل'),
 'steel-pattern': ('طقم صواني خشب بنقشة هندسية | WOODELA', 'طقم صواني خشب بنقشة هندسية من صينيتين بإطار زان روماني؛ الكبيرة 42 × 29 سم والصغيرة 33 × 22 سم. لتقديم المشروبات والحلوى في المنزل.', 'طقم صينيتين بإطار خشبي ونقشة هندسية'),
 'breakfast-mosaic': ('صينية فطار خشب برجلين بنقشة موزاييك | WOODELA', 'صينية فطار خشب برجلين بنقشة موزاييك، مقاس 62 × 37 سم، بإطار من خشب الزان الروماني. صينية واحدة للتقديم والفطار في المنزل. الدفع عند الاستلام.', 'صينية فطار خشب برجلين بنقشة موزاييك'),
 'breakfast-metal': ('صينية فطار خشب بمقابض معدنية 62 × 37 سم | WOODELA', 'صينية فطار خشب بمقابض معدنية من الزان الروماني، مقاس 62 × 37 سم. صينية واحدة لتقديم الفطار والمشروبات وضيافة المنزل. الدفع عند الاستلام.', 'صينية فطار خشب واحدة بمقابض معدنية'),
 'snack-small': ('علبة تسالي خشب 3 أقسام بغطاء شفاف | WOODELA', 'علبة تسالي خشب صغيرة 3 أقسام، مقاس 31 × 16 سم، من الزان الروماني بغطاء أكريليك شفاف منزلق. لتقديم المكسرات والحلوى. الدفع عند الاستلام.', 'علبة تسالي خشب مستطيلة بثلاثة أقسام وغطاء أكريليك شفاف'),
 'snack-four': ('علبة تسالي خشب 4 علب منفصلة داخل إطار | WOODELA', 'علبة تسالي خشب 31 × 31 سم: أربع علب منفصلة تتجمع داخل إطار زان روماني، مع غطاء أكريليك شفاف. لتقديم المكسرات والحلوى. الدفع عند الاستلام.', 'علبة تسالي خشب بأربع علب منفصلة داخل إطار رئيسي'),
 'tissues': ('حامل رول مناديل خشبي بتفصيلة زهرة | WOODELA', 'حامل رول مناديل خشبي من الزان الروماني بتفصيلة زهرة، قطعة واحدة للمطبخ أو ركن القهوة. شاهد صورة المنتج وتفاصيله؛ المقاس غير متوفر حاليًا.', 'حامل رول مناديل خشبي بتفصيلة زهرة خشبية'),
}

def head_meta(s, title, desc, alt=None):
 s=re.sub(r'<title>.*?</title>',lambda _: '<title>'+html.escape(title)+'</title>',s,count=1,flags=re.S)
 s=re.sub(r'(<meta\s+(?:name|property)="(?:description|og:description)"\s+content=")[^"]*("\s*/?>)',lambda m:m[1]+html.escape(desc,quote=True)+m[2],s)
 s=re.sub(r'(<meta\s+property="og:title"\s+content=")[^"]*("\s*/?>)',lambda m:m[1]+html.escape(title,quote=True)+m[2],s)
 if alt:s=re.sub(r'(<meta\s+property="og:image:alt"\s+content=")[^"]*("\s*/?>)',lambda m:m[1]+html.escape(alt,quote=True)+m[2],s)
 if not re.search(r'<meta\s+name="robots"',s):s=s.replace('</head>','<meta name="robots" content="index,follow,max-image-preview:large">\n</head>',1)
 return s

s=(ROOT/'index.html').read_text()
products=json.loads(re.search(r'^const PRODUCTS\s*=\s*(.*?);',s,re.M|re.S)[1])
assert set(SEO)=={p['id'] for p in products}
# Dimensions always come from the approved storefront data, not from copy drafts.
dim_src=re.search(r'^const PRODUCT_DIMENSIONS\s*=\s*(.*?);',s,re.M|re.S)[1]
dimensions={k:json.loads(v) for k,v in re.findall(r"'([\w-]+)': (\[\[.*?\]\])",dim_src)}
# All drafted numeric dimensions must match published values.
for sku,(title,desc,alt) in SEO.items():
 published={tuple(x) for x in dimensions.get(sku,[])}
 for a,b in re.findall(r'(\d+) × (\d+)',desc):assert (int(a),int(b)) in published,(sku,a,b,published)

def image_alts(t):
 bysrc={p['image']:SEO[p['id']][2] for p in products}
 def fix(m):
  tag=m[0];src=re.search(r'\bsrc="([^"]+)"',tag)
  if src and src[1].lstrip('/') in bysrc:
   tag=re.sub(r'\balt="[^"]*"','alt="'+html.escape(bysrc[src[1].lstrip('/')],quote=True)+'"',tag)
  return tag
 return re.sub(r'<img\b[^>]*>',fix,t)

s=head_meta(s,'WOODELA | صواني خشب وعلب تسالي للمنزل والضيافة','تسوق أطقم صواني خشب وصواني فطار وعلب تسالي خشب من WOODELA. صور أصلية ومقاسات واضحة للمنزل والضيافة. دفع عند الاستلام وشحن مجاني من 1000 جنيه.')
s=image_alts(s)
alts='const PRODUCT_IMAGE_ALTS='+json.dumps({k:v[2] for k,v in SEO.items()},ensure_ascii=False,separators=(',',':'))+';'
if 'const PRODUCT_IMAGE_ALTS=' in s:s=re.sub(r'^const PRODUCT_IMAGE_ALTS=.*?;$',lambda _:alts,s,flags=re.M)
else:s=re.sub(r'(^const PRODUCTS\s*=\s*.*?;)',lambda m:m[1]+'\n'+alts,s,count=1,flags=re.M|re.S)
s=s.replace('alt="${p.name}" loading="lazy"','alt="${PRODUCT_IMAGE_ALTS[p.id]||p.name}" loading="lazy"')
s=s.replace("$('heroProduct').alt=heroChoice.name;","$('heroProduct').alt=PRODUCT_IMAGE_ALTS[heroChoice.id]||heroChoice.name;")
# Existing user-approved official accounts, unchanged from the storefront footer.
socials=['https://www.facebook.com/share/18Vkf2kAcP/','https://instagram.com/WOODELA.home','https://www.tiktok.com/@woodela_home']
def store_identity(m):
 data=json.loads(m[1])
 if data.get('@type')=='Store':
  data['@id']=SITE+'/#store';data['sameAs']=socials
  data['description']='WOODELA متجر للمنتجات المنزلية الخشبية والضيافة: أطقم صواني وصواني فطار وعلب تسالي وحامل مناديل.'
 return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'</script>'
s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',store_identity,s,flags=re.S)
(ROOT/'index.html').write_text(s)
for product in products:
 sku=product['id'];p=ROOT/'products'/f'{sku}.html';t=p.read_text();title,desc,alt=SEO[sku]
 t=head_meta(t,title,desc,alt);t=image_alts(t);p.write_text(t)
# Keep all existing page and image URLs. Add only supported image sitemap tags.
rows=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',f'  <url><loc>{SITE}/</loc></url>']
for p in products:rows.append(f'  <url><loc>{SITE}/products/{p["id"]}.html</loc><image:image><image:loc>{escape(SITE+"/"+p["image"])}</image:loc></image:image></url>')
rows.append('</urlset>');(ROOT/'sitemap.xml').write_text('\n'.join(rows)+'\n')
# Archive stays accessible; keep the discontinued desk-organizer offer out of search.
legacy=ROOT/'index-9.html';t=legacy.read_text()
if not re.search(r'<meta\s+name="robots"',t):
 t=t.replace('</head>','<meta name="robots" content="noindex,follow">\n</head>',1);legacy.write_text(t)
print('Updated 12 current page metadata sets, 11 image entries and archived-page search directive.')
