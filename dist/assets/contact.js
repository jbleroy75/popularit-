// Formulaires « Nous contacter » et « Laisser un avis » : envoi au relais leads (Worker leads-relay, kind "contact").
(() => {
  const startedAt = Date.now();
  const FIELDS = ['name', 'organisation', 'email', 'phone', 'topic', 'message', 'preferred', 'company'];

  for (const form of document.querySelectorAll('form[data-kind]')) {
    const status = form.querySelector('.form-status');
    const button = form.querySelector('button[type=submit]');
    const review = form.dataset.kind === 'review';
    const say = (msg, ok) => { status.textContent = msg; status.dataset.state = ok ? 'ok' : 'error'; };

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const missing = [...form.querySelectorAll('[required]')].find((el) => (el.type === 'checkbox' ? !el.checked : !el.value.trim()));
      if (missing) return say(missing.type === 'checkbox' ? 'Merci de cocher la case d’accord.' : 'Merci de compléter les champs obligatoires.'), missing.focus();
      if (!form.email.checkValidity()) return say('Indiquez une adresse e-mail valide.'), form.email.focus();
      button.disabled = true;
      say('Envoi…', true);
      const data = Object.fromEntries(FIELDS.filter((k) => form[k]).map((k) => [k, form[k].value]));
      if (review) data.message = `Note : ${form.note.value}/5\nSignature souhaitée : ${form.signature.value}\n\n${data.message}`;
      try {
        const r = await fetch('https://leads.jbleroy.fr/api/lead', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...data, kind: 'contact', consent: true, formStartedAt: startedAt, pageUrl: location.href }),
        });
        const res = await r.json().catch(() => ({}));
        if (r.ok && res.ok) {
          form.reset();
          say(review ? 'Merci pour votre avis. Nous vous écrivons avant de le publier.' : 'Merci, votre message est bien arrivé. Nous vous répondons sous 24 heures ouvrées.', true);
        } else if (r.status === 429) {
          say('Trop d’envois depuis cette connexion. Réessayez dans une heure.');
        } else {
          say('L’envoi n’a pas abouti. Vérifiez les champs et réessayez.');
        }
      } catch {
        say('Connexion impossible pour le moment. Réessayez dans quelques instants.');
      } finally {
        button.disabled = false;
      }
    });
  }
})();
