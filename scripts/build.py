"""Génère tout le site statique dans dist/ : accueil, avis, périmètre, ressources et articles, sitemap, robots.

Usage : python3 scripts/build.py
Contenus éditoriaux : content/blog.json (articles), content/avis.json (avis clients réels, publiés avec accord).
"""
from pathlib import Path
from html.parser import HTMLParser
import json, html, math

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
ORIGIN = 'https://effacemoi.jbleroy.fr'
UPDATED = '2026-10-26'
articles = json.loads((ROOT / 'content/blog.json').read_text())
avis = json.loads((ROOT / 'content/avis.json').read_text())


def esc(s):
    return html.escape(s, quote=True)


class Plain(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain(s):
    p = Plain()
    p.feed(s)
    return ' '.join(p.parts)


for a in articles:
    a['words'] = len(plain(a['intro'] + ' ' + ' '.join(b for h, b in a['sections'])).split())
    assert a['words'] >= 1500, (a['slug'], a['words'])
    a['minutes'] = math.ceil(a['words'] / 200)
by_slug = {a['slug']: a for a in articles}

# ---------------------------------------------------------------- gabarit commun
NAV = [('/#situations', 'Situations traitées'), ('/#methode', 'Méthode'), ('/#avocats', 'Avocats'),
       ('/avis/', 'Avis'), ('/blog/', 'Ressources')]


def head(title, description, path, schema=None, og_type='website'):
    ld = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")}</script>' if schema else ''
    return f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{ORIGIN}{path}">
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{ORIGIN}{path}"><meta property="og:locale" content="fr_FR">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23161616'/%3E%3Ctext x='16' y='23' font-family='Georgia,serif' font-size='20' text-anchor='middle' fill='%23fff'%3EE%3C/text%3E%3C/svg%3E">
<link rel="preload" href="/assets/fonts/source-serif.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">{ld}</head><body>
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="top"><div class="wrap top-in"><a href="/" class="logo">EffaceMoi</a>
<nav aria-label="Navigation principale">{''.join(f'<a href="{h}">{t}</a>' for h, t in NAV)}</nav>
<a class="top-cta" href="/#contact">Nous contacter</a></div></header>
<main id="contenu">'''


FOOTER = '''</main>
<footer class="foot"><div class="wrap foot-in">
<div><a href="/" class="logo">EffaceMoi</a><p>Réputation et vie privée en ligne des dirigeants, des entrepreneurs et de leurs proches.</p></div>
<ul><li><a href="/#situations">Situations traitées</a></li><li><a href="/#methode">Méthode</a></li><li><a href="/#avocats">Avocats</a></li><li><a href="/plateformes/">Périmètre</a></li></ul>
<ul><li><a href="/avis/">Avis clients</a></li><li><a href="/blog/">Ressources</a></li><li><a href="/#questions">Questions</a></li><li><a href="/#contact">Contact</a></li></ul>
<p class="foot-note">Aucun résultat n’est garanti : la décision appartient au site, au moteur de recherche ou au juge. EffaceMoi n’est affilié à aucune plateforme citée.</p>
</div></footer></body></html>'''


def write(path, content):
    f = DIST / path.strip('/') / 'index.html' if path != '/' else DIST / 'index.html'
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content)


def block(id_, label, body, cls=''):
    """Section en deux colonnes : intitulé court à gauche, contenu à droite."""
    return f'<section class="block {cls}"{f" id={chr(34)}{id_}{chr(34)}" if id_ else ""}><div class="wrap block-in"><h2 class="block-label">{label}</h2><div class="block-body">{body}</div></div></section>'


# ---------------------------------------------------------------- accueil
TOPICS = ['Article ou publication qui me met en cause', 'Résultat Google associé à mon nom', 'Informations personnelles publiées',
          'Faux profil ou usurpation', 'Photos ou vidéos diffusées sans accord', 'Surveillance de mon nom dans la durée', 'Autre']

situations = [
    ('Un article qui vous met en cause', 'Un papier ancien sur une affaire classée, un billet de blog inexact, un avis dénigrant sur votre entreprise. Selon le cas : actualisation, droit de réponse, retrait ou action en diffamation.'),
    ('Un résultat Google associé à votre nom', 'Le lien existe toujours, mais il n’a plus lieu d’apparaître quand on vous cherche. Demande de déréférencement au titre du RGPD, et recours auprès de la CNIL si elle est refusée.'),
    ('Votre adresse ou votre téléphone en ligne', 'Annuaires, sites de données, forums : votre domicile, celui de vos proches ou des informations sur votre patrimoine circulent. Demandes d’effacement et suivi des republications.'),
    ('Un faux profil à votre nom', 'Un compte LinkedIn, Instagram ou X utilise votre nom ou votre photo, parfois pour contacter vos partenaires. Signalement, conservation des preuves, plainte si nécessaire.'),
    ('Des images diffusées sans votre accord', 'Photos privées, vidéos, montages générés par IA. Ces dossiers sont traités en priorité et ne sont partagés qu’avec l’avocat qui en a besoin.'),
    ('Des documents internes qui ont fuité', 'Courriers, échanges privés, documents de l’entreprise reproduits sans autorisation. Retrait auprès des hébergeurs, sur le fondement du droit d’auteur ou du secret des affaires.'),
]
faq = [
    ('Pouvez-vous garantir qu’un contenu disparaîtra ?', 'Non. La décision appartient au site, au moteur de recherche ou au juge. Ce que nous pouvons vous dire après le premier échange, c’est si la démarche a des chances raisonnables d’aboutir, et sur quel fondement.'),
    ('Combien cela coûte-t-il ?', 'Cela dépend du nombre de contenus, des sites concernés et de l’éventuelle nécessité d’aller devant un juge. Vous recevez une proposition écrite après le premier échange ; rien n’est engagé avant votre accord.'),
    ('Qui connaîtra mon dossier ?', 'Votre interlocuteur chez nous et, si une action juridique est nécessaire, l’avocat qui la mène. Nous ne citons jamais nos clients. Un accord de confidentialité peut être signé avant que vous nous exposiez les détails.'),
    ('Supprimer ou déréférencer, quelle différence ?', 'Supprimer, c’est faire retirer la page chez le site qui la publie. Déréférencer, c’est faire disparaître le lien des résultats d’un moteur de recherche quand on tape votre nom ; la page existe toujours. Les deux se mènent souvent en parallèle.'),
    ('Vous occupez-vous aussi de l’entreprise ou de ma famille ?', 'Oui. Une mise en cause vise souvent le dirigeant et sa société en même temps, et les proches sont régulièrement exposés.'),
]

home_schema = {'@context': 'https://schema.org', '@type': 'ProfessionalService', 'name': 'EffaceMoi', 'url': ORIGIN + '/',
               'description': 'Protection de la réputation en ligne des dirigeants et de leurs proches, avec des avocats spécialisés.',
               'areaServed': 'FR', 'knowsLanguage': 'fr'}

home = head('EffaceMoi — Réputation en ligne des dirigeants',
            'Articles, résultats Google, faux profils, informations personnelles exposées : EffaceMoi aide les dirigeants et leurs proches à faire retirer ce qui leur nuit en ligne, avec des avocats spécialisés.',
            '/', home_schema)
home += f'''
<section class="intro"><div class="wrap">
<p class="kicker">Réputation et vie privée en ligne</p>
<h1>Ce que l’on trouve sur vous en ligne vous suit partout. Nous vous aidons à le faire retirer.</h1>
<div class="intro-cols">
<p>Un article dépassé qui remonte en premier quand on tape votre nom. Un faux profil qui écrit à vos partenaires. Votre adresse personnelle sur un annuaire. Nous identifions ce qui peut être retiré ou déréférencé, nous menons les démarches, et nos avocats prennent le relais quand il faut aller plus loin.</p>
<p>Nous travaillons pour des dirigeants, des entrepreneurs, des personnalités et leurs familles, avec une règle simple : personne d’autre que les intervenants du dossier ne sait que vous êtes notre client.</p>
</div>
<p class="intro-cta"><a class="btn" href="#contact">Demander un premier échange</a><span>Confidentiel et sans engagement</span></p>
</div></section>
''' + block('situations', 'Les situations que nous traitons', '<dl class="cases">' + ''.join(f'<div><dt>{esc(t)}</dt><dd>{esc(d)}</dd></div>' for t, d in situations) + '</dl><p class="aside-link"><a href="/plateformes/">Sites et plateformes concernés →</a></p>') + block('methode', 'Notre façon de travailler', '''<ol class="method">
<li><b>Un premier échange.</b> Par téléphone ou en visio. Vous nous expliquez la situation ; nous vous disons franchement ce qui peut être fait, et ce qui ne le peut pas.</li>
<li><b>Un état des lieux écrit.</b> Ce qui apparaît quand on cherche votre nom, ce qui est contestable, sur quel fondement et auprès de qui.</li>
<li><b>Une proposition.</b> Le périmètre, le calendrier et le montant, par écrit, avant tout engagement de votre part.</li>
<li><b>Les démarches, jusqu’au bout.</b> Demandes de retrait, déréférencement, relances, et compte rendu à chaque réponse obtenue.</li>
</ol>''') + block('avocats', 'Quand il faut aller plus loin', '''<p class="lead-p">Une demande amiable ne suffit pas toujours. Nous travaillons avec des avocats dans chacun des domaines qu’un dossier de réputation peut toucher, et ils interviennent dès que la situation le demande : mise en demeure, plainte, référé, action contre un hébergeur à l’étranger.</p>
<ul class="fields"><li>Droit de la presse et diffamation</li><li>Données personnelles et vie privée</li><li>Droit pénal et cybercriminalité</li><li>Propriété intellectuelle</li><li>Droit des affaires et concurrence</li><li>Procédures à l’étranger</li></ul>
<p>Vous n’avez pas à chercher le bon avocat ni à répéter votre histoire : nous transmettons le dossier, nous coordonnons, et nous restons votre interlocuteur.</p>''', 'block-dark') + block('honoraires', 'Honoraires', '<p class="lead-p">Nous ne publions pas de tarifs : deux dossiers ne se ressemblent jamais. Après le premier échange, vous recevez une proposition écrite. Les honoraires d’avocat, lorsqu’une action juridique est engagée, font l’objet d’une convention distincte que vous signez directement avec lui.</p>') + block('confidentialite', 'Confidentialité', '<p class="lead-p">Nous ne citons pas nos clients, nous ne demandons que les informations utiles et nous pouvons signer un accord de confidentialité avant tout échange sur le fond. Les avis publiés sur ce site le sont avec l’accord de leur auteur, sans élément permettant de l’identifier.</p>') + block('questions', 'Questions fréquentes', '<div class="faq">' + ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(r)}</p></details>' for q, r in faq) + '</div>') + f'''
<section class="contact" id="contact"><div class="wrap contact-in">
<div class="contact-text"><h2>Nous contacter</h2>
<p>Quelques lignes suffisent. Si vous préférez ne rien écrire de votre situation, indiquez seulement comment vous joindre : nous en parlerons de vive voix.</p>
<p>Nous vous répondons sous 24 heures ouvrées.</p></div>
<form class="form" id="contact-form" data-kind="contact" novalidate>
<div class="row2"><label>Nom<input name="name" autocomplete="name" maxlength="120" required></label>
<label>Fonction, société <span>facultatif</span><input name="organisation" autocomplete="organization-title" maxlength="160"></label></div>
<div class="row2"><label>E-mail<input name="email" type="email" autocomplete="email" maxlength="200" required></label>
<label>Téléphone <span>facultatif</span><input name="phone" type="tel" autocomplete="tel" maxlength="40"></label></div>
<label>Sujet<select name="topic">{''.join(f'<option>{esc(t)}</option>' for t in TOPICS)}</select></label>
<label>Message <span>facultatif</span><textarea name="message" maxlength="1500" rows="4"></textarea></label>
<label>Je préfère être rappelé par<select name="preferred"><option>Téléphone</option><option>E-mail</option><option>Visio</option></select></label>
<div class="hp" aria-hidden="true"><label>Société<input name="company" tabindex="-1" autocomplete="off"></label></div>
<label class="check"><input type="checkbox" name="consent" required><span>J’accepte que ces informations servent uniquement à me recontacter.</span></label>
<button class="btn" type="submit">Envoyer</button>
<p class="form-status" role="status" aria-live="polite"></p>
</form></div></section>
<script src="/assets/contact.js" defer></script>
''' + FOOTER
write('/', home)

# ---------------------------------------------------------------- avis
if avis:
    reviews = '<div class="reviews">' + ''.join(
        f'<figure class="review"><p class="stars" aria-label="{int(r.get("note", 5))} sur 5">{"★" * int(r.get("note", 5))}{"☆" * (5 - int(r.get("note", 5)))}</p>'
        f'<blockquote>{esc(r["texte"])}</blockquote><figcaption>{esc(r["auteur"])}'
        f'{f", {esc(r["date"])}" if r.get("date") else ""}</figcaption></figure>' for r in avis) + '</div>'
else:
    reviews = '<p class="empty">Aucun avis n’est encore publié. Les premiers retours de nos clients apparaîtront ici dès qu’ils nous auront donné leur accord.</p>'
avis_page = head('Avis clients — EffaceMoi', 'Les avis des clients accompagnés par EffaceMoi, publiés avec leur accord et sans élément permettant de les identifier.', '/avis/')
avis_page += f'''
<section class="page-top"><div class="wrap"><p class="crumb"><a href="/">Accueil</a> / Avis clients</p>
<h1>Avis clients</h1>
<p class="lead-p">Nos clients tiennent à leur discrétion. Leurs avis sont publiés avec leur accord, signés par leur fonction et leur secteur plutôt que par leur nom. Nous ne retouchons pas le fond et nous publions aussi les avis mitigés.</p></div></section>
<section class="block"><div class="wrap">{reviews}</div></section>
<section class="contact"><div class="wrap contact-in">
<div class="contact-text"><h2>Laisser un avis</h2>
<p>Vous avez été accompagné par EffaceMoi ? Votre retour aide d’autres personnes dans la même situation à franchir le pas.</p>
<p>Nous vous écrivons avant publication pour valider la signature et, si besoin, retirer un détail trop identifiant. Votre adresse e-mail n’est jamais affichée.</p></div>
<form class="form" id="review-form" data-kind="review" novalidate>
<label>Votre note<select name="note"><option value="5">5 sur 5</option><option value="4">4 sur 5</option><option value="3">3 sur 5</option><option value="2">2 sur 5</option><option value="1">1 sur 5</option></select></label>
<label>Votre avis<textarea name="message" maxlength="1200" rows="6" required></textarea></label>
<div class="row2"><label>Signature affichée<input name="signature" maxlength="100" placeholder="Ex. : dirigeante, secteur industriel" required></label>
<label>E-mail <span>non publié</span><input name="email" type="email" autocomplete="email" maxlength="200" required></label></div>
<input type="hidden" name="name" value="Avis client"><input type="hidden" name="topic" value="Avis client">
<div class="hp" aria-hidden="true"><label>Société<input name="company" tabindex="-1" autocomplete="off"></label></div>
<label class="check"><input type="checkbox" name="consent" required><span>J’accepte la publication de cet avis sous la signature indiquée, après validation avec moi.</span></label>
<button class="btn" type="submit">Envoyer mon avis</button>
<p class="form-status" role="status" aria-live="polite"></p>
</form></div></section>
<script src="/assets/contact.js" defer></script>
''' + FOOTER
write('/avis/', avis_page)

# ---------------------------------------------------------------- périmètre
platforms = [('Google, Bing', 'Résultats associés à votre nom, images, suggestions de recherche.'),
             ('Presse en ligne', 'Articles inexacts, dépassés ou diffamatoires : actualisation, droit de réponse, retrait.'),
             ('LinkedIn, X, Instagram, Facebook, TikTok, YouTube', 'Faux profils, publications vous mettant en cause, images diffusées sans accord.'),
             ('Forums et sites d’avis', 'Avis dénigrants, discussions diffamatoires, commentaires indexés.'),
             ('Annuaires et sites de données', 'Adresse, téléphone, informations sur vos proches ou votre patrimoine.'),
             ('Sites hébergés à l’étranger', 'Hébergeurs, bureaux d’enregistrement et éditeurs hors de France, avec des avocats habitués à ces procédures.')]
perimetre = head('Périmètre — EffaceMoi', 'Moteurs de recherche, presse en ligne, réseaux sociaux, forums, annuaires, sites étrangers : où EffaceMoi intervient.', '/plateformes/')
perimetre += f'''
<section class="page-top"><div class="wrap"><p class="crumb"><a href="/">Accueil</a> / Périmètre</p>
<h1>Où nous intervenons</h1>
<p class="lead-p">Chaque site a ses règles, et le droit applicable change selon l’endroit où il est hébergé. Voici les cas les plus fréquents ; les autres s’étudient au cas par cas.</p></div></section>
''' + block('', 'Sites et plateformes', '<dl class="cases">' + ''.join(f'<div><dt>{esc(t)}</dt><dd>{esc(d)}</dd></div>' for t, d in platforms) + '</dl><p class="small">EffaceMoi n’est affilié à aucune de ces plateformes et n’y dispose d’aucun accès privilégié. Chaque demande est examinée par son destinataire.</p><p><a class="btn" href="/#contact">Nous contacter</a></p>') + FOOTER
write('/plateformes/', perimetre)

# ---------------------------------------------------------------- ressources
related_map = {
    'supprimer-leak-onlyfans': ['demande-retrait-dmca', 'suivre-demande-retrait', 'supprimer-resultat-google'],
    'photo-intime-sans-consentement': ['doxxing-donnees-exposees', 'signaler-usurpation-identite', 'supprimer-resultat-google'],
    'supprimer-donnees-personnelles-internet': ['doxxing-donnees-exposees', 'supprimer-resultat-google', 'suivre-demande-retrait'],
    'supprimer-resultat-google': ['supprimer-donnees-personnelles-internet', 'photo-intime-sans-consentement', 'suivre-demande-retrait'],
    'demande-retrait-dmca': ['supprimer-leak-onlyfans', 'suivre-demande-retrait', 'photo-intime-sans-consentement'],
    'signaler-usurpation-identite': ['doxxing-donnees-exposees', 'supprimer-donnees-personnelles-internet', 'suivre-demande-retrait'],
    'doxxing-donnees-exposees': ['supprimer-donnees-personnelles-internet', 'signaler-usurpation-identite', 'supprimer-resultat-google'],
    'suivre-demande-retrait': ['demande-retrait-dmca', 'supprimer-resultat-google', 'supprimer-donnees-personnelles-internet'],
    'deepfake-image-intime-retrait': ['photo-intime-sans-consentement', 'supprimer-resultat-google', 'conserver-preuves-contenu-en-ligne'],
    'retirer-photo-personnelle-google': ['supprimer-resultat-google', 'supprimer-donnees-personnelles-internet', 'photo-intime-sans-consentement'],
    'proteger-contenu-createur-copies': ['supprimer-leak-onlyfans', 'demande-retrait-dmca', 'conserver-preuves-contenu-en-ligne'],
    'conserver-preuves-contenu-en-ligne': ['suivre-demande-retrait', 'signaler-usurpation-identite', 'proteger-contenu-createur-copies']}

for a in articles:
    path = '/blog/' + a['slug'] + '/'
    schema = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BlogPosting', 'headline': a['title'], 'description': a['description'], 'datePublished': a.get('published', '2026-10-25'),
         'dateModified': UPDATED, 'wordCount': a['words'], 'inLanguage': 'fr-FR', 'author': {'@type': 'Organization', 'name': 'EffaceMoi', 'url': ORIGIN},
         'publisher': {'@type': 'Organization', 'name': 'EffaceMoi', 'url': ORIGIN}, 'mainEntityOfPage': ORIGIN + path},
        {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': ORIGIN + '/'},
                                                        {'@type': 'ListItem', 'position': 2, 'name': 'Ressources', 'item': ORIGIN + '/blog/'},
                                                        {'@type': 'ListItem', 'position': 3, 'name': a['title'], 'item': ORIGIN + path}]}]}
    toc = ''.join(f'<li><a href="#etape-{i}">{esc(h)}</a></li>' for i, (h, b) in enumerate(a['sections'], 1))
    body = ''.join(f'<section id="etape-{i}"><h2>{esc(h)}</h2>{b}</section>' for i, (h, b) in enumerate(a['sections'], 1))
    sources = ''.join(f'<li><a href="{esc(u)}">{esc(n)}</a></li>' for n, u in a['sources'])
    related = ''.join(f'<li><a href="/blog/{s}/">{esc(by_slug[s]["title"])}</a></li>' for s in related_map[a['slug']])
    page = head(a['title'] + ' | EffaceMoi', a['description'], path, schema, 'article') + f'''
<article class="article"><div class="wrap">
<header class="article-head"><p class="crumb"><a href="/">Accueil</a> / <a href="/blog/">Ressources</a> / {esc(a['cat'])}</p>
<h1>{esc(a['title'])}</h1><p class="meta">{esc(a['cat'])} · mis à jour le 26 octobre 2026 · {a['minutes']} min de lecture</p></header>
<div class="article-grid"><aside class="toc"><p>Sommaire</p><ol>{toc}</ol></aside>
<div class="prose"><p class="lead-p">{a['intro']}</p>{body}
<section class="sources"><h2>Sources</h2><ul>{sources}</ul><p class="small">Les formulaires et critères évoluent : vérifiez les indications du destinataire au moment de votre démarche. Ces informations générales ne remplacent pas un conseil adapté à votre situation.</p></section>
<aside class="note-box"><p><b>Vous préférez déléguer ?</b> Nous menons ces démarches pour vous et faisons intervenir un avocat lorsque c’est nécessaire. <a href="/#contact">Nous contacter</a></p></aside>
<section class="related"><h2>À lire aussi</h2><ul>{related}</ul></section>
</div></div></div></article>''' + FOOTER
    write(path, page)

listing = ''.join(f'<li><a href="/blog/{a["slug"]}/"><span class="meta">{esc(a["cat"])} · {a["minutes"]} min</span><b>{esc(a["title"])}</b><span>{esc(a["description"])}</span></a></li>' for a in articles)
blog_schema = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Ressources EffaceMoi', 'url': ORIGIN + '/blog/',
               'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i, 'url': ORIGIN + '/blog/' + a['slug'] + '/', 'name': a['title']} for i, a in enumerate(articles, 1)]}}
write('/blog/', head('Ressources : retrait, déréférencement, données personnelles | EffaceMoi',
                     'Guides pratiques pour comprendre les recours : déréférencement, retrait de contenus, données personnelles exposées, usurpation d’identité.',
                     '/blog/', blog_schema) + f'''
<section class="page-top"><div class="wrap"><p class="crumb"><a href="/">Accueil</a> / Ressources</p>
<h1>Ressources</h1><p class="lead-p">Des guides pour comprendre qui saisir, sur quel fondement, et comment suivre la réponse. Chaque guide cite les sources officielles.</p></div></section>
<section class="block"><div class="wrap"><ul class="posts">{listing}</ul></div></section>''' + FOOTER)

# ---------------------------------------------------------------- sitemap, robots
urls = ['/', '/avis/', '/plateformes/', '/blog/'] + ['/blog/' + a['slug'] + '/' for a in articles]
(DIST / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                  + ''.join(f'<url><loc>{ORIGIN}{u}</loc><lastmod>{UPDATED}</lastmod></url>' for u in urls) + '</urlset>')
(DIST / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n')
print(f'{len(urls)} pages générées')
