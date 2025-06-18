/**
 * General utility module. Contains things like RGB -> HEX color conversions, 
 * general DOM utility functions, and parsing / interpolating functions.
 */

/**
 * A promise that resolves immediately if the given HTMLElement exists in the DOM 
 * already, or otherwise when the DOM element is added the future.
 * @param id the id of the DOM element to look for.
 * @returns a Promise containing the HTMLElement once it's been located.
 */
export function waitForElementById(id: string): Promise<HTMLElement> {
  return new Promise((resolve) => {

    const resolveIfFound = () => {
        const element = document.getElementById(id);
        if (element){
            return resolve(element);
        }
    };

    // Return if the element already exists.
    resolveIfFound();

    // Otherwise create an observer to listen for DOM changes.
    const observer = new MutationObserver(resolveIfFound);
    observer.observe(document.body, { childList: true, subtree: true });

  });
}

/**
 * Blend two hexidecimal colors together.
 * @param color1 the first color to interpolate (starting point).
 * @param color2 the second color to interpolate (destination).
 * @param t the distance (between 0 and 1) to move from color 1 towards color 2.
 * @returns a new hexidecimal color.
 */
export function blendHexColors(color1: string, color2: string, t: number): string {

  // Clamp t between 0 and 1
  t = Math.max(0, Math.min(1, t));

  // Convert hex to RGB
  const c1 = hexToRgb(color1);
  const c2 = hexToRgb(color2);

  if (!c1 || !c2) throw new Error("Invalid color format");

  // Interpolate RGB values
  const r = Math.round(c1.r + (c2.r - c1.r) * t);
  const g = Math.round(c1.g + (c2.g - c1.g) * t);
  const b = Math.round(c1.b + (c2.b - c1.b) * t);

  // Convert back to hex
  return rgbToHex(r, g, b);
}

/**
 * Convert a hexidecimal color to an RGB color.
 * @param hex the hexidecimal color to convert.
 * @returns an RBG-formatted color.
 */
function hexToRgb(hex: string): { r: number, g: number, b: number } | null {
  const match = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i);
  if (!match) return null;

  return {
    r: parseInt(match[1], 16),
    g: parseInt(match[2], 16),
    b: parseInt(match[3], 16),
  };
}

/**
 * Convert an RBG color to hexidecimal.
 * @param r the red value.
 * @param g the green value.
 * @param b the blue value.
 * @returns a hexidecimal-formatted color.
 */
function rgbToHex(r: number, g: number, b: number): string {
  return `#${[r, g, b]
    .map((x) => x.toString(16).padStart(2, '0'))
    .join('')}`;
}

/**
 * Interpolate evenly between two numbers, take one of the numbers if the other one is undefined, 
 * or return undefined if both numbers are none or undefined.
 */
export function interpolateNumbers(n1: number | undefined | null, n2: number | undefined | null): number | undefined {
    n1 = isNaN(Number(n1)) ? undefined : Number(n1);
    n2 = isNaN(Number(n2)) ? undefined : Number(n2);
    if (n1 === undefined && n2 === undefined){
        return undefined;
    }
    if (n1 === undefined && n2 !== undefined){
        return n2;
    }
    if (n2 === undefined && n1 !== undefined){
        return n1;
    }
    if (n1 !== undefined && n2 !== undefined){
        return (n1 + n2) / 2;
    }
    return undefined;
}

/**
 * Take any JavaScript object as input and coerce any number-like values to actual numbers, e.g., {foo: "5", ...} --> {foo: 5.0, ...}.
 */
export function coerceNumbersDeep(input: any): any {
    if (Array.isArray(input)) {
        return input.map(coerceNumbersDeep);
    } else if (input !== null && typeof input === 'object') {
        const result: Record<string, any> = {};
        for (const [key, value] of Object.entries(input)) {
            result[key] = coerceNumbersDeep(value);
        }
        return result;
    } else if (typeof input === 'string' || typeof input === 'boolean') {
        const num = Number(input);
        return isNaN(num) ? input : num;
    } else {
        return input;
    }
}
