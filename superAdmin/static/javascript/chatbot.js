document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("chatbot-toggle");
  const window_ = document.getElementById("chatbot-window");
  const closeBtn = document.getElementById("chatbot-close");
  const form = document.getElementById("chatbot-form");
  const input = document.getElementById("chatbot-input");
  const messagesDiv = document.getElementById("chatbot-messages");
  const sendBtn = document.getElementById("chatbot-send");
  const icon = document.getElementById("chatbot-icon");

  let historique = [];
  let isLoading = false;

  // Ouvrir / fermer le chatbot
  toggle.addEventListener("click", function () {
    const isHidden = window_.classList.contains("hidden");
    window_.classList.toggle("hidden");
    icon.className = isHidden ? "fas fa-times text-xl" : "fas fa-robot text-xl";
    if (isHidden) {
      input.focus();
    }
  });

  closeBtn.addEventListener("click", function () {
    window_.classList.add("hidden");
    icon.className = "fas fa-robot text-xl";
  });

  // Suggestions rapides
  document.querySelectorAll(".suggestion-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const msg = btn.getAttribute("data-msg");
      input.value = msg;
      form.dispatchEvent(new Event("submit"));
    });
  });

  // Ajouter un message dans le chat
  function ajouterMessage(contenu, role) {
    const wrapper = document.createElement("div");
    wrapper.className = "flex items-start" + (role === "user" ? " justify-end" : "");

    if (role === "assistant") {
      wrapper.innerHTML =
        '<div class="w-7 h-7 bg-blue-100 rounded-full flex items-center justify-center mr-2 flex-shrink-0 mt-1">' +
        '<i class="fas fa-robot text-blue-600 text-xs"></i></div>' +
        '<div class="bg-white rounded-lg rounded-tl-none px-3 py-2 shadow-sm max-w-[80%]">' +
        '<div class="text-sm text-gray-700 whitespace-pre-wrap chatbot-response">' +
        formaterReponse(contenu) +
        "</div></div>";
    } else {
      wrapper.innerHTML =
        '<div class="bg-blue-600 text-white rounded-lg rounded-tr-none px-3 py-2 shadow-sm max-w-[80%]">' +
        '<p class="text-sm">' +
        escapeHtml(contenu) +
        "</p></div>";
    }

    messagesDiv.appendChild(wrapper);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  // Indicateur de chargement
  function ajouterLoading() {
    const wrapper = document.createElement("div");
    wrapper.className = "flex items-start";
    wrapper.id = "loading-indicator";
    wrapper.innerHTML =
      '<div class="w-7 h-7 bg-blue-100 rounded-full flex items-center justify-center mr-2 flex-shrink-0 mt-1">' +
      '<i class="fas fa-robot text-blue-600 text-xs"></i></div>' +
      '<div class="bg-white rounded-lg rounded-tl-none px-3 py-2 shadow-sm">' +
      '<div class="flex space-x-1"><div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>' +
      '<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay:0.1s"></div>' +
      '<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay:0.2s"></div></div></div>';
    messagesDiv.appendChild(wrapper);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  function supprimerLoading() {
    const el = document.getElementById("loading-indicator");
    if (el) el.remove();
  }

  // Formater la reponse (markdown basique)
  function formaterReponse(text) {
    let html = escapeHtml(text);

    // Blocs de code ```json ... ``` ou ``` ... ```
    html = html.replace(
      /```(\w*)\n([\s\S]*?)```/g,
      '<pre class="bg-gray-800 text-green-400 rounded-lg p-3 my-2 text-xs overflow-x-auto"><code>$2</code></pre>'
    );

    // Code inline
    html = html.replace(
      /`([^`]+)`/g,
      '<code class="bg-gray-100 text-red-600 px-1 rounded text-xs">$1</code>'
    );

    // Gras
    html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

    // Listes
    html = html.replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>');
    html = html.replace(
      /^\d+\. (.+)$/gm,
      '<li class="ml-4 list-decimal">$1</li>'
    );

    // Sauts de ligne
    html = html.replace(/\n/g, "<br>");

    return html;
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Envoi du message
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const message = input.value.trim();
    if (!message || isLoading) return;

    ajouterMessage(message, "user");
    input.value = "";
    isLoading = true;
    sendBtn.disabled = true;
    ajouterLoading();

    fetch("/api/chatbot/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: message, historique: historique }),
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        supprimerLoading();
        if (data.error) {
          ajouterMessage("Erreur : " + data.error, "assistant");
        } else {
          ajouterMessage(data.reponse, "assistant");
          historique.push({ role: "user", content: message });
          historique.push({ role: "assistant", content: data.reponse });
          // Garder les 10 derniers echanges max
          if (historique.length > 20) {
            historique = historique.slice(-20);
          }
        }
      })
      .catch(function (err) {
        supprimerLoading();
        ajouterMessage(
          "Erreur de connexion. Vérifiez que le serveur est en marche.",
          "assistant"
        );
      })
      .finally(function () {
        isLoading = false;
        sendBtn.disabled = false;
        input.focus();
      });
  });
});
