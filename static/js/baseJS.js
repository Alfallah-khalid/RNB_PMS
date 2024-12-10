document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector('.sidebar');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const fullscreenToggleBtn = document.getElementById('fullscreen-toggle');
    const restoreButton = document.getElementById('restore-button');
    const body = document.body;

    // Toggle Sidebar
    toggleSidebarBtn.addEventListener('click', () => {
        sidebar.classList.toggle('hidden');
    });

    // Fullscreen Mode
    fullscreenToggleBtn.addEventListener('click', () => {
        if (!document.fullscreenElement) {
            body.requestFullscreen().then(() => {
                body.classList.add('fullscreen-mode');
                restoreButton.classList.remove('hidden');
            });
        }
    });

    // Restore from Fullscreen
    restoreButton.addEventListener('click', () => {
        if (document.fullscreenElement) {
            document.exitFullscreen().then(() => {
                body.classList.remove('fullscreen-mode');
                restoreButton.classList.add('hidden');
            });
        }
    });
});
