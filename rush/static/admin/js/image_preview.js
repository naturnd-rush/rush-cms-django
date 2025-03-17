document.addEventListener('DOMContentLoaded', function() {
    // Get the image input element
    const imageInput = document.querySelector('.image-input');

    if (imageInput) {
        // When an image is selected, show the preview
        imageInput.addEventListener('change', function(event) {
            const input = event.target;
            const reader = new FileReader();

            reader.onload = function(e) {
                let preview = document.getElementById('image-preview');
                if (!preview) {
                    preview = document.createElement('img');
                    preview.id = 'image-preview';
                    preview.width = 100;
                    preview.height = 100;
                    input.parentNode.insertBefore(preview, input.nextSibling);
                }
                preview.src = e.target.result;
            };

            reader.readAsDataURL(input.files[0]);
        });
    }

    // If there's already an image, show the preview
    const existingImage = document.getElementById('id_image').value;
    if (existingImage) {
        const preview = document.createElement('img');
        preview.id = 'image-preview';
        preview.width = 100;
        preview.height = 100;
        preview.src = existingImage;
        const imageInputElement = document.getElementById('id_image');
        imageInputElement.parentNode.insertBefore(preview, imageInputElement.nextSibling);
    }
});
