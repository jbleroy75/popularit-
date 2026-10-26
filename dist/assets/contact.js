// Formulaire « Entretien confidentiel » : envoi au relais leads (Worker leads-relay, kind "contact").
(() => {
  const form = document.getElementById('contact-form');
  if (!form) return;
  const status = form.querySelector('.form-status');
  const button = form.querySelector('button[type=submit]');
  const startedAt = Date.now();
  if (new URLSearchParams(location.search).get('sujet') === 'avis') form.topic.value = 'Partager mon avis';

  const say = (msg, ok) => { status.textContent = msg; status.dataset.state = ok ? 'ok' : 'error'; };

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!form.name.value.trim()) return say('Indiquez votre nom ou vos initiales.'), form.name.focus();
    if (!form.email.checkValidity() || !form.email.value) return say('Indiquez une adresse e-mail valide.'), form.email.focus();
    if (!form.consent.checked) return say('Merci de cocher la case d’accord pour être recontacté.'), form.consent.focus();
    button.disabled = true;
    say('Envoi en cours…', true);
    const data = Object.fromEntries(['name', 'organisation', 'email', 'phone', 'topic', 'message', 'preferred', 'company']
      .map((k) => [k, form[k].value]));
    try {
      const r = await fetch('https://leads.jbleroy.fr/api/lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, kind: 'contact', consent: true, formStartedAt: startedAt, pageUrl: location.href }),
      });
      const res = await r.json().catch(() => ({}));
      if (r.ok && res.ok) {
        form.reset();
        say('Merci. Votre demande a bien été reçue : votre interlocuteur vous recontacte sous 24 h ouvrées.', true);
      } else if (r.status === 429) {
        say('Trop de demandes envoyées depuis cette connexion. Réessayez dans une heure.');
      } else {
        say('L’envoi n’a pas abouti. Vérifiez les champs puis réessayez.');
      }
    } catch {
      say('Connexion impossible pour le moment. Réessayez dans quelques instants.');
    } finally {
      button.disabled = false;
    }
  });
})();
