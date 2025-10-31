from dataclasses import dataclass
from typing import Any, List

from django.db.models import Model
from django.forms import Select
from django.template import Context, Engine
from django.utils.safestring import mark_safe

from rush.context_processors import base_url_from_request


class TiledForeignKeyWidget(Select):
    """
    A foreign-key selection widget for the admin site that displays foreign-key
    instances in a tile-like manner which can be selected by a user clicking on them.
    """

    @dataclass
    class Choice:
        """
        A possible choice of which foreign-key to select.
        """

        id: str

        # Relative url (e.g., from file-field)
        thumbnail_url: str

        # the form model instance (of type A) that has a foreign-key to a model (of type B),
        # whose instances we wish to display as selectable tiles.
        instance: Model

        # The name of the foreign key field (to a model of type B), on the form model instance model (of type A).
        fk_name: str

        request: Any

        def selected_str(self) -> str:
            """
            True when the fk object is attached to the form instance.
            """
            related = getattr(self.instance, self.fk_name, None)
            if related is None:
                # LOG TODO: Should log warning here.
                return ""
            selected = str(related.id) == self.id
            return "selected" if selected else ""

        def base_media_url(self) -> str:
            return base_url_from_request(self.request)

    def __init__(self, display_choices: List[Choice], attrs=None):
        self.display_choices = display_choices
        super().__init__(
            attrs,
            [
                # Just use id as the label for choices here, since the
                # display_html is shown in lieu of a label.
                (x.id, x.id)
                for x in display_choices
            ],
        )

    def render(self, name, value, attrs=None, renderer=None):
        """
        Renders the widget as a grid of tiles with images.
        """

        # Prepare context
        context = {
            "name": name,
            "value": value,
            "display_choices": self.display_choices,
        }
        template_str = """
        <div class="tiled-foreignkey-widget">

            {% for choice in display_choices %}
                <div class="tile {{ choice.selected_str }}" data-value="{{ choice.id }}">
                    <img src="{{ choice.base_media_url }}{{ choice.thumbnail_url }}" alt="">
                </div>
            {% endfor %}

            <!-- Upload new tile -->
            <div class="tile upload-tile" data-action="upload">
                <span class="plus-icon">+</span>
            </div>

            <!-- Hidden select -->
            <select name="{{ name }}" class="tiled-fk-select" style="display:none;">
                {% for choice in display_choices %}
                    <option value="{{ choice.id }}" {{ choice.selected_str }}></option>
                {% endfor %}
            </select>

        </div>

        <!-- Upload Modal -->
        <div class="upload-modal" style="display:none;">
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <h3>Upload New Icon</h3>
                <input type="file" class="icon-file-input" accept=".svg,.png,.webp,.jpg,.jpeg">
                <div class="preview-container" style="display:none;">
                    <img class="preview-image" src="" alt="Preview">
                </div>
                <div class="modal-actions">
                    <button type="button" class="upload-btn">Upload</button>
                    <button type="button" class="cancel-btn">Cancel</button>
                </div>
                <div class="upload-status"></div>
            </div>
        </div>

        <script type="module">
            document.querySelectorAll('.tiled-foreignkey-widget:not([data-initialized])').forEach(widget => {
                widget.setAttribute('data-initialized', 'true');
                const modal = widget.parentElement.querySelector('.upload-modal');
                const fileInput = modal.querySelector('.icon-file-input');
                const previewContainer = modal.querySelector('.preview-container');
                const previewImage = modal.querySelector('.preview-image');
                const uploadBtn = modal.querySelector('.upload-btn');
                const cancelBtn = modal.querySelector('.cancel-btn');
                const uploadStatus = modal.querySelector('.upload-status');

                // Handle tile selection
                widget.querySelectorAll('.tile:not(.upload-tile)').forEach(tile => {
                    tile.addEventListener('click', () => {
                        widget.querySelectorAll('.tile').forEach(t => t.classList.remove('selected'));
                        tile.classList.add('selected');
                        widget.querySelector('.tiled-fk-select').value = tile.dataset.value;
                    });
                });

                // Handle upload tile click
                widget.querySelector('.upload-tile').addEventListener('click', () => {
                    modal.style.display = 'block';
                });

                // Handle file selection for preview
                fileInput.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            previewImage.src = e.target.result;
                            previewContainer.style.display = 'block';
                        };
                        reader.readAsDataURL(file);
                    }
                });

                // Handle cancel button
                cancelBtn.addEventListener('click', () => {
                    modal.style.display = 'none';
                    fileInput.value = '';
                    previewContainer.style.display = 'none';
                    uploadStatus.textContent = '';
                });

                // Handle upload button
                uploadBtn.addEventListener('click', async () => {
                    const file = fileInput.files[0];
                    if (!file) {
                        uploadStatus.textContent = 'Please select a file';
                        return;
                    }

                    // Prevent multiple clicks
                    if (uploadBtn.disabled) {
                        return;
                    }

                    const formData = new FormData();
                    formData.append('file', file);

                    // Get CSRF token
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                    uploadStatus.textContent = 'Uploading...';
                    uploadBtn.disabled = true;
                    cancelBtn.disabled = true;

                    try {
                        const response = await fetch('/rush/icon/ajax-upload/', {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': csrfToken,
                            },
                            body: formData
                        });

                        const data = await response.json();

                        if (response.ok) {
                            // Add new tile to the widget
                            const newTile = document.createElement('div');
                            newTile.className = 'tile selected';
                            newTile.dataset.value = data.id;
                            newTile.innerHTML = `<img src="${data.url}" alt="">`;

                            // Insert before upload tile
                            const uploadTile = widget.querySelector('.upload-tile');
                            widget.insertBefore(newTile, uploadTile);

                            // Add to select options
                            const select = widget.querySelector('.tiled-fk-select');
                            const option = document.createElement('option');
                            option.value = data.id;
                            option.selected = true;
                            select.appendChild(option);

                            // Deselect other tiles
                            widget.querySelectorAll('.tile').forEach(t => t.classList.remove('selected'));
                            newTile.classList.add('selected');

                            // Add click handler to new tile
                            newTile.addEventListener('click', () => {
                                widget.querySelectorAll('.tile').forEach(t => t.classList.remove('selected'));
                                newTile.classList.add('selected');
                                select.value = newTile.dataset.value;
                            });

                            // Close modal
                            modal.style.display = 'none';
                            fileInput.value = '';
                            previewContainer.style.display = 'none';
                            uploadStatus.textContent = '';
                        } else {
                            uploadStatus.textContent = 'Error: ' + (data.error || 'Upload failed');
                        }
                    } catch (error) {
                        uploadStatus.textContent = 'Error: ' + error.message;
                    } finally {
                        uploadBtn.disabled = false;
                        cancelBtn.disabled = false;
                    }
                });
            });
        </script>

        <style>
            .tiled-foreignkey-widget {
                display: flex;
                flex-wrap: wrap;
                width: 340px; /* controls 5 tiles per row */
                gap: 10px;
                justify-content: left;
                margin-top: 8px;
            }

            .tiled-foreignkey-widget .tile {
                width: 60px;
                height: 60px;
                border: 2px solid #ddd;
                border-radius: 6px;
                box-sizing: border-box;
                cursor: pointer;
                display: flex;
                padding: 4px;
                justify-content: center;
                align-items: center;
                background: #fafafa;
                transition: border 0.18s ease, box-shadow 0.18s ease;
            }

            .tiled-foreignkey-widget .tile:hover {
                border-color: #4285f4;
                box-shadow: 0 0 4px rgba(66,133,244,0.4);
            }

            .tiled-foreignkey-widget .tile.selected {
                border-color: #1e65d6;
                background: #e8f0fe;
                box-shadow: 0 0 0 2px rgba(30,101,214,0.3);
            }

            .tiled-foreignkey-widget img {
                width: 100%;
                height: auto;
                object-fit: contain;
            }

            /* Upload tile styles */
            .tiled-foreignkey-widget .upload-tile {
                border: 2px dashed #aaa;
                background: #f5f5f5;
            }

            .tiled-foreignkey-widget .upload-tile:hover {
                border-color: #4285f4;
                background: #e8f0fe;
            }

            .tiled-foreignkey-widget .plus-icon {
                font-size: 32px;
                color: #666;
                font-weight: 300;
            }

            /* Modal styles */
            .upload-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
            }

            .upload-modal .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
            }

            .upload-modal .modal-content {
                position: relative;
                background: white;
                margin: 100px auto;
                padding: 30px;
                width: 500px;
                max-width: 90%;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }

            .upload-modal h3 {
                margin-top: 0;
                margin-bottom: 20px;
                font-size: 20px;
            }

            .upload-modal .icon-file-input {
                display: block;
                margin-bottom: 15px;
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }

            .upload-modal .preview-container {
                margin-bottom: 15px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                background: #fafafa;
            }

            .upload-modal .preview-image {
                max-width: 200px;
                max-height: 200px;
            }

            .upload-modal .modal-actions {
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }

            .upload-modal button {
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }

            .upload-modal .upload-btn {
                background: #4285f4;
                color: white;
                flex: 1;
            }

            .upload-modal .upload-btn:hover {
                background: #357ae8;
            }

            .upload-modal .upload-btn:disabled {
                background: #ccc;
                cursor: not-allowed;
            }

            .upload-modal .cancel-btn {
                background: #f1f1f1;
                color: #333;
            }

            .upload-modal .cancel-btn:hover {
                background: #e1e1e1;
            }

            .upload-modal .upload-status {
                color: #d32f2f;
                font-size: 14px;
                min-height: 20px;
            }
        </style>
        """
        engine = Engine()
        template = engine.from_string(template_str)
        html = template.render(Context(context))
        return mark_safe(html)
