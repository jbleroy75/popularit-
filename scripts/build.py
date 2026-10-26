"""Génère tout le site statique dans dist/ : accueil, avis, périmètre, blog et articles, sitemap, robots.

Usage : python3 scripts/build.py
Contenus éditoriaux : content/blog.json (articles), content/avis.json (avis clients publiés avec accord).
"""
from pathlib import Path
from html.parser import HTMLParser
import json, html, math, shutil

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
NAV = [('/#expertises', 'Expertises'), ('/#avocats', 'Avocats'), ('/#methode', 'Méthode'),
       ('/avis/', 'Avis'), ('/blog/', 'Ressources')]


def head(title, description, path, schema=None, og_type='website'):
    ld = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")}</script>' if schema else ''
    return f'''<!doctype html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{ORIGIN}{path}">
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{ORIGIN}{path}"><meta property="og:locale" content="fr_FR"><meta name="theme-color" content="#0d1726">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230d1726'/%3E%3Ctext x='16' y='23' font-family='Georgia,serif' font-size='20' text-anchor='middle' fill='%23c9a96e'%3EE%3C/text%3E%3C/svg%3E">
<link rel="preload" href="/assets/fonts/cormorant-500.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/assets/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">{ld}</head><body>
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="topbar"><div class="wrap topbar-in"><a href="/" class="logo">EffaceMoi<small>Réputation &amp; vie privée</small></a>
<nav aria-label="Navigation principale">{''.join(f'<a href="{h}">{t}</a>' for h, t in NAV)}</nav>
<a class="btn btn-light" href="/#contact">Entretien confidentiel</a></div></header>
<main id="contenu">'''


FOOTER = f'''</main>
<footer class="footer"><div class="wrap">
<div class="footer-top"><div><a href="/" class="logo">EffaceMoi<small>Réputation &amp; vie privée</small></a>
<p>Protection de la réputation en ligne des dirigeants, entrepreneurs et personnalités. Intervention discrète, appuyée par un réseau d’avocats spécialisés.</p></div>
<div class="footer-cols"><div><strong>Cabinet</strong><a href="/#expertises">Expertises</a><a href="/#avocats">Avocats partenaires</a><a href="/#methode">Méthode</a><a href="/plateformes/">Périmètre</a></div>
<div><strong>Ressources</strong><a href="/blog/">Guides</a><a href="/avis/">Avis clients</a><a href="/#questions">Questions fréquentes</a></div>
<div><strong>Contact</strong><a href="/#contact">Entretien confidentiel</a><span>Réponse sous 24 h ouvrées</span></div></div></div>
<div class="footer-bottom"><span>© 2026 EffaceMoi</span><span>Aucun résultat n’est garanti : les décisions appartiennent aux plateformes, moteurs de recherche et juridictions. EffaceMoi n’est affilié à aucune plateforme citée.</span></div>
</div></footer></body></html>'''


def section_head(num, eyebrow, title, intro=''):
    mark = f'<span>{num}</span>' if num else ''
    return (f'<div class="sec-head"><div class="eyebrow">{mark}{eyebrow}</div><h2>{title}</h2>'
            + (f'<p>{intro}</p>' if intro else '') + '</div>')


def write(path, content):
    f = DIST / path.strip('/') / 'index.html' if path != '/' else DIST / 'index.html'
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content)


# ---------------------------------------------------------------- accueil
PREVIEW = ['supprimer-resultat-google', 'signaler-usurpation-identite', 'supprimer-donnees-personnelles-internet']
TOPICS = ['Contenus diffamatoires ou dénigrants', 'Résultats de recherche préjudiciables', 'Données personnelles exposées',
          'Usurpation d’identité ou faux profil', 'Images ou vidéos diffusées sans accord', 'Veille et protection continue',
          'Partager mon avis', 'Autre situation']

home_schema = {'@context': 'https://schema.org', '@type': 'ProfessionalService', 'name': 'EffaceMoi', 'url': ORIGIN + '/',
               'description': 'Protection de la réputation en ligne des dirigeants et personnalités, avec un réseau d’avocats spécialisés.',
               'areaServed': 'FR', 'knowsLanguage': 'fr'}

