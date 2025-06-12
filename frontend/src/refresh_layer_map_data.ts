import {type Style, getStyleById, getMapDataById} from "./graphql"
import type { FeatureCollection, Geometry, Feature } from 'geojson';
import type {PathOptions, StyleFunction} from "leaflet"
import * as L from 'leaflet';
import { Parser } from 'expr-eval';

/************
 * This script refreshes map data using the GraphQL API whenever the "map_data" Django
 * admin field is changed and injects it into the page as a hidden element so it can be
 * used to render the Layer's map preview.
 ************/

interface StyleOnLayer{
    style: Style,
    feature_mapping: string,
}

interface MapPreviewState {
    stylesOnLayer: Array<StyleOnLayer>,
    currentLayer: L.GeoJSON<any, Geometry> | null,
}

interface MapPreviewUpdate {
    type: "Style" | "MapData",
}
interface StyleUpdate extends MapPreviewUpdate {
    newStylesOnLayers: Array<StyleOnLayer>,
}
interface MapDataUpdate extends MapPreviewUpdate {
    newGeoJsonData: FeatureCollection<Geometry, any> | null,
}

/**
 * Get the currently configured style data for this layer.
 */
async function getStyleUpdate(): Promise<StyleUpdate> {
    const stylesOnLayers: Array<StyleOnLayer> = [];
    for (let inlineRow of document.querySelectorAll("tr[id*='stylesonlayer_set-']")){
        // for each styleOnLayer inline group
        const styleId = (inlineRow.querySelector("select[id*='-style']") as HTMLSelectElement)?.value;
        const featureMapping = (inlineRow.querySelector("textarea[id*='feature_mapping']") as HTMLInputElement | null)?.value;
        if (!(styleId && featureMapping)){
            // most likely an empty inline
            continue;
        }
        const style = await getStyleById(styleId);
        if (style !== null){
            stylesOnLayers.push({
                style: style,
                feature_mapping: featureMapping,
            });
        }
    }
    return {
        type: "Style",
        newStylesOnLayers: stylesOnLayers,
    };
}

/**
 * Fetch GeoJSON using the UUID present in the map-data input field.
 */
async function getMapDataUpdate(mapDataSelectEl: HTMLSelectElement): Promise<MapDataUpdate>{    
    let mapDataId = mapDataSelectEl.value;
    const clearMapData = {type: "MapData", newGeoJsonData: null} as MapDataUpdate;
    if (mapDataId === null || mapDataId === ""){
        return clearMapData;
    }
    let mapData = await getMapDataById(mapDataId);
    if (mapData === null){
        return clearMapData;
    }
    const geojson = JSON.parse(mapData.geojson);
    if (geojson.features === null || geojson.features === undefined){
        return clearMapData;
    }
    return {
        type: "MapData",
        newGeoJsonData: geojson as FeatureCollection,
    }
}

/**
 * Namespaced accessor for adding StyleOnLayer inline element event listeners. 
 * This code isn't the most efficient, but I'm leaving it for now because it works...
 */
const inlineElements = {
    styles: {
        addEventListener: (callback: (mutation: MutationRecord) => void): void => {
            const inlineGroup = document.getElementById('stylesonlayer_set-group');
            if (inlineGroup !== null) {
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.target instanceof HTMLSelectElement && mutation.type === "childList"){
                            callback(mutation);
                        }
                    });
                });
                observer.observe(inlineGroup, {childList: true, subtree: true});
            }
        },
    },
    featureMappings: {
        addEventListener: (callback: (event: Event) => void): void => {
            document.addEventListener('input', (event) => {
                const target = event.target;
                const featureChanged = target instanceof HTMLTextAreaElement && target.id.includes('feature_mapping');
                if (featureChanged) {
                    callback(event);
                }
            });
        },
    },
};

function interpolateHexColor(color1: string, color2: string, t: number): string {
  // Ensure t is between 0 and 1
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

function hexToRgb(hex: string): { r: number, g: number, b: number } | null {
  const match = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i);
  if (!match) return null;

  return {
    r: parseInt(match[1], 16),
    g: parseInt(match[2], 16),
    b: parseInt(match[3], 16),
  };
}

function rgbToHex(r: number, g: number, b: number): string {
  return `#${[r, g, b]
    .map((x) => x.toString(16).padStart(2, '0'))
    .join('')}`;
}

/**
 * Interpolate evnly between two numbers, take one of the numbers if the other one is undefined, 
 * or return undefined if both numbers are none or undefined.
 */
