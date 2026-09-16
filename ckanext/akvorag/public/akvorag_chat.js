/**
 * Akvo RAG Interactive Chat Widget Component for CKAN
 */
(function() {
  function initAkvoRAGWidget() {
    const launcher = document.getElementById('akvorag-launcher');
    const panel = document.getElementById('akvorag-chat-panel');
    const closeBtn = document.getElementById('akvorag-close-btn');
    const form = document.getElementById('akvorag-chat-form');
    const input = document.getElementById('akvorag-chat-input');
    const msgContainer = document.getElementById('akvorag-messages');
    const sendBtn = document.getElementById('akvorag-send-btn');

    if (!launcher || !panel) return;

    // Toggle chat panel
    launcher.addEventListener('click', function() {
      const isHidden = panel.classList.contains('akvorag-hidden');
      if (isHidden) {
        panel.classList.remove('akvorag-hidden');
        if (input) input.focus();
      } else {
        panel.classList.add('akvorag-hidden');
      }
    });

    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
        panel.classList.add('akvorag-hidden');
      });
    }

    if (!form || !input) return;

    const endpoint = panel.getAttribute('data-endpoint') || 'https://akvo.ngrok.dev';
    const kbId = panel.getAttribute('data-kb-id');
    const isConfigured = panel.getAttribute('data-configured') === 'true';

    function appendMessage(text, role, citations) {
      const msgDiv = document.createElement('div');
      msgDiv.className = 'akvorag-msg ' + (role === 'user' ? 'akvorag-msg-user' : 'akvorag-msg-assistant');
      msgDiv.textContent = text;

      if (citations && citations.length > 0) {
        const citeDiv = document.createElement('div');
        citeDiv.className = 'akvorag-citations';
        const title = document.createElement('div');
        title.className = 'akvorag-citations-title';
        title.textContent = 'Sources:';
        citeDiv.appendChild(title);

        citations.forEach(c => {
          const item = document.createElement('div');
          const docName = c.document_name || c.filename || c.title || 'Source Document';
          const page = c.page ? ` (p. ${c.page})` : '';
          item.textContent = `• ${docName}${page}`;
          citeDiv.appendChild(item);
        });
        msgDiv.appendChild(citeDiv);
      }

      msgContainer.appendChild(msgDiv);
      msgContainer.scrollTop = msgContainer.scrollHeight;
      return msgDiv;
    }

    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      const queryText = input.value.trim();
      if (!queryText) return;

      appendMessage(queryText, 'user');
      input.value = '';
      input.disabled = true;
      sendBtn.disabled = true;

      const loadingMsg = appendMessage('Thinking...', 'assistant');

      try {
        const payload = {
          job_type: 'CHAT',
          prompt: queryText,
          knowledge_base_ids: kbId ? [parseInt(kbId, 10)] : []
        };

        const res = await fetch(`${endpoint}/api/v1/apps/jobs`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          throw new Error(`Server returned HTTP ${res.status}`);
        }

        const data = await res.json();
        const answer = data.answer || data.response || data.content || (data.result && data.result.answer) || 'No response generated.';
        const citations = data.citations || data.sources || (data.result && data.result.citations) || [];

        loadingMsg.textContent = answer;
        if (citations.length > 0) {
          const citeDiv = document.createElement('div');
          citeDiv.className = 'akvorag-citations';
          const title = document.createElement('div');
          title.className = 'akvorag-citations-title';
          title.textContent = 'Sources:';
          citeDiv.appendChild(title);

          citations.forEach(c => {
            const item = document.createElement('div');
            const docName = c.document_name || c.filename || c.title || 'Source Document';
            const page = c.page ? ` (p. ${c.page})` : '';
            item.textContent = `• ${docName}${page}`;
            citeDiv.appendChild(item);
          });
          loadingMsg.appendChild(citeDiv);
        }
      } catch (err) {
        loadingMsg.textContent = `Error querying AI Assistant: ${err.message}. Please verify Akvo RAG endpoint connectivity.`;
      } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
        msgContainer.scrollTop = msgContainer.scrollHeight;
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAkvoRAGWidget);
  } else {
    initAkvoRAGWidget();
  }
})();
