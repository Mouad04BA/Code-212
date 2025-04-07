document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    const body = document.body;
    
    // Check for saved theme preference or default to light
    const currentTheme = localStorage.getItem('theme') || 'light';
    if (currentTheme === 'dark') {
        body.classList.add('dark-mode');
    }
    
    // Toggle dark mode on click
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            body.classList.toggle('dark-mode');
            
            // Save preference to localStorage
            const theme = body.classList.contains('dark-mode') ? 'dark' : 'light';
            localStorage.setItem('theme', theme);
            
            // Update charts if they exist
            if (typeof updateChartsTheme === 'function') {
                updateChartsTheme();
            }
        });
    }
});
