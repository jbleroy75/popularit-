# EffaceMoi

Site vitrine de présentation d’un service d’accompagnement pour les demandes de retrait de contenus intimes diffusés sans consentement et de données personnelles exposées en ligne.

## Contenu

- `dist/` : pages statiques prêtes à publier
- `content/blog.json` : contenus éditoriaux
- `scripts/build.py` : génère tout le site (accueil, avis, périmètre, ressources, sitemap)
- `content/expertises.json` : pages détaillées par situation (/expertises/…)
- `content/avis.json` : avis clients publiés (réels, avec accord, anonymisés)

Le service présenté sur le site n’implique aucun partenariat officiel avec les plateformes citées et ne garantit pas le retrait des contenus.

## Hébergement

Cloudflare Workers (static assets), Worker `effacemoi`, domaine https://effacemoi.jbleroy.fr (`wrangler.jsonc`).
Chaque push sur `main` redéploie via `.github/workflows/deploy-cloudflare.yml` (secret `CLOUDFLARE_API_TOKEN`).
