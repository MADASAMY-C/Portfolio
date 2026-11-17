document.addEventListener('DOMContentLoaded', () => {
    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    // Modal logic
    const closeBtns = document.querySelectorAll('.close-modal');
    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal').classList.remove('active');
        });
    });

    // Close on overlay click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });

    // --- Projects ---
    const projectModal = document.getElementById('projectModal');
    if (projectModal) {
        document.getElementById('addProjectBtn').addEventListener('click', () => {
            document.getElementById('modalTitle').innerText = 'Add Project';
            document.getElementById('projectForm').action = '/admin/projects/add';
            document.getElementById('projectForm').reset();
            projectModal.classList.add('active');
        });

        document.querySelectorAll('.edit-project-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const b = e.currentTarget;
                document.getElementById('modalTitle').innerText = 'Edit Project';
                document.getElementById('projectForm').action = '/admin/projects/edit/' + b.getAttribute('data-id');
                
                document.getElementById('formTitle').value = b.getAttribute('data-title');
                document.getElementById('formCategory').value = b.getAttribute('data-category');
                document.getElementById('formDescription').value = b.getAttribute('data-description');
                document.getElementById('formTech').value = b.getAttribute('data-tech');
                document.getElementById('formGithub').value = b.getAttribute('data-github');
                document.getElementById('formLive').value = b.getAttribute('data-live');
                document.getElementById('formFeatured').checked = b.getAttribute('data-featured') === '1' || b.getAttribute('data-featured') === 'True';
                
                projectModal.classList.add('active');
            });
        });
    }

    // --- Skills ---
    const skillModal = document.getElementById('skillModal');
    if (skillModal) {
        document.getElementById('addSkillBtn').addEventListener('click', () => {
            document.getElementById('modalTitle').innerText = 'Add Skill';
            document.getElementById('skillForm').action = '/admin/skills/add';
            document.getElementById('skillForm').reset();
            skillModal.classList.add('active');
        });

        document.querySelectorAll('.edit-skill-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const b = e.currentTarget;
                document.getElementById('modalTitle').innerText = 'Edit Skill';
                document.getElementById('skillForm').action = '/admin/skills/edit/' + b.getAttribute('data-id');
                
                document.getElementById('formName').value = b.getAttribute('data-name');
                document.getElementById('formCategory').value = b.getAttribute('data-category');
                document.getElementById('formPercentage').value = b.getAttribute('data-percentage');
                document.getElementById('formIcon').value = b.getAttribute('data-icon');
                
                skillModal.classList.add('active');
            });
        });
    }

    // --- Achievements ---
    const achievementModal = document.getElementById('achievementModal');
    if (achievementModal) {
        document.getElementById('addAchievementBtn').addEventListener('click', () => {
            document.getElementById('modalTitle').innerText = 'Add Achievement';
            document.getElementById('achievementForm').action = '/admin/achievements/add';
            document.getElementById('achievementForm').reset();
            achievementModal.classList.add('active');
        });

        document.querySelectorAll('.edit-achievement-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const b = e.currentTarget;
                document.getElementById('modalTitle').innerText = 'Edit Achievement';
                document.getElementById('achievementForm').action = '/admin/achievements/edit/' + b.getAttribute('data-id');
                
                document.getElementById('formTitle').value = b.getAttribute('data-title');
                document.getElementById('formIssuer').value = b.getAttribute('data-issuer');
                document.getElementById('formDescription').value = b.getAttribute('data-description');
                document.getElementById('formDate').value = b.getAttribute('data-date') || '';
                document.getElementById('formUrl').value = b.getAttribute('data-url');
                
                achievementModal.classList.add('active');
            });
        });
    }
});
