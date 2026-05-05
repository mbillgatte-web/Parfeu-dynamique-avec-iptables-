// </script>
console.log("Nouveau JS chargé !");


document.addEventListener("DOMContentLoaded", () => {
    const usersTableBody = document.getElementById("users-table-body");
    const addUserBtn = document.getElementById("add-user-btn");
    const userModal = document.getElementById("user-modal");
    const deleteModal = document.getElementById("delete-modal");
    const closeModalBtn = document.getElementById("close-modal");
    const cancelBtn = document.getElementById("cancel-btn");
    const saveBtn = document.getElementById("save-btn");
    const confirmDeleteBtn = document.getElementById("confirm-delete-btn");
    const cancelDeleteBtn = document.getElementById("cancel-delete-btn");

    const usernameInput = document.getElementById("username");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const userIdInput = document.getElementById("user-id");
    const modalTitle = document.getElementById("modal-title");

    let users = [];
    let userToDelete = null;
    let isEditing = false;

    // Fonction pour afficher la liste des utilisateurs
    function renderUsers() {
        usersTableBody.innerHTML = "";
        users.forEach((user, index) => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">${index + 1}</td>
                <td class="px-6 py-4 whitespace-nowrap">${user.username}</td>
                <td class="px-6 py-4 whitespace-nowrap">${user.email}</td>
                <td class="px-6 py-4 whitespace-nowrap">${user.lastLogin || "Jamais"}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <button class="text-indigo-600 hover:text-indigo-900 mr-3 edit-btn" data-index="${index}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="text-red-600 hover:text-red-900 delete-btn" data-index="${index}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;

            usersTableBody.appendChild(row);
        });

        // Mettre à jour les compteurs
        // document.getElementById("total-items").textContent = users.length;
        document.getElementById("total-SuperAdmin").textContent = users.filter(u => u.role === "Super Admin").length;
        document.getElementById("total-Admin").textContent = users.filter(u => u.role === "Admin").length;
        document.getElementById("total-User").textContent = users.filter(u => u.role === "User").length;

        attachRowEvents();
    }

    // Attacher les événements des boutons modifier/supprimer
    function attachRowEvents() {
        document.querySelectorAll(".edit-btn").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const index = e.currentTarget.dataset.index;
                const user = users[index];

                usernameInput.value = user.username;
                emailInput.value = user.email;
                passwordInput.value = "";
                userIdInput.value = index;
                modalTitle.textContent = "Modifier un utilisateur";
                isEditing = true;
                openModal();
            });
        });

        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const index = e.currentTarget.dataset.index;
                userToDelete = index;
                deleteModal.classList.remove("hidden");
            });
        });
    }

    function openModal() {
        userModal.classList.remove("hidden");
    }

    function closeModal() {
        userModal.classList.add("hidden");
        isEditing = false;
        userIdInput.value = "";
        usernameInput.value = "";
        emailInput.value = "";
        passwordInput.value = "";
    }

    function closeDeleteModal() {
        deleteModal.classList.add("hidden");
        userToDelete = null;
    }

    // Ajouter un utilisateur
    addUserBtn.addEventListener("click", () => {
        isEditing = false;
        modalTitle.textContent = "Ajouter un utilisateur";
        openModal();
    });

    // Annuler
    closeModalBtn.addEventListener("click", closeModal);
    cancelBtn.addEventListener("click", closeModal);
    cancelDeleteBtn.addEventListener("click", closeDeleteModal);

    // Enregistrer
    saveBtn.addEventListener("click", () => {
        const username = usernameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        if (!username || !email) {
            alert("Nom et Email sont obligatoires");
            return;
        }

        const user = {
            username,
            email,
            lastLogin: new Date().toLocaleString(),
            role: "User" // Tu peux changer la logique si besoin
        };

        if (isEditing) {
            users[userIdInput.value] = { ...users[userIdInput.value], ...user };
        } else {
            users.push(user);
        }

        renderUsers();
        closeModal();
    });

    // Confirmer suppression
    confirmDeleteBtn.addEventListener("click", () => {
        if (userToDelete !== null) {
            users.splice(userToDelete, 1);
            renderUsers();
            closeDeleteModal();
        }
    });

    // Simule des données par défaut
    users = [
        { username: "admin", email: "admin@mail.com", lastLogin: "2025-08-15 12:00", role: "Super Admin" },
        { username: "lucas", email: "lucas@mail.com", lastLogin: "2025-08-20 10:30", role: "Admin" },
        { username: "nina", email: "nina@mail.com", lastLogin: null, role: "User" }
    ];

    renderUsers();
});


        // Check password strength
        function checkPasswordStrength(password) {
            let strength = 0;
            
            // Length check
            if (password.length >= 8) strength++;
            if (password.length >= 12) strength++;
            
            // Complexity checks
            if (/[A-Z]/.test(password)) strength++;
            if (/[0-9]/.test(password)) strength++;
            if (/[^A-Za-z0-9]/.test(password)) strength++;
            
            // Cap at 4
            return Math.min(strength, 4);
        }

        // Update password strength indicator
        function updatePasswordStrength() {
            const password = passwordInput.value;
            const strength = checkPasswordStrength(password);
            const strengthText = ['Très faible', 'Faible', 'Moyen', 'Fort', 'Très fort'][strength];
            const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-400', 'bg-green-600'];
            
            // Reset all bars
            for (let i = 1; i <= 4; i++) {
                const bar = document.getElementById(`strength-${i}`);
                bar.className = `password-strength w-1/4 bg-gray-200 rounded-sm`;
            }
            
            // Set active bars
            for (let i = 1; i <= strength; i++) {
                const bar = document.getElementById(`strength-${i}`);
                bar.className = `password-strength w-1/4 ${strengthColors[strength]} rounded-sm`;
            }
            
            // Update text
            const strengthTextElement = document.getElementById('password-strength-text');
            strengthTextElement.textContent = password ? `Force du mot de passe: ${strengthText}` : '';
            strengthTextElement.className = `text-xs mt-1 ${password ? 'text-gray-700' : 'text-gray-500'}`;
        }

        // Toggle password visibility
        function togglePasswordVisibility() {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                togglePasswordBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                passwordInput.type = 'password';
                togglePasswordBtn.innerHTML = '<i class="fas fa-eye"></i>';
            }
        }

        // // Setup event listeners
        // function setupEventListeners() {
        //     // Modal controls
        //     addUserBtn.addEventListener('click', openAddModal);
        //     closeModalBtn.addEventListener('click', () => userModal.classList.add('hidden'));
        //     closeDeleteModalBtn.addEventListener('click', () => deleteModal.classList.add('hidden'));
        //     cancelBtn.addEventListener('click', () => userModal.classList.add('hidden'));
        //     cancelDeleteBtn.addEventListener('click', () => deleteModal.classList.add('hidden'));
        //     saveBtn.addEventListener('click', saveUser);
        //     confirmDeleteBtn.addEventListener('click', deleteUser);
            
        //     // Password strength
        //     passwordInput.addEventListener('input', updatePasswordStrength);
            
        //     // Toggle password visibility
        //     togglePasswordBtn.addEventListener('click', togglePasswordVisibility);
            
        //     // Close modals when clicking outside
        //     window.addEventListener('click', (e) => {
        //         if (e.target === userModal) {
        //             userModal.classList.add('hidden');
        //         }
        //         if (e.target === deleteModal) {
        //             deleteModal.classList.add('hidden');
        //         }
        //     });
            
        //     // Mobile menu toggle
        //     menuToggle.addEventListener('click', () => {
        //         sidebar.classList.toggle('sidebar-open');
        //     });
        // }

        // Initialize the app
      
 {/* </script> */}