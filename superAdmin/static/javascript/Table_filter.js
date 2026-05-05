document.addEventListener("DOMContentLoaded", () => {
    const addRuleModal = document.getElementById('add-rule-modal');
    const addRuleForm = document.getElementById('add-rule-form');
    const priorityInput = document.getElementById('rule-priority');

    document.getElementById('add-rule-btn').addEventListener('click', () => {
        addRuleModal.classList.remove('hidden');
    });
    document.getElementById('close-modal').addEventListener('click', () => addRuleModal.classList.add('hidden'));
    document.getElementById('cancel-modal').addEventListener('click', () => addRuleModal.classList.add('hidden'));

    const notifier = (msg) => {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg animate-fadeIn';
        notification.innerHTML = `<i class="fas fa-check-circle mr-2"></i> ${msg}`;
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.classList.add('opacity-0', 'transition-opacity', 'duration-300');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    };

    document.getElementById('confirm-add-rule').addEventListener('click', (e) => {
        e.preventDefault();
        priorityInput.value = "0";  // Ajout normal
        addRuleForm.submit();
        notifier("Nouvelle règle ajoutée");
        addRuleModal.classList.add('hidden');
        addRuleForm.reset();
    });

    document.getElementById('add-priority-rule').addEventListener('click', (e) => {
        e.preventDefault();
        priorityInput.value = "1";  // Ajout en priorité
        addRuleForm.submit();
        notifier("Nouvelle règle ajoutée en priorité");
        addRuleModal.classList.add('hidden');
        addRuleForm.reset();
    });
});


     // GESTION DE LA SUPPRESSION D’UNE RÈGLE

document.addEventListener("DOMContentLoaded", () => {
    const deleteModal = document.getElementById("delete-modal");
    const deleteForm = document.getElementById("delete-form");
    const cancelBtn = document.getElementById("cancel-delete");

    // Quand on clique sur une poubelle
    document.querySelectorAll(".delete_btn").forEach(btn => {
        btn.addEventListener("click", () => {
            // Mettre à jour l'action du formulaire avec le data-url du bouton
            const url = btn.getAttribute("data-url");
            deleteForm.setAttribute("action", url);

            // Afficher la modal
            deleteModal.classList.remove("hidden");
        });
    });

    // Bouton Annuler
    cancelBtn.addEventListener("click", () => {
        deleteModal.classList.add("hidden");
    });

    // Fermer si on clique en dehors de la modal
    deleteModal.addEventListener("click", (e) => {
        if (e.target === deleteModal) {
            deleteModal.classList.add("hidden");
        }
    });

    // Soumission du formulaire classique : pas besoin de JS ici
    // Django s’occupera de la suppression avec le POST vers l’URL du formulaire
});

  




// // GESTION DE LA MODIFICATION D’UNE RÈGLE 
document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll(".edit-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const modal = document.getElementById("edit-modal");

                 // Afficher la modal
                modal.classList.remove("hidden");

                // Remplir les champs avec les data-attributes du bouton
                document.getElementById("edit-rule-id").value = btn.dataset.id;
                document.getElementById("edit-ip-source").value = btn.dataset.ipsource;
                document.getElementById("edit-ip-destination").value = btn.dataset.ipdestination;
                document.getElementById("edit-port-source").value = btn.dataset.portsource;
                document.getElementById("edit-port-destination").value = btn.dataset.portdestination;
                document.getElementById("edit-form-protocol").value = btn.dataset.protocol;
                document.getElementById("edit-form-action").value = btn.dataset.action;
                document.getElementById("edit-form-desc").value = btn.dataset.desc;
                document.getElementById("edit-chain").value = btn.dataset.chain;

                // Afficher une alerte (pour test)

                alert("Données chargées pour l'édition de la règle ID: " + btn.dataset.id);

               
            });
        });

        // Fermer la modal
        document.getElementById("close-edit-modal").addEventListener("click", () => {
            document.getElementById("edit-modal").classList.add("hidden");
        });
        document.getElementById("cancel-edit").addEventListener("click", () => {
            document.getElementById("edit-modal").classList.add("hidden");
        });

});


