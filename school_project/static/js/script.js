// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Initialize popovers
document.addEventListener('DOMContentLoaded', function() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Confirm delete
document.addEventListener('DOMContentLoaded', function() {
    var deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
});

// Dynamic form fields
document.addEventListener('DOMContentLoaded', function() {
    var formFields = document.querySelectorAll('[data-dynamic-field]');
    formFields.forEach(function(field) {
        var dependentField = document.querySelector(field.dataset.dependentField);
        if (dependentField) {
            dependentField.addEventListener('change', function() {
                // Clear the dependent field
                field.innerHTML = '<option value="">---------</option>';
                
                // Get the new options based on the selected value
                if (this.value) {
                    fetch(`/api/get-options/?field=${field.dataset.dynamicField}&value=${this.value}`)
                        .then(response => response.json())
                        .then(data => {
                            data.forEach(function(item) {
                                var option = document.createElement('option');
                                option.value = item.id;
                                option.textContent = item.name;
                                field.appendChild(option);
                            });
                        });
                }
            });
        }
    });
});

// File input preview
document.addEventListener('DOMContentLoaded', function() {
    var fileInputs = document.querySelectorAll('[data-preview]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            var preview = document.querySelector(this.dataset.preview);
            if (preview) {
                if (this.files && this.files[0]) {
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                    }
                    reader.readAsDataURL(this.files[0]);
                }
            }
        });
    });
});
