// Admin Panel Functions

function confirmDelete(binId, location) {
    return confirm('Are you sure you want to delete bin at "' + location + '"?');
}

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const fillLevel = form.querySelector('[name="fill_level"]');
            if (fillLevel && (fillLevel.value < 0 || fillLevel.value > 100)) {
                e.preventDefault();
                alert('Fill level must be between 0 and 100');
                return false;
            }
        });
    });
});