expertises = [
    ('Contenus diffamatoires et dénigrement', 'Articles, avis, publications ou forums qui portent atteinte à votre honneur ou à celui de votre entreprise. Qualification des propos, demandes de retrait auprès des éditeurs et hébergeurs, action judiciaire lorsque nécessaire.'),
    ('Résultats de recherche', 'Résultats associés à votre nom qui sont obsolètes, inexacts ou excessifs. Demandes de déréférencement fondées sur le RGPD et le droit à l’oubli, et recours lorsque la réponse ne convient pas.'),
    ('Données personnelles exposées', 'Adresse, téléphone, informations familiales ou patrimoniales publiées ou revendues par des annuaires et courtiers en données. Effacement, opposition et suivi des republications.'),
    ('Usurpation d’identité', 'Faux profils, comptes trompeurs ou sites utilisant votre nom, votre image ou votre marque. Signalements auprès des plateformes, conservation des preuves et dépôt de plainte accompagné.'),
    ('Atteintes à la vie privée et à l’image', 'Photos, vidéos ou informations intimes diffusées sans votre accord, y compris les montages et contenus générés par IA. Traitement prioritaire et entièrement confidentiel.'),
    ('Fuites et contenus copiés', 'Documents internes, échanges privés ou contenus protégés reproduits sans autorisation. Notifications aux hébergeurs et actions fondées sur le droit d’auteur ou le secret des affaires.'),
]
lawyer_fields = [
    ('Droit de la presse', 'Diffamation, injure, droit de réponse'),
    ('Vie privée et données', 'RGPD, droit à l’image, déréférencement'),
    ('Pénal du numérique', 'Plaintes, harcèlement, usurpation'),
    ('Propriété intellectuelle', 'Droit d’auteur, marques, contrefaçon'),
    ('Droit des affaires', 'Dénigrement, concurrence, secret des affaires'),
    ('Contentieux international', 'Hébergeurs et éditeurs situés à l’étranger'),
]
steps = [
    ('Entretien confidentiel', 'Un échange avec votre interlocuteur dédié pour comprendre la situation, les enjeux et l’urgence. Sans engagement.'),
    ('Audit d’exposition', 'Cartographie de ce qui est publié sur vous : moteurs de recherche, presse, réseaux sociaux, forums, annuaires.'),
    ('Stratégie et proposition', 'Plan d’action priorisé, voies amiables et juridiques, calendrier et honoraires présentés avant tout engagement.'),
    ('Intervention', 'Demandes de retrait et de déréférencement, mises en demeure et procédures conduites par nos avocats lorsque nécessaire.'),
    ('Veille et compte rendu', 'Suivi des réponses, contrôle des republications et rapport confidentiel à chaque étape.'),
]
offers = [
    ('Audit de réputation', 'Pour savoir précisément ce qui circule sur vous ou votre entreprise.', ['Analyse des résultats associés à votre nom', 'Identification des contenus à risque', 'Recommandations hiérarchisées', 'Restitution confidentielle']),
    ('Intervention ciblée', 'Pour traiter un ou plusieurs contenus préjudiciables identifiés.', ['Stratégie amiable et juridique', 'Demandes de retrait et de déréférencement', 'Avocat spécialisé selon le dossier', 'Suivi jusqu’à la décision']),
    ('Protection continue', 'Pour les dirigeants et familles exposés dans la durée.', ['Veille de votre nom et de vos proches', 'Alerte et traitement rapides', 'Interlocuteur dédié joignable', 'Bilan périodique']),
]
faq = [
    ('Pouvez-vous garantir la suppression d’un contenu ?', 'Non, et nous nous méfions de quiconque le promet. La décision appartient à l’éditeur, à l’hébergeur, au moteur de recherche ou au juge. Notre rôle est de choisir les bons fondements, de constituer un dossier solide et de mener chaque démarche jusqu’à son terme, avec nos avocats lorsque la voie juridique s’impose.'),
    ('Comment est préservée la confidentialité ?', 'Votre dossier est suivi par un interlocuteur unique et partagé avec le seul avocat concerné. Nous ne publions aucune référence client et un accord de confidentialité peut être signé dès le premier échange.'),
    ('Quels sont vos honoraires ?', 'Ils dépendent du nombre de contenus, des plateformes concernées et de la nécessité d’une action judiciaire. Ils vous sont présentés par écrit, après l’entretien, avant tout engagement. Les éventuels honoraires d’avocat font l’objet d’une convention distincte.'),
    ('Supprimer et déréférencer, est-ce la même chose ?', 'Non. La suppression agit sur la page d’origine, chez l’éditeur ou l’hébergeur. Le déréférencement retire le lien des résultats d’un moteur de recherche pour une requête donnée ; la page peut rester accessible. Les deux démarches sont souvent menées ensemble.'),
    ('Intervenez-vous pour une entreprise ou pour mes proches ?', 'Oui. Nous accompagnons aussi les entreprises dont la réputation est mise en cause, ainsi que les familles de dirigeants exposées en ligne.'),
    ('En combien de temps pouvez-vous agir ?', 'Les premières mesures (conservation des preuves, signalements urgents) peuvent être engagées dès la validation de la proposition. Les délais de réponse dépendent ensuite de chaque plateforme ou juridiction.'),
]

