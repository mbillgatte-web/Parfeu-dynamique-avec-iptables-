   // Manipulation de la sidebar
        document.getElementById('toggle-sidebar').addEventListener('click', function() {
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content-area');
            
            sidebar.classList.toggle('sidebar-collapsed');
            // content.classList.toggle('ml-64');
            // content.classList.toggle('ml-20');
        });

        // Active menu item
        const menuItems = document.querySelectorAll('.menu-item');
        menuItems.forEach(item => {
            item.addEventListener('click', function() {
                // Si la barre latérale est réduite, l'agrandir
                const sidebar = document.getElementById('sidebar');
                if (sidebar.classList.contains('sidebar-collapsed')) {
                    sidebar.classList.remove('sidebar-collapsed');
                    // document.getElementById('content-area').classList.add('ml-64');
                    // document.getElementById('content-area').classList.remove('ml-20');
                }

                // Met à jour l'état actif
                menuItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
            });
        });



          //  <script>
            // Thème sombre/clair
            const themeBtn = document.getElementById('toggle-theme');
            const themeIcon = document.getElementById('theme-icon');
            const htmlTag = document.documentElement;

            // Fonction pour basculer le thème
            themeBtn.addEventListener('click', () => {
                if (htmlTag.classList.contains('dark')) {
                    htmlTag.classList.remove('dark');
                    themeIcon.classList.remove('fa-sun');
                    themeIcon.classList.add('fa-moon');
                } else {
                    htmlTag.classList.add('dark');
                    themeIcon.classList.remove('fa-moon');
                    themeIcon.classList.add('fa-sun');
                }
            });
   // </script>
