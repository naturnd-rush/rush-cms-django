/***
 * This script synchronizes number slider <--> textbox input fields on a Django admin changeform.
 * Without this script, changing the slider may not update it's corresponding textbox input.
 */

/**
 * Bind the postion of the slider input when the user changes the input textBox value.
 * @param slider the slider input element whose position should be changed.
 * @param textBox the textBox input element whose value changes to listen to.
 */
function bindSliderToTextBox(slider: HTMLInputElement, textBox: HTMLInputElement): void {
    textBox.addEventListener("input", () => {
        if (textBox.value !== "" && !isNaN(Number(textBox.value))){
            // Set the slider value (i.e., it's "position")
            slider.value = textBox.value;   
        }
    });
    textBox.addEventListener("focus", () => {
        // Auto-highlight textBox number for easy editing.
        textBox.select();
    });
}

/**
 * Bind the textBox input's value when the user moves the slider to a new position.
 * @param textBox the textBox input element whose value should be changed.
 * @param slider the slider input element whose position changes to listen to.
 */
function bindTextBoxToSlider(textBox: HTMLInputElement, slider: HTMLInputElement): void {
    slider.addEventListener("input", () => {
        textBox.value = slider.value;

        // Dispatch event to update the style-preview (it reads from the textbox value), or any 
        // other code that wishes to "listen-in" on slider-textbox input events / changes.
        textBox.dispatchEvent(new Event("input", { bubbles: false }));
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const sliderInputContainers = (document.querySelectorAll(".dual-slider-textbox") as NodeListOf<HTMLDivElement>);
    for (let container of sliderInputContainers){
        const fieldname = container.dataset.fieldname;
        const slider = container.querySelector(`#slider_${fieldname}`) as HTMLInputElement;
        const textBox = container.querySelector(`#id_${fieldname}`) as HTMLInputElement;
        if (slider && textBox){
            bindSliderToTextBox(slider, textBox);
            bindTextBoxToSlider(textBox, slider);
        }
    }
});