home = head('EffaceMoi — Protection de la réputation en ligne des dirigeants',
            'Contenus diffamatoires, résultats de recherche, données exposées, usurpation : EffaceMoi protège la réputation en ligne des dirigeants et personnalités, avec un réseau d’avocats spécialisés.',
            '/', home_schema)
home += f'''
<section class="hero"><div class="wrap hero-in">
<div class="hero-copy">
<div class="eyebrow light">Dirigeants · Entrepreneurs · Personnalités</div>
<h1>Votre réputation se défend <em>avec discrétion.</em></h1>
<p class="hero-lead">Contenus diffamatoires, résultats de recherche préjudiciables, informations privées exposées : nous reprenons la maîtrise de ce qui est publié sur vous, avec un réseau d’avocats spécialisés qui engagent les actions nécessaires.</p>
<div class="hero-cta"><a class="btn btn-gold" href="#contact">Demander un entretien confidentiel</a><a class="link-light" href="#methode">Découvrir notre méthode →</a></div>
<ul class="hero-proof"><li>Interlocuteur unique</li><li>Avocats spécialisés dans chaque domaine</li><li>Confidentialité absolue</li></ul>
</div>
<aside class="dossier" aria-label="Exemple de livrable : audit d’exposition">
<div class="dossier-head"><span>Audit d’exposition</span><span class="stamp">Confidentiel</span></div>
<p class="dossier-sub">Exemple de restitution</p>
<ol class="dossier-list">
<li><span>Résultats associés au nom</span><b class="lvl lvl-3">Prioritaire</b></li>
<li><span>Articles et publications en cause</span><b class="lvl lvl-2">À traiter</b></li>
<li><span>Données personnelles exposées</span><b class="lvl lvl-3">Prioritaire</b></li>
<li><span>Faux profils et usurpations</span><b class="lvl lvl-1">Sous veille</b></li>
</ol>
<div class="dossier-foot"><span>Voies d’action</span><p>Retrait amiable · Déréférencement · Mise en demeure · Procédure</p></div>
</aside>
</div></section>

<section class="band"><div class="wrap band-in"><span>Ce que nous protégeons</span><ul><li>Votre nom</li><li>Votre image</li><li>Votre vie privée</li><li>Votre entreprise</li><li>Vos proches</li></ul></div></section>

<section class="sec" id="pour-qui"><div class="wrap">
{section_head('I', 'Pour qui', 'Ceux dont le nom <em>engage davantage.</em>', 'Quand une publication touche un dirigeant, elle touche aussi une entreprise, des équipes, des partenaires et une famille. Nos interventions sont pensées pour ces enjeux.')}
<div class="audience">
<article><h3>Dirigeants et mandataires</h3><p>Présidents, directeurs généraux, administrateurs dont la réputation conditionne la confiance des actionnaires, des banques et des équipes.</p></article>
<article><h3>Entrepreneurs et investisseurs</h3><p>Fondateurs, associés et investisseurs exposés lors d’une levée de fonds, d’une cession ou d’un conflit.</p></article>
<article><h3>Personnalités publiques</h3><p>Personnalités, créateurs et professions exposées qui doivent séparer vie publique et vie privée.</p></article>
<article><h3>Familles et patrimoines</h3><p>Familles d’affaires et proches de dirigeants dont l’adresse, les biens ou la vie privée circulent en ligne.</p></article>
</div></div></section>

<section class="sec sec-alt" id="expertises"><div class="wrap">
{section_head('II', 'Expertises', 'Chaque atteinte appelle <em>la bonne réponse.</em>', 'Nous qualifions d’abord la situation : le fondement juridique et l’interlocuteur pertinent déterminent l’efficacité de la démarche.')}
<div class="expertises">{''.join(f'<article><span class="num">{i:02d}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></article>' for i, (t, d) in enumerate(expertises, 1))}</div>
</div></section>

<section class="sec sec-dark" id="avocats"><div class="wrap lawyers">
<div class="lawyers-copy">
<div class="eyebrow light"><span>III</span>Le réseau juridique</div>
<h2>Des avocats dans chaque domaine, <em>prêts à agir.</em></h2>
<p>Une atteinte à la réputation n’est jamais un sujet unique : elle mêle droit de la presse, protection des données, pénal, propriété intellectuelle et parfois droit étranger. C’est pourquoi nous travaillons avec un réseau d’avocats, chacun spécialiste de son domaine.</p>
<p>Lorsque la voie amiable ne suffit pas, l’avocat compétent prend le relais et fait le nécessaire : mise en demeure, requête auprès de l’hébergeur, plainte, procédure en référé. Vous gardez un seul interlocuteur ; nous coordonnons l’ensemble.</p>
<a class="btn btn-gold" href="#contact">Exposer ma situation</a>
</div>
<div class="fields">{''.join(f'<div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for t, d in lawyer_fields)}</div>
</div></section>

<section class="sec" id="methode"><div class="wrap">
{section_head('IV', 'Méthode', 'Une démarche <em>structurée</em>, de l’entretien au compte rendu.')}
<ol class="steps">{''.join(f'<li><span class="num">{i:02d}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></li>' for i, (t, d) in enumerate(steps, 1))}</ol>
</div></section>

<section class="sec sec-alt" id="accompagnements"><div class="wrap">
{section_head('V', 'Accompagnements', 'Un dispositif <em>à la mesure</em> de votre situation.', 'Chaque mission est construite après l’entretien. Le périmètre, le calendrier et les honoraires vous sont présentés par écrit avant tout engagement.')}
<div class="offers">{''.join(f'<article><h3>{esc(t)}</h3><p>{esc(d)}</p><ul>{"".join(f"<li>{esc(x)}</li>" for x in items)}</ul><a href="#contact">Sur proposition →</a></article>' for t, d, items in offers)}</div>
</div></section>

<section class="sec" id="engagements"><div class="wrap">
{section_head('VI', 'Engagements', 'La discrétion <em>n’est pas une option.</em>')}
<div class="pledges">
<div><h3>Aucune référence publiée</h3><p>Nous ne citons jamais nos clients. Les avis publiés le sont uniquement avec l’accord de leur auteur, sous forme anonymisée.</p></div>
<div><h3>Un accord de confidentialité</h3><p>Il peut être signé dès le premier échange, avant même que vous nous exposiez les détails de votre situation.</p></div>
<div><h3>Le strict nécessaire</h3><p>Nous ne demandons que les informations utiles au dossier, et vos éléments ne sont partagés qu’avec l’avocat concerné.</p></div>
<div><h3>Une parole honnête</h3><p>Aucun résultat n’est promis. Nous vous disons ce qui est réaliste, ce qui ne l’est pas, et pourquoi.</p></div>
</div></div></section>

<section class="sec sec-alt blog-preview"></section>

<section class="sec" id="questions"><div class="wrap faq">
{section_head('VII', 'Questions', 'Avant notre <em>premier échange.</em>')}
<div class="faq-list">{''.join(f'<details><summary>{esc(q)}</summary><p>{esc(r)}</p></details>' for q, r in faq)}</div>
</div></section>

<section class="sec sec-dark" id="contact"><div class="wrap contact">
<div class="contact-copy">
<div class="eyebrow light"><span>VIII</span>Entretien confidentiel</div>
<h2>Parlons de votre situation, <em>en toute discrétion.</em></h2>
<p>Indiquez simplement comment vous joindre et la nature du sujet. Inutile de détailler votre situation ici : nous en parlerons de vive voix.</p>
<ol class="next"><li><b>Sous 24 h ouvrées</b>Votre interlocuteur dédié vous recontacte par le moyen que vous avez choisi.</li><li><b>Premier entretien</b>Un échange sans engagement, couvert par un accord de confidentialité si vous le souhaitez.</li><li><b>Proposition écrite</b>Stratégie, calendrier et honoraires, avant toute intervention.</li></ol>
</div>
<form class="contact-form" id="contact-form" novalidate>
<div class="grid2"><label>Nom ou initiales<input name="name" autocomplete="name" maxlength="120" required></label>
<label>Fonction / organisation <span>(facultatif)</span><input name="organisation" autocomplete="organization-title" maxlength="160"></label></div>
<div class="grid2"><label>E-mail<input name="email" type="email" autocomplete="email" maxlength="200" required></label>
<label>Téléphone <span>(facultatif)</span><input name="phone" type="tel" autocomplete="tel" maxlength="40"></label></div>
<label>Nature de la situation<select name="topic">{''.join(f'<option>{esc(t)}</option>' for t in TOPICS)}</select></label>
<label>Message <span>(facultatif, restez général)</span><textarea name="message" maxlength="1500" rows="4" placeholder="Quelques mots de contexte, vos disponibilités…"></textarea></label>
<label>Être recontacté par<select name="preferred"><option>Téléphone</option><option>E-mail</option><option>Visioconférence</option></select></label>
<div class="hp" aria-hidden="true"><label>Société<input name="company" tabindex="-1" autocomplete="off"></label></div>
<label class="consent"><input type="checkbox" name="consent" required><span>J’accepte que ces informations soient utilisées pour me recontacter. Elles ne sont ni cédées ni utilisées à d’autres fins.</span></label>
<button class="btn btn-gold" type="submit">Demander un entretien</button>
<p class="form-status" role="status" aria-live="polite"></p>
</form>
</div></section>
<script src="/assets/contact.js" defer></script>
''' + FOOTER
cards = ''.join(f'<a class="guide" href="/blog/{s}/"><span class="guide-cat">{esc(by_slug[s]["cat"])} · {by_slug[s]["minutes"]} min</span><strong>{esc(by_slug[s]["title"])}</strong><span class="guide-go">Lire le guide →</span></a>' for s in PREVIEW)
home = home.replace('<section class="sec sec-alt blog-preview"></section>', f'''<section class="sec sec-alt blog-preview"><div class="wrap">
<div class="sec-head row"><div><div class="eyebrow">Ressources</div><h2>Comprendre <em>vos recours.</em></h2></div><a class="more" href="/blog/">Tous les guides →</a></div>
<div class="guides">{cards}</div></div></section>''')
write('/', home)

