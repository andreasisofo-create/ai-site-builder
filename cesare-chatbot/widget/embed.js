/**
 * embed.js — Script di embedding del widget Rally di Roma Capitale
 *
 * Utilizzo su WordPress:
 * <script src="https://srv1352958.hstgr.cloud/widget/embed.js"
 *         data-url="https://srv1352958.hstgr.cloud"></script>
 *
 * Funzionamento:
 * 1. Legge data-url dal tag <script> corrente
 * 2. Imposta window.RALLY_CHAT_URL (usato dal widget per sapere dove chiamare l'API)
 * 3. Fetch dell'HTML del widget
 * 4. Inietta il contenuto nel body della pagina host
 * 5. Esegue gli script inline contenuti nel widget
 */

(function () {
  'use strict';

  // Esegui una sola volta
  if (window.__rallyWidgetLoaded) return;
  window.__rallyWidgetLoaded = true;

  // Trova il tag <script> che ha caricato questo file
  const scripts = document.querySelectorAll('script[src*="embed.js"]');
  const thisScript = scripts[scripts.length - 1];

  // Legge il data-url dal tag script
  const baseUrl = thisScript
    ? (thisScript.getAttribute('data-url') || '').replace(/\/$/, '')
    : '';

  // Imposta l'URL base per il widget (letto da chat-widget.html)
  window.RALLY_CHAT_URL = baseUrl || 'http://localhost:3000';

  const widgetUrl = window.RALLY_CHAT_URL + '/widget/chat-widget.html';

  // Fetch e inject del widget
  fetch(widgetUrl)
    .then(function (resp) {
      if (!resp.ok) throw new Error('Fetch widget fallito: ' + resp.status);
      return resp.text();
    })
    .then(function (html) {
      // Parser DOM
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      // Inietta gli stili <style> dal <head> del widget
      doc.querySelectorAll('style').forEach(function (style) {
        const clone = document.createElement('style');
        clone.textContent = style.textContent;
        document.head.appendChild(clone);
      });

      // Inietta elementi dal <body> del widget (FAB + widget div)
      // Esclude la demo-page (.demo-page) per non sporcare la pagina host
      doc.body.querySelectorAll(':scope > *').forEach(function (el) {
        if (el.classList && el.classList.contains('demo-page')) return;

        // Non iniettare script direttamente — gestiti sotto
        if (el.tagName === 'SCRIPT') return;

        const clone = document.importNode(el, true);
        document.body.appendChild(clone);
      });

      // Esegui gli script inline del widget nell'ordine corretto
      doc.body.querySelectorAll('script').forEach(function (script) {
        if (script.src) return; // script esterni ignorati
        try {
          // eslint-disable-next-line no-new-func
          (new Function(script.textContent))();
        } catch (e) {
          console.error('[Rally Embed] Errore esecuzione script widget:', e);
        }
      });

      console.log('[Rally Embed] Widget caricato da', widgetUrl);
    })
    .catch(function (err) {
      console.error('[Rally Embed] Impossibile caricare il widget:', err.message);
    });
})();
