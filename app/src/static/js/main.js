$(document).ready(function() {
    // Handle form submission
    $('#uploadForm').on('submit', function(e) {
        e.preventDefault();
        
        // Show loading spinner
        $('#loadingSpinner').removeClass('d-none');
        $('#calculateBtn').prop('disabled', true);
        
        // Create FormData object
        var formData = new FormData(this);
        
        // Send AJAX request
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                if (response.success) {
                    if (response.html) {
                        // Replace page content with results HTML
                        document.open();
                        document.write(response.html);
                        document.close();
                        // Update browser history so back button works correctly
                        history.pushState({}, "Results", "/results");
                    } else if (response.redirect) {
                        // Fallback to redirect if html not provided
                        window.location.href = response.redirect;
                    }
                } else {
                    // Show error message
                    alert('Error: ' + response.error);
                    $('#loadingSpinner').addClass('d-none');
                    $('#calculateBtn').prop('disabled', false);
                }
            },
            error: function(xhr) {
                var errorMsg = 'An error occurred during processing.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                alert('Error: ' + errorMsg);
                $('#loadingSpinner').addClass('d-none');
                $('#calculateBtn').prop('disabled', false);
            }
        });
    });
});