# ---------------------------------------------------------------- avis
if avis:
    reviews = '<div class="reviews">' + ''.join(
        f'<figure class="review"><div class="stars" aria-label="{r.get("note", 5)} sur 5">{"★" * int(r.get("note", 5))}</div>'
        f'<blockquote>{esc(r["texte"])}</blockquote><figcaption><b>{esc(r["auteur"])}</b>{esc(r.get("contexte", ""))}'
        f'{f" · {esc(r["date"])}" if r.get("date") else ""}</figcaption></figure>' for r in avis) + '</div>'
else:
    reviews = '''<div class="reviews-empty"><h2>Les premiers témoignages <em>arrivent.</em></h2><p>Nos clients attachent, par définition, une grande importance à leur discrétion. Nous publierons ici leurs retours dès qu’ils nous auront donné leur accord, sous une forme qui ne permet pas de les identifier.</p></div>'''
avis_page = head('Avis clients — EffaceMoi', 'Avis de clients accompagnés par EffaceMoi pour protéger leur réputation en ligne, publiés avec leur accord et sous forme anonymisée.', '/avis/')
avis_page += f'''
<section class="page-head"><div class="wrap"><div class="crumb"><a href="/">Accueil</a> / Avis clients</div>
<div class="eyebrow">Avis clients</div><h1>Ce que nos clients <em>en disent.</em></h1>
<p class="lead">Des retours authentiques, publiés avec l’accord de leurs auteurs. Pour préserver leur discrétion, les noms sont remplacés par la fonction et le secteur d’activité.</p></div></section>
<section class="sec sec-tight"><div class="wrap">{reviews}</div></section>
<section class="sec sec-alt"><div class="wrap">
{section_head('', 'Notre charte', 'Des avis <em>vérifiables par nous, anonymes pour vous.</em>')}
<div class="pledges">
<div><h3>Clients réels uniquement</h3><p>Seules les personnes que nous avons effectivement accompagnées peuvent laisser un avis.</p></div>
<div><h3>Accord écrit</h3><p>Aucun avis n’est publié sans l’accord explicite de son auteur, qui peut demander son retrait à tout moment.</p></div>
<div><h3>Anonymisation</h3><p>Nom, entreprise et détails du dossier sont retirés : seuls la fonction et le secteur apparaissent.</p></div>
<div><h3>Aucun tri</h3><p>Nous ne modifions pas le fond des avis et ne publions pas uniquement les plus favorables.</p></div>
</div></div></section>
<section class="sec sec-dark"><div class="wrap cta-band"><div><div class="eyebrow light">Vous avez été accompagné ?</div><h2>Partagez <em>votre retour.</em></h2><p>Quelques lignes suffisent. Nous vous recontactons pour valider avec vous la version publiée.</p></div><a class="btn btn-gold" href="/?sujet=avis#contact">Laisser un avis</a></div></section>
''' + FOOTER
write('/avis/', avis_page)

# ---------------------------------------------------------------- périmètre
platforms = [('Google et Bing', 'Déréférencement de résultats associés à votre nom, suggestions de recherche, images.'),
             ('Presse en ligne', 'Articles inexacts, obsolètes ou diffamatoires : droit de réponse, actualisation, retrait.'),
             ('Réseaux sociaux', 'LinkedIn, X, Instagram, Facebook, TikTok, YouTube : signalements, faux profils, contenus publiés sans accord.'),
             ('Forums et sites d’avis', 'Avis dénigrants, discussions diffamatoires, fils de commentaires indexés.'),
             ('Annuaires et courtiers en données', 'Adresse, téléphone, informations sur les proches : effacement et opposition.'),
             ('Sites hébergés à l’étranger', 'Hébergeurs, registrars et éditeurs hors de France, avec l’appui d’avocats habitués aux procédures internationales.')]
perimetre = head('Périmètre d’intervention — EffaceMoi', 'Moteurs de recherche, presse en ligne, réseaux sociaux, forums, annuaires : le périmètre d’intervention d’EffaceMoi pour protéger votre réputation.', '/plateformes/')
perimetre += f'''
<section class="page-head"><div class="wrap"><div class="crumb"><a href="/">Accueil</a> / Périmètre</div>
<div class="eyebrow">Périmètre d’intervention</div><h1>Partout où <em>votre nom apparaît.</em></h1>
<p class="lead">Chaque support obéit à ses propres règles et à son propre droit. Nous identifions l’interlocuteur compétent et le fondement adapté, puis nos avocats prennent le relais lorsque la voie amiable ne suffit pas.</p></div></section>
<section class="sec sec-tight"><div class="wrap"><div class="expertises">{''.join(f'<article><span class="num">{i:02d}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></article>' for i, (t, d) in enumerate(platforms, 1))}</div>
<p class="fineprint">EffaceMoi n’est affilié à aucune des plateformes citées et ne dispose d’aucun accès privilégié à leurs services. Chaque demande est examinée par son destinataire, sans garantie de résultat ni de délai.</p></div></section>
<section class="sec sec-dark"><div class="wrap cta-band"><div><div class="eyebrow light">Un autre support ?</div><h2>Chaque situation <em>s’étudie.</em></h2><p>Le périmètre n’est pas limité à ces exemples. Exposez-nous le cas lors d’un entretien confidentiel.</p></div><a class="btn btn-gold" href="/#contact">Demander un entretien</a></div></section>
''' + FOOTER
write('/plateformes/', perimetre)

# ---------------------------------------------------------------- blog
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
    related = ''.join(f'<a class="guide" href="/blog/{s}/"><span class="guide-cat">{esc(by_slug[s]["cat"])}</span><strong>{esc(by_slug[s]["title"])}</strong><span class="guide-go">Lire →</span></a>' for s in related_map[a['slug']])
    page = head(a['title'] + ' | EffaceMoi', a['description'], path, schema, 'article') + f'''
<article class="article"><div class="wrap">
<header class="article-head"><div class="crumb"><a href="/">Accueil</a> / <a href="/blog/">Ressources</a> / {esc(a['cat'])}</div>
<div class="eyebrow">{esc(a['cat'])} · Guide pratique</div><h1>{esc(a['title'])}</h1>
<p class="meta">Mis à jour le 26 octobre 2026 · {a['minutes']} min de lecture</p><p class="lead">{a['intro']}</p></header>
<div class="article-layout"><aside class="toc"><strong>Sommaire</strong><ol>{toc}</ol></aside>
<div class="article-body">{body}
<section class="sources"><h2>Sources officielles</h2><ul>{sources}</ul><p class="note">Les formulaires et critères évoluent : vérifiez les indications du destinataire au moment de votre démarche. Ces informations générales ne remplacent pas un conseil adapté à votre situation.</p></section>
<aside class="article-cta"><div class="eyebrow light">Besoin d’être accompagné ?</div><h2>Confiez-nous <em>la démarche.</em></h2><p>Nous qualifions la situation, menons les demandes et faisons intervenir l’avocat compétent lorsque c’est nécessaire.</p><a class="btn btn-gold" href="/#contact">Demander un entretien confidentiel</a></aside>
</div></div>
<section class="related"><h2>À lire aussi</h2><div class="guides">{related}</div></section>
</div></article>''' + FOOTER
    write(path, page)

