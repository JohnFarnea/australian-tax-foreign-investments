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
                        
                        // Add event handler for detail links after page is loaded
                        $(document).ready(function() {
                            setupDetailLinks();
                        });
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
    
    // Function to set up detail link click handlers
    function setupDetailLinks() {
        $('.detail-link').on('click', function(e) {
            e.preventDefault();
            
            // Get the URL from the link
            var url = $(this).attr('href');
            
            // Extract the element type from the URL
            var element = url.split('/').pop();
            
            // Determine element name and data based on the element type
            var elementName, elementData;
            
            switch(element) {
                case 'sales_details':
                    elementName = 'Sales Details';
                    elementData = window.results.sales_details;
                    break;
                case 'opening_balance':
                    elementName = 'Opening Balance';
                    elementData = window.results.opening_balance;
                    break;
                case 'purchases_details':
                    elementName = 'Purchases Details';
                    elementData = window.results.purchases_details;
                    break;
                case 'closing_balance':
                    elementName = 'Closing Balance';
                    elementData = window.results.closing_balance;
                    break;
                default:
                    alert('Unknown detail type');
                    return;
            }
            
            // Send AJAX request to get details page with the data
            $.ajax({
                url: url,
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    element_name: elementName,
                    element_data: elementData,
                    full_results: window.results // Pass the full results for "Back to Results" functionality
                }),
                success: function(response) {
                    if (response.success && response.html) {
                        // Replace page content with details HTML
                        document.open();
                        document.write(response.html);
                        document.close();
                        // Update browser history
                        history.pushState({}, elementName, url);
                    } else {
                        alert('Error: ' + (response.error || 'Failed to load details'));
                    }
                },
                error: function(xhr) {
                    var errorMsg = 'An error occurred while loading details.';
                    if (xhr.responseJSON && xhr.responseJSON.error) {
                        errorMsg = xhr.responseJSON.error;
                    }
                    alert('Error: ' + errorMsg);
                }
            });
        });
    }
});
