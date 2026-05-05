  // Gestion de l'ajout de règles
document.addEventListener("DOMContentLoaded", () => {
            const addRuleModal = document.getElementById('add-nat-rule-modal');
            const addRuleForm = document.getElementById('add-nat-rule-form');

            
            document.getElementById('add-rule-btn').addEventListener('click', () => {
                addRuleModal.classList.remove('hidden');
            });

            document.getElementById('close-nat-modal').addEventListener('click', () => {
                addRuleModal.classList.add('hidden');
            });


            document.getElementById('cancel-add-nat-rule').addEventListener('click', () => {
                addRuleModal.classList.add('hidden');
            });


                    // AJOUTER UNE REGLE NAT


});


     // GESTION DE LA SUPPRESSION D’UNE RÈGLE

document.addEventListener("DOMContentLoaded", () => {
    const deleteModal = document.getElementById("delete-nat-modal");
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
                const modal = document.getElementById("edit-nat-modal");

                 // Afficher la modal
                modal.classList.remove("hidden");

                // Remplir les champs avec les data-attributes du bouton
                document.getElementById("edit-rule-id").value = btn.dataset.id;
                document.getElementById("edit-source").value = btn.dataset.ipsource;
                document.getElementById("edit-destination").value = btn.dataset.ipdestination;
                document.getElementById("edit-source-port").value = btn.dataset.portsource;
                document.getElementById("edit-destination-port").value = btn.dataset.portdestination;
                document.getElementById("edit-protocol").value = btn.dataset.protocol;
                document.getElementById("edit-interface-dentree").value = btn.dataset.interface_dentree;
                document.getElementById("edit-interface-sortie").value = btn.dataset.interface_sortie;
                document.getElementById("edit-to-ip").value = btn.dataset.newDestination;
                document.getElementById("edit-to-ip").value = btn.dataset.newSource;
                document.getElementById("edit-to-port").value = btn.dataset.newPort;
                document.getElementById("edit-nat-type").value = btn.dataset.type;
                document.getElementById("edit-comment").value = btn.dataset.desc;
              

                // Afficher une alerte (pour test)

                alert("Données chargées pour l'édition NAT de la règle ID: " + btn.dataset.id);

               
            });
        });

        // Fermer la modal
        document.getElementById("close-modal").addEventListener("click", () => {
            document.getElementById("edit-nat-modal").classList.add("hidden");
        });
        document.getElementById("cancel-edit").addEventListener("click", () => {
            document.getElementById("edit-nat-modal").classList.add("hidden");
        });

});