listing = ''.join(f'<a class="post" href="/blog/{a["slug"]}/"><span class="guide-cat">{esc(a["cat"])} · {a["minutes"]} min</span><h2>{esc(a["title"])}</h2><p>{esc(a["description"])}</p><span class="guide-go">Lire le guide →</span></a>' for a in articles)
blog_schema = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Ressources EffaceMoi', 'url': ORIGIN + '/blog/',
               'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i, 'url': ORIGIN + '/blog/' + a['slug'] + '/', 'name': a['title']} for i, a in enumerate(articles, 1)]}}
write('/blog/', head('Ressources : réputation en ligne, retrait et déréférencement | EffaceMoi',
                     'Guides détaillés pour comprendre les recours : déréférencement, retrait de contenus, données personnelles exposées, usurpation d’identité.',
                     '/blog/', blog_schema) + f'''
<section class="page-head"><div class="wrap"><div class="crumb"><a href="/">Accueil</a> / Ressources</div>
<div class="eyebrow">Ressources · {len(articles)} guides</div><h1>Comprendre <em>vos recours.</em></h1>
<p class="lead">Quel interlocuteur saisir, sur quel fondement, et comment suivre la réponse. Des guides détaillés, appuyés sur les sources officielles.</p></div></section>
<section class="sec sec-tight"><div class="wrap posts">{listing}</div></section>''' + FOOTER)

# ---------------------------------------------------------------- sitemap, robots
urls = ['/', '/avis/', '/plateformes/', '/blog/'] + ['/blog/' + a['slug'] + '/' for a in articles]
(DIST / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                  + ''.join(f'<url><loc>{ORIGIN}{u}</loc><lastmod>{UPDATED}</lastmod></url>' for u in urls) + '</urlset>')
(DIST / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n')
print(f'{len(urls)} pages générées')