function interpolateNumbers(n1: number | undefined | null, n2: number | undefined | null): number | undefined {
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
 * TODO
 */
function coerceNumbersDeep(input: any): any {
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


function drawMapPreview(map: L.Map, state: MapPreviewState, update: MapPreviewUpdate): void{
    console.log("Drawing map preview with state: ", state);

    // Always remove the previous layer, if there is one, from the map. 
    // Otherwse, it overlaps with the new layer being drawn.
    if (state.currentLayer !== null){
        map.removeLayer(state.currentLayer);
    }

    // Update currentLayer if we are receiving new map data.
    if ("MapData" === update.type){
        const newGeoJson = (update as MapDataUpdate).newGeoJsonData;
        if (newGeoJson === null){
            state.currentLayer = null;
        } else {
            state.currentLayer = L.geoJSON(newGeoJson);
            map.fitBounds(state.currentLayer.getBounds());
        }
    }

    // Update stylesOnLayer if we are receiving new style data
    else if ("Style" === update.type) {
        state.stylesOnLayer = (update as StyleUpdate).newStylesOnLayers;
    }

    /**
     * Begin drawing the map.
     */

    if (state.currentLayer === null){
        // Exit if there is no layer to draw at this point...
        return;
    }

    const parser = new Parser();
    const styleFunc = (feature: Feature<Geometry, any>): PathOptions => {

        // Find which styles should be applied to this feature by testing
        // the feature mapping against the feature's properties.
        let appliedStyles: Array<Style> = [];
        for (let styleOnLayer of state.stylesOnLayer){
            try{
                const expr = parser.parse(styleOnLayer.feature_mapping);
                if (expr.evaluate(coerceNumbersDeep(feature.properties)) === true){
                    appliedStyles.push(styleOnLayer.style);
                }
            } catch (error){
                // Don't apply style if parsing fails
            }
        }

        // Build path options from the styles. If there are multiple
        // styles being applied to the same feature, we just give our
        // best guess at how the user wants their map to look by using
        // linear interpolation on what we can and overriding the rest...
        // TODO: Talked with Doug today and decided to send serialized JSON leaflet
        //       map layer object back to the frontend, so that we can resolve multiple styled
        //       applied to the same feature in a single location, and simplify the frontend code.
        //       Mark this TODO as done when an endpoint is exposed via GraphQL to get serialized leaflet
        //       layer data, which is serialized on layer model save.
        
        let drawFill = false;
        let drawStroke = false;
        let drawMarker = false;

        let fillOpacity = undefined;
        let strokeOpacity = undefined;
        let markerIconOpacity = undefined;

        let fillColor = undefined;
        let strokeColor = undefined;
        
        let strokeWeight = undefined;

        // Style attributes that can't be interpolated (just take the most recent one from the applied styles)
        let markerIcon = undefined;
        let strokeDashArray = "";
        let strokeDashOffset = undefined; // technically can be interpolated but I don't think it would be intuitive for a user
        let strokeLineCap = "round";
        let strokeLineJoin = "round";


        for (let style of appliedStyles){

            // If one style draws something then the combined style will also draw that thing
            if (style.drawFill === true){
                drawFill = true;
            }
            if (style.drawStroke === true){
                drawStroke = true;
            }
            if (style.drawMarker === true){
                drawMarker = true;
            }

            fillOpacity = interpolateNumbers(fillOpacity, style.fillOpacity);

            // // When two styles are combined their opacity is averaged
            // if (fillOpacity === undefined){
            //     if (!Number.isNaN(style.fillOpacity)){
            //         fillOpacity = style.fillOpacity;
            //     }
            // } else {
            //     // interpolate fill opacity
            //     fillOpacity = (Number.parseFloat(fillOpacity) + style.fillOpacity) / 2);
            // }
            if (strokeOpacity === undefined){
                strokeOpacity = style.strokeOpacity;
            } else {
                // interpolate stroke opacity
                strokeOpacity = (strokeOpacity + style.strokeOpacity) / 2;
            }
            if (markerIconOpacity === undefined){
                markerIconOpacity = style.markerIconOpacity;
            } else {
                // interpolate marker-icon opacity
                markerIconOpacity = (markerIconOpacity + style.markerIconOpacity) / 2;
            }

            if (fillColor === undefined){
                fillColor = style.fillColor;
            } else {
                // interpolate fill color
                fillColor = interpolateHexColor(fillColor, style.fillColor, 0.5);
            }
            if (strokeColor === undefined){
                strokeColor = style.strokeColor;
            } else {
                // interpolate stroke color
                strokeColor = interpolateHexColor(strokeColor, style.strokeColor, 0.5);
            }

            strokeWeight = interpolateNumbers(strokeWeight, style.strokeWeight);
            // if (strokeWeight === undefined){
            //     strokeWeight = style.strokeWeight;
            // } else {
            //     // interpolate stroke weight
            //     strokeWeight = (strokeWeight + style.strokeWeight) / 2;
            // }

            // just set / override the rest of the attributes
            if (style.markerIcon !== ""){
                markerIcon === style.markerIcon;
            }
            if (style.strokeDashArray !== null){
                strokeDashArray = style.strokeDashArray;
            }
            if (style.strokeDashOffset !== null){
                strokeDashOffset = style.strokeDashOffset;
            }
            strokeLineJoin = style.strokeLineJoin;
            strokeLineCap = style.strokeLineCap;
        }
        const featureStyle = {
            
            fill: drawFill,
            fillColor: fillColor,
            fillOpacity: fillOpacity,

            stroke: drawStroke,
            weight: strokeWeight,
            color: strokeColor,
            dashArray: strokeDashArray,
            dashOffset: strokeDashOffset,
            lineCap: strokeLineCap as L.LineCapShape,
            lineJoin: strokeLineJoin as L.LineJoinShape,

            // TODO: Handle markers
        };
        //console.log("FeatureStyle: ", featureStyle);
        return featureStyle;
    };
    
    const styledGeoJsonData = L.geoJSON(state.currentLayer.toGeoJSON(), {
        style: styleFunc as StyleFunction,
        onEachFeature: (feature, layer) => {
            // // Optionally bind popups or other handlers
            // if (feature.properties && feature.properties.name) {
            //     layer.bindPopup(`Name: ${feature.properties.name}`);
            // }
        }
    });
    state.currentLayer = styledGeoJsonData;
    styledGeoJsonData.addTo(map)

    // if (rawGeoJson.type === 'FeatureCollection') {
    //     const featureCollection = rawGeoJson as FeatureCollection<Geometry, any>;

    //     const layer = L.geoJSON(featureCollection, {
    //         onEachFeature: (feature, layer) => {
    //             layer.bindPopup('Feature ID: ' + (feature.id ?? 'none'));
    //         },
    //     });

    //     layer.addTo(map);
    // } else {
    //     console.error('Expected GeoJSON type="FeatureCollection", but was:', state.geojson.type);
    // }
}

document.addEventListener('DOMContentLoaded', () => {

    // Initialize leaflet map
    let map = L.map('map-preview').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '© OpenStreetMap contributors',
    }).addTo(map);

    // Initialize object to track map preview state
    let mapPreviewState: MapPreviewState = {
        stylesOnLayer: [],
        currentLayer: null,
    };
    
    // Listen to redraw the map when a feature-mapping is changed. Because I want to update the
    // map live while the user is typing in the feature mapping text areas, I use the HTML "input"
    // event. However, it is likely that this will create too many updates, and subsequent API calls
    // to the GraphQL API for style data. To fix this, I simply keep track of whether we should update
    // the style data using this even listener, and check to dispatch this update every second or so.
    let fmUpdate = false;
    inlineElements.featureMappings.addEventListener(() => fmUpdate = true);
    const sendFmUpdateAndPoll = () => {
        if (fmUpdate === true){
            getStyleUpdate().then(styleUpdate => {
                console.log('Updating map styles based on a feature-mapping change!');
                drawMapPreview(map, mapPreviewState, styleUpdate);
            });
        }
        fmUpdate = false;
        setTimeout(sendFmUpdateAndPoll, 1000);
    };
    setTimeout(sendFmUpdateAndPoll, 1000);

    // Listen to redraw the map when a style is changed.
    inlineElements.styles.addEventListener(() => {
        getStyleUpdate().then(styleUpdate => {
            drawMapPreview(map, mapPreviewState, styleUpdate);
        });
    });

    // Hook into the map-data selection element
    const mapDataSelectEl = (document.getElementById('id_map_data') as HTMLSelectElement);
    if (mapDataSelectEl === null){
        throw new Error("Expected to find a DOM element with id='id_map_data'.");
    }
    
    // Listen to redraw the map when the underlying map-data is changed.
    mapDataSelectEl.addEventListener("change", () => {
        getMapDataUpdate(mapDataSelectEl).then(mapDataUpdate => {
            drawMapPreview(map, mapPreviewState, mapDataUpdate);
        })
    });

    // Draw the initial map using the current map-data and style info.
    Promise.all([
        getStyleUpdate(), 
        getMapDataUpdate(mapDataSelectEl),
    ]).then(([styleUpdate, mapDataUpdate]: [StyleUpdate, MapDataUpdate]) => {
        // Inefficient, but meh.
        drawMapPreview(map, mapPreviewState, mapDataUpdate);
        drawMapPreview(map, mapPreviewState, styleUpdate);
    });







    let geoJsonLayer; // updated by drawMapPreview
    const drawMapPreviewOld = () => {

        if (!select.value) {
            let emptyMapData = JSON.parse("\{\}"); // empty GeoJson data
            if (geoJsonLayer) {
                map.removeLayer(geoJsonLayer);
            }
            geoJsonLayer = L.geoJSON(emptyMapData).addTo(map);
            map.fitBounds(geoJsonLayer.getBounds());
        }
        const query = `
            query ($id: UUID!) {
                mapData(id: $id) {
                    geojson
                }
            }
        `;
        fetch("/graphql/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                // TODO Add CSRF token here
            },
            body: JSON.stringify({
                query: query,
                variables: {id: select.value},
            }),
        })
        .then((res) => res.json())
        .then((response) => {
            let mapData = response.data.mapData.geojson;
            try {
                mapData = JSON.parse(mapData);
            } catch (e) {
                console.warn("Invalid GeoJSON:", e);
                mapData = JSON.parse("\{\}"); // empty GeoJson data
            }
            finally {
                if (geoJsonLayer) {
                    map.removeLayer(geoJsonLayer);
                }

                // Get styles on layers object ids
                const styles = [];
                document.querySelectorAll("[id^='id_stylesonlayer_set-'][id$='-style']").forEach(input => {
                    if (input.value) {
                        let styleId = input.value;
                        const query = `
                            query ($id: UUID!) {
                                style(id: $id) {
                                    drawStroke
                                    strokeColor
                                    strokeWeight
                                    strokeOpacity
                                    strokeLineCap
                                    strokeLineJoin
                                    strokeDashArray
                                    strokeDashOffset
                                    drawFill
                                    fillColor
                                    fillOpacity
                                }
                            }
                        `;
                        fetch("/graphql/", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                                // TODO Add CSRF token here
                            },
                            body: JSON.stringify({
                                query: query,
                                variables: {id: styleId},
                            }),
                        })
                        .then((res) => res.json())
                        .then((response) => {
                            let style = response.data.style;
                            styles.push(style);
                            const mainStyle = styles[0];
                            console.log('main style vvv');
                            console.log(mainStyle);
                            let geoJsonLayer = L.geoJSON(mapData, {
                                style: function (feature) {
                                    return {
                                        color: mainStyle.strokeColor,
                                        weight: mainStyle.strokeWeight,
                                        opacity: mainStyle.strokeOpacity,
                                        lineCap: mainStyle.strokeLineCap,
                                        lineJoin: mainStyle.strokeLineJoin,
                                        dashArray: mainStyle.strokeDashArray,
                                        dashOffset: mainStyle.strokeDashOffset, 
                                        fillColor: mainStyle.fillColor,
                                        fillOpacity: parseFloat(mainStyle.fillOpacity),
                                    };
                                }
                            }).addTo(map);
                            map.fitBounds(geoJsonLayer.getBounds());
                        });
                    }
                });
                // // Default styles
                // geoJsonLayer = L.geoJSON(mapData, {
                //     style: function (feature) {
                //         return {
                //         color: "purple",         // stroke color
                //         weight: 2,               // stroke width
                //         opacity: 1.0,            // stroke opacity
                //         fillColor: "transparent",// no fill
                //         fillOpacity: 0
                //         };
                //     }
                // }).addTo(map);

            }})
        .catch((err) => {
            console.error("GraphQL error:", err);
        });
    };

    // Add event-listener to id_map_data so that when it changes we draw the map preview.
    const mapDataEl = document.getElementById('id_map_data');
    if (mapDataEl) {
        mapDataEl.addEventListener('change', function () {
            // drawMapPreview();
        });
    }

    if (stylesOnLayersGroup) {
        stylesOnLayersGroup.addEventListener('change', function () {
            // drawMapPreview();
        });
    }

    // Draw map preview after initial page load
    // drawMapPreview();

});