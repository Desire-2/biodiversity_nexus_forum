
document.addEventListener('DOMContentLoaded', function() {
    const profileImage = document.getElementById('profile-image');
    const logoutLink = document.getElementById('logout-link');
    if (profileImage) {
        profileImage.addEventListener('click', function(event) {
            event.preventDefault();
            if (logoutLink.style.display === 'none') {
                logoutLink.style.display = 'block';
            } else {
                logoutLink.style.display = 'none';
            }
        });
    }
});