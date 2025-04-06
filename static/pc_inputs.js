document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('buildSheetForm');
    
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/generate-build-sheet', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                // Handle the response - perhaps redirect to a print view
                window.location.href = '/build-sheet/print?id=' + result.id;
            } else {
                console.error('Failed to generate build sheet');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});