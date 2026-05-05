

                                                              // Graphiques
        // Graphique du trafic le diagramme 
        const trafficCtx = document.getElementById('trafficChart').getContext('2d');
        const trafficChart = new Chart(trafficCtx, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '00:00'],
                datasets: [
                    {
                        label: 'Entrant',
                        data: [12, 19, 3, 5, 2, 3, 15],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Sortant',
                        data: [8, 15, 10, 12, 8, 10, 5],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                        legend:
                    {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Mbps'
                        }
                    }
                }
            }
        });

        // Graphique du type de trafic le diagramme circulaire sur les protocoles
        const trafficTypeCtx = document.getElementById('trafficTypeChart').getContext('2d');
        const trafficTypeChart = new Chart(trafficTypeCtx, {
            type: 'doughnut',
            data: {
                labels: ['HTTP', 'HTTPS', 'SSH', 'FTP', 'DNS', 'Autre'],
                datasets: [{
                    data: [35, 30, 10, 5, 15, 5],
                    backgroundColor: [
                        '#3b82f6',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#8b5cf6',
                        '#64748b'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                },
                cutout: '70%'
            }
        });

        // Graphique de l'état des paquets le diagramme circulaire sur les statuts des paquets 
        const packetStatusCtx = document.getElementById('packetStatusChart').getContext('2d');
        const packetStatusChart = new Chart(packetStatusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Accepté', 'Rejeté', 'Supprimé'],
                datasets: [{
                    data: [75, 15, 10],
                    backgroundColor: [
                        '#10b981',
                        '#ef4444',
                        '#64748b'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                },
                cutout: '70%'
            }
        });

        // Animation au défilement
        const animateOnScroll = function() {
            const elements = document.querySelectorAll('.animate-fadeIn');
            
            elements.forEach(element => {
                const elementPosition = element.getBoundingClientRect().top;
                const screenPosition = window.innerHeight / 1.3;
                
                if (elementPosition < screenPosition) {
                    element.style.opacity = '1';
                }
            });
        };

        window.addEventListener('scroll', animateOnScroll);
        window.addEventListener('load', animateOnScroll);


                    // . Code JS pour le formulaire de modification d'une suggestion 
        document.addEventListener("DOMContentLoaded", function() {


                            // Ouvre le formulaire de modification
                            document.querySelectorAll('.btn-modifier_sugg').forEach(btn => {
                                btn.addEventListener('click', function(e) {
                                    e.preventDefault();
                                    // Remplir les champs ici selon l'alerte (exemple statique)
                                   document.getElementById('form-rule-id').value = btn.dataset.id;
                                   document.getElementById('form-chaine').value = btn.dataset.chaine;
                                   document.getElementById('form-ip-source').value = btn.dataset.ipsource;
                                   document.getElementById('form-ip-destination').value = btn.dataset.ipdestination;
                                   document.getElementById('form-port').value = btn.dataset.port;
                                   document.getElementById('form-protocol').value = btn.dataset.protocol;
                                   document.getElementById('form-action').value = btn.dataset.action;
                                   document.getElementById('form-desc').value = btn.dataset.desc;
                                   document.getElementById('modal-overlay').classList.remove('hidden');
                                   document.body.classList.add('modal-open');
                                });
                            });

                            // Fonction pour fermer le modal
                            function closeModal() {
                                document.getElementById('modal-overlay').classList.add('hidden');
                                document.body.classList.remove('modal-open');
                            }

                            // Bouton croix
                            document.getElementById('close-modal').onclick = closeModal;

                            // Bouton Annuler
                            document.getElementById('cancel-modal').onclick = closeModal;

                            // Fermer en cliquant sur le fond noir
                            document.getElementById('modal-overlay').addEventListener('click', function(e) {
                                if (e.target === this) {
                                    closeModal();
                                }
                            });

        });

        document.addEventListener("DOMContentLoaded", function() {
            document.querySelectorAll('.btn-supprimer_sugg').forEach(btn => {
                btn.addEventListener('click', function(e) {
                   

                    // Récupérer l'ID de la suggestion
                    const suggId = btn.dataset.id;
                    const desc = btn.dataset.desc;

                    // Demande de confirmation
                    if (confirm(`Voulez-vous vraiment supprimer la suggestion : "${desc}" ?`)) {
                        // Soumettre le formulaire de suppression
                        document.getElementById(`delete-form`).submit();
                    }
                });
          });
        });