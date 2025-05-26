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
                    // Redirect to results page
                    window.location.href = response.redirect;
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
