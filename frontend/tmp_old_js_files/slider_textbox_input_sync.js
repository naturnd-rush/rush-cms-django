/***
 * This script synchronizes number slider <--> textbox input fields on a Django admin changeform.
 * Without this script, changing the slider may not update it's corresponding textbox input.
 */
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".dual-slider-textbox").forEach(container => {
        const fieldname = container.dataset.fieldname;
        const slider = container.querySelector(`#slider_${fieldname}`);
        const textbox = container.querySelector(`#id_${fieldname}`);

        if (!slider || !textbox) return;

        // Slider → Textbox
        slider.addEventListener("input", () => {
            textbox.value = slider.value;

            // Dispatch event to update the style-preview (it reads from the textbox value).
            textbox.dispatchEvent(new Event("input", { bubbles: false }));
        });

        // Textbox → Slider
        textbox.addEventListener("input", () => {
            if (textbox.value === "" || isNaN(textbox.value)) return;
            slider.value = textbox.value;
        });

        textbox.addEventListener("focus", () => {
            // Auto-highlight textbox number for easy editing.
            textbox.select();
        });
    });
});
