from pathlib import Path
from html.parser import HTMLParser
import json,re,html,math
root=Path(__file__).resolve().parents[1]/'dist'
origin='https://effacemoi.jbleroy.fr'
articles=json.loads((root.parent/'content/blog.json').read_text())
class Plain(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,data):self.parts.append(data)
def plain(s):
 p=Plain();p.feed(s);return ' '.join(p.parts)
for a in articles:
 a['words']=len(plain(a['intro']+' '+ ' '.join(b for h,b in a['sections'])).split())
 assert a['words']>=1500,(a['slug'],a['words'])
 a['minutes']=math.ceil(a['words']/200)
def esc(s):return html.escape(s,quote=True)
def head(title,description,path,schema):
 return f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | EffaceMoi</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{origin}{path}"><meta property="og:type" content="{'article' if '/blog/'!=path else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{origin}{path}"><meta property="og:locale" content="fr_FR"><link rel="preload" href="/assets/fonts/instrument-serif.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/assets/fonts/inter.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/assets/blog.css"><link rel="stylesheet" href="/assets/theme.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('</','<\\/')}</script></head><body><nav><a href="/" class="logo">EffaceMoi<span>.</span></a><div class="links"><a href="/plateformes/">Plateformes</a><a href="/blog/">Blog</a><a href="/avis/">Avis</a><a href="/#tarifs">Tarifs</a><a class="btn navbtn" href="/#request">Créer une demande</a></div></nav>'''
footer='''<div class="wrap"><footer><a href="/" class="logo">EffaceMoi<span>.</span></a><p>Guides pratiques · Sources officielles citées dans chaque article.<br>Informations générales, à adapter à votre situation.</p><a class="footerlink" href="/blog/">Tous les articles</a></footer></div></body></html>'''
related_map={
'supprimer-leak-onlyfans':['demande-retrait-dmca','suivre-demande-retrait','supprimer-resultat-google'],
'photo-intime-sans-consentement':['doxxing-donnees-exposees','signaler-usurpation-identite','supprimer-resultat-google'],
'supprimer-donnees-personnelles-internet':['doxxing-donnees-exposees','supprimer-resultat-google','suivre-demande-retrait'],
'supprimer-resultat-google':['supprimer-donnees-personnelles-internet','photo-intime-sans-consentement','suivre-demande-retrait'],
'demande-retrait-dmca':['supprimer-leak-onlyfans','suivre-demande-retrait','photo-intime-sans-consentement'],
'signaler-usurpation-identite':['doxxing-donnees-exposees','supprimer-donnees-personnelles-internet','suivre-demande-retrait'],
'doxxing-donnees-exposees':['supprimer-donnees-personnelles-internet','signaler-usurpation-identite','supprimer-resultat-google'],
'suivre-demande-retrait':['demande-retrait-dmca','supprimer-resultat-google','supprimer-donnees-personnelles-internet'],
'deepfake-image-intime-retrait':['photo-intime-sans-consentement','supprimer-resultat-google','conserver-preuves-contenu-en-ligne'],
'retirer-photo-personnelle-google':['supprimer-resultat-google','supprimer-donnees-personnelles-internet','photo-intime-sans-consentement'],
'proteger-contenu-createur-copies':['supprimer-leak-onlyfans','demande-retrait-dmca','conserver-preuves-contenu-en-ligne'],
'conserver-preuves-contenu-en-ligne':['suivre-demande-retrait','signaler-usurpation-identite','proteger-contenu-createur-copies']}
by_slug={a['slug']:a for a in articles}
for a in articles:
 path='/blog/'+a['slug']+'/'
 schema={'@context':'https://schema.org','@graph':[{'@type':'BlogPosting','headline':a['title'],'description':a['description'],'datePublished':a.get('published','2026-10-25'),'dateModified':'2026-10-26','wordCount':a['words'],'inLanguage':'fr-FR','author':{'@type':'Organization','name':'EffaceMoi','url':origin},'publisher':{'@type':'Organization','name':'EffaceMoi','url':origin},'mainEntityOfPage':origin+path},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Accueil','item':origin+'/'},{'@type':'ListItem','position':2,'name':'Blog','item':origin+'/blog/'},{'@type':'ListItem','position':3,'name':a['title'],'item':origin+path}]}]}
 toc=''.join(f'<li><a href="#etape-{i}">{esc(h)}</a></li>' for i,(h,b) in enumerate(a['sections'],1))
 body=''.join(f'<section id="etape-{i}"><h2>{esc(h)}</h2>{b}</section>' for i,(h,b) in enumerate(a['sections'],1))
 sources=''.join(f'<li><a href="{esc(u)}">{esc(n)}</a></li>' for n,u in a['sources'])
 related=''.join(f'<a href="/blog/{slug}/">{esc(by_slug[slug]["title"])} →</a>' for slug in related_map[a['slug']])
 page=head(a['title'],a['description'],path,schema)+f'''<main class="wrap"><div class="crumb"><a href="/">Accueil</a> / <a href="/blog/">Blog</a> / {esc(a['cat'])}</div><header class="article-top"><div class="eyebrow">{esc(a['cat'])} · Guide pratique</div><h1>{esc(a['title'])}</h1><p class="post-meta">EffaceMoi · Mis à jour le 26 octobre 2026 · {a['minutes']} min de lecture</p><p class="lead">{a['intro']}</p></header><div class="article-layout"><aside class="toc"><strong>Dans cet article</strong><ol>{toc}</ol></aside><article class="article-body">{body}<section class="sources"><h2>Sources officielles</h2><ul>{sources}</ul><p class="article-note">Les formulaires et critères peuvent évoluer. Vérifiez les indications du destinataire au moment de votre démarche. Ces informations générales ne remplacent pas l’examen de votre situation.</p></section><div class="article-cta"><h2>Préparez votre demande de retrait.</h2><p>Ajoutez les liens concernés, modifiez votre brouillon et exportez-le. Gratuit, sans envoyer de photo ni de vidéo à EffaceMoi.</p><a href="/#request" class="btn">Créer un brouillon →</a><p class="article-note">Vous transmettez la demande au destinataire. EffaceMoi n’effectue pas d’envoi automatique.</p></div></article></div><section class="related"><h2>À lire aussi</h2><div class="related-list">{related}</div></section></main>'''+footer
 d=root/'blog'/a['slug'];d.mkdir(parents=True,exist_ok=True);(d/'index.html').write_text(page)
listing=''.join(f'''<a class="post-link" href="/blog/{a['slug']}/"><div class="post-meta">{esc(a['cat'])}<br>{a['minutes']} min de lecture</div><div><h2>{esc(a['title'])}</h2><p>{esc(a['description'])}</p></div><span>↗</span></a>''' for a in articles)
schema={'@context':'https://schema.org','@type':'CollectionPage','name':'Les guides EffaceMoi','url':origin+'/blog/','mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i,'url':origin+'/blog/'+a['slug']+'/','name':a['title']} for i,a in enumerate(articles,1)]}}
(root/'blog/index.html').write_text(head('Retrait de contenus et vie privée : les guides','Douze guides détaillés pour signaler les contenus diffusés sans accord, protéger vos données et suivre vos demandes de retrait.','/blog/',schema)+f'''<main class="wrap"><header class="blog-head"><div class="eyebrow">Le blog EffaceMoi · 12 guides</div><h1>Les démarches,<br>expliquées clairement.</h1><p>Quel site contacter, quoi demander et comment suivre la réponse. Des guides détaillés, des exemples et les sources officielles pour chaque situation.</p></header><section class="post-list" aria-label="Articles">{listing}</section></main>'''+footer)
home=(root/'index.html').read_text()
preview='<section class="blog-preview"><div class="eyebrow">12 guides pratiques</div><h2>Comprendre les démarches.</h2><div class="guide-cards">'+''.join(f'<a class="guide-card" href="/blog/{a["slug"]}/"><span class="guide-cat">{esc(a["cat"])} · {a["minutes"]} min</span><strong>{esc(a["title"])}</strong><span class="guide-go" aria-hidden="true">→</span></a>' for a in articles[:4])+'</div><p><a class="guide-all" href="/blog/">Voir les 12 guides →</a></p></section>'
assert 'class="blog-preview"' in home
home=re.sub(r'<section class="blog-preview".*?</section>',lambda m:preview,home,flags=re.S)
(root/'index.html').write_text(home)
urls=[origin+'/',origin+'/blog/',origin+'/avis/',origin+'/plateformes/']+[origin+'/blog/'+a['slug']+'/' for a in articles]
(root/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+u+'</loc><lastmod>2026-10-26</lastmod></url>' for u in urls)+'</urlset>')
(root/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+origin+'/sitemap.xml\n')
print(json.dumps([{'slug':a['slug'],'words':a['words']} for a in articles],ensure_ascii=False))
