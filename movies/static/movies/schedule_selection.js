// In movies/static/movies/schedule_selection.js

document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('form[method="get"]');
    const scheduleForm = document.querySelector('form[action="/generate-schedule/"]');
    let selectedMovies = new Set();

    // Load saved selections from session storage
    const savedSelection = sessionStorage.getItem('selectedMovies');
    if (savedSelection) {
        selectedMovies = new Set(JSON.parse(savedSelection));
    }

    // Function to update the hidden input field with all selected IDs
    function updateHiddenInput() {
        const hiddenInput = document.getElementById('selected-movies-input');
        if (hiddenInput) {
            hiddenInput.value = JSON.stringify(Array.from(selectedMovies));
        }
    }

    // Add checkboxes for currently rendered movies to the selectedMovies set if they were previously selected
    const checkboxes = document.querySelectorAll('input[name="movies"]');
    checkboxes.forEach(checkbox => {
        if (selectedMovies.has(checkbox.value)) {
            checkbox.checked = true;
        }
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                selectedMovies.add(this.value);
            } else {
                selectedMovies.delete(this.value);
            }
            updateHiddenInput();
            sessionStorage.setItem('selectedMovies', JSON.stringify(Array.from(selectedMovies)));
        });
    });

    // Add hidden input to the schedule form to submit all selected IDs
    const hiddenScheduleInput = document.createElement('input');
    hiddenScheduleInput.type = 'hidden';
    hiddenScheduleInput.name = 'movies';
    hiddenScheduleInput.id = 'selected-movies-input';
    scheduleForm.appendChild(hiddenScheduleInput);
    updateHiddenInput(); // Initial update

    // Add a click listener to the schedule button to ensure all checkboxes are added to the form before submission
    const scheduleButton = document.querySelector('form[action="/generate-schedule/"] button[type="submit"]');
    if (scheduleButton) {
        scheduleButton.addEventListener('click', function(event) {
            // Prevent the default form submission to manually handle it
            event.preventDefault();

            // Clear all existing checkboxes and add a single hidden input with all selected IDs
            const existingCheckboxes = scheduleForm.querySelectorAll('input[name="movies"]');
            existingCheckboxes.forEach(cb => {
                if(cb.type === 'checkbox') {
                    cb.remove();
                }
            });

            const finalInput = document.createElement('input');
            finalInput.type = 'hidden';
            finalInput.name = 'movies';
            finalInput.value = JSON.stringify(Array.from(selectedMovies));
            scheduleForm.appendChild(finalInput);
            
            // Now submit the form
            scheduleForm.submit();
        });
    }
});