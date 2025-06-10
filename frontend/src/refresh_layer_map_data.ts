import {type Style, type StyleOnLayerResponse, getStylesOnLayerById} from "./graphql"

/************
 * This script refreshes map data using the GraphQL API whenever the "map_data" Django
 * admin field is changed and injects it into the page as a hidden element so it can be
 * used to render the Layer's map preview.
 ************/

interface StyleOnLayer{
    style: Style,
    feature_mapping: string,
}

async function getLayerStyleData(): Promise<Array<StyleOnLayer>> {
    // TODO: This should be querying Style not StyleOnLayerResponse via the graphQL API because relying on the styleonlayerids to fetch data
    // will fail when a new styleonlayer inline row is created (the styleonlayer model hasn't yet been saved and so there will be nothing to fetch!)
    const result: Array<StyleOnLayer> = [];
    for (let inlineRow of document.querySelectorAll("tr[id*='stylesonlayer_set-']")){
        // for each styleOnLayer inline group
        const modelId = inlineRow.querySelector("[id*='style-on-layer-id-hook']")?.innerHTML;
        const featureMapping = (inlineRow.querySelector("textarea[id*='feature_mapping']") as HTMLInputElement | null)?.value;
        if (!(modelId && featureMapping)){
            // most likely an empty inline
            continue;
        }
        const response = await getStylesOnLayerById(modelId);
        result.push({
            style: response.style,
            feature_mapping: featureMapping,
        });
    }
    return result;
}

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

document.addEventListener('DOMContentLoaded', () => {

    let layerStyleData: Array<StyleOnLayer> = [];

    inlineElements.featureMappings.addEventListener((event) => {
        console.log("Feature changed! ", event);
    });
    inlineElements.styles.addEventListener((mutation) => {
        console.log("Style changed: ", mutation);
    });
    

    // if (input) {
    //     input.addEventListener('input', (event) => {
    //     const target = event.target as HTMLInputElement;
    //     console.log('New value:', target.value);
    //     });
    // }

    getLayerStyleData().then(data => console.log(data));

    // const select = document.getElementById('id_map_data');
    // const stylesOnLayersGroup = document.getElementById('stylesonlayer_set-group');

    // // Initialize leaflet map
    // let map = L.map('map-preview').setView([0, 0], 2);
    // L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    //     maxZoom: 18,
    //     attribution: '© OpenStreetMap contributors'
    // }).addTo(map);

    // let geoJsonLayer; // updated by drawMapPreview
    // const drawMapPreview = () => {

    //     if (!select.value) {
    //         let emptyMapData = JSON.parse("\{\}"); // empty GeoJson data
    //         if (geoJsonLayer) {
    //             map.removeLayer(geoJsonLayer);
    //         }
    //         geoJsonLayer = L.geoJSON(emptyMapData).addTo(map);
    //         map.fitBounds(geoJsonLayer.getBounds());
    //     }
    //     const query = `
    //         query ($id: UUID!) {
    //             mapData(id: $id) {
    //                 geojson
    //             }
    //         }
    //     `;
    //     fetch("/graphql/", {
    //         method: "POST",
    //         headers: {
    //             "Content-Type": "application/json",
    //             "Accept": "application/json",
    //             // TODO Add CSRF token here
    //         },
    //         body: JSON.stringify({
    //             query: query,
    //             variables: {id: select.value},
    //         }),
    //     })
    //     .then((res) => res.json())
    //     .then((response) => {
    //         let mapData = response.data.mapData.geojson;
    //         try {
    //             mapData = JSON.parse(mapData);
    //         } catch (e) {
    //             console.warn("Invalid GeoJSON:", e);
    //             mapData = JSON.parse("\{\}"); // empty GeoJson data
    //         }
    //         finally {
    //             if (geoJsonLayer) {
    //                 map.removeLayer(geoJsonLayer);
    //             }

    //             // Get styles on layers object ids
    //             const styles = [];
    //             document.querySelectorAll("[id^='id_stylesonlayer_set-'][id$='-style']").forEach(input => {
    //                 if (input.value) {
    //                     let styleId = input.value;
    //                     const query = `
    //                         query ($id: UUID!) {
    //                             style(id: $id) {
    //                                 drawStroke
    //                                 strokeColor
    //                                 strokeWeight
    //                                 strokeOpacity
    //                                 strokeLineCap
    //                                 strokeLineJoin
    //                                 strokeDashArray
    //                                 strokeDashOffset
    //                                 drawFill
    //                                 fillColor
    //                                 fillOpacity
    //                             }
    //                         }
    //                     `;
    //                     fetch("/graphql/", {
    //                         method: "POST",
    //                         headers: {
    //                             "Content-Type": "application/json",
    //                             "Accept": "application/json",
    //                             // TODO Add CSRF token here
    //                         },
    //                         body: JSON.stringify({
    //                             query: query,
    //                             variables: {id: styleId},
    //                         }),
    //                     })
    //                     .then((res) => res.json())
    //                     .then((response) => {
    //                         let style = response.data.style;
    //                         styles.push(style);
    //                         const mainStyle = styles[0];
    //                         console.log('main style vvv');
    //                         console.log(mainStyle);
    //                         let geoJsonLayer = L.geoJSON(mapData, {
    //                             style: function (feature) {
    //                                 return {
    //                                     color: mainStyle.strokeColor,
    //                                     weight: mainStyle.strokeWeight,
    //                                     opacity: mainStyle.strokeOpacity,
    //                                     lineCap: mainStyle.strokeLineCap,
    //                                     lineJoin: mainStyle.strokeLineJoin,
    //                                     dashArray: mainStyle.strokeDashArray,
    //                                     dashOffset: mainStyle.strokeDashOffset, 
    //                                     fillColor: mainStyle.fillColor,
    //                                     fillOpacity: parseFloat(mainStyle.fillOpacity),
    //                                 };
    //                             }
    //                         }).addTo(map);
    //                         map.fitBounds(geoJsonLayer.getBounds());
    //                     });
    //                 }
    //             });
    //             // // Default styles
    //             // geoJsonLayer = L.geoJSON(mapData, {
    //             //     style: function (feature) {
    //             //         return {
    //             //         color: "purple",         // stroke color
    //             //         weight: 2,               // stroke width
    //             //         opacity: 1.0,            // stroke opacity
    //             //         fillColor: "transparent",// no fill
    //             //         fillOpacity: 0
    //             //         };
    //             //     }
    //             // }).addTo(map);

    //         }})
    //     .catch((err) => {
    //         console.error("GraphQL error:", err);
    //     });
    // };

    // // Add event-listener to id_map_data so that when it changes we draw the map preview.
    // const mapDataEl = document.getElementById('id_map_data');
    // if (mapDataEl) {
    //     mapDataEl.addEventListener('change', function () {
    //         drawMapPreview();
    //     });
    // }

    // if (stylesOnLayersGroup) {
    //     stylesOnLayersGroup.addEventListener('change', function () {
    //         drawMapPreview();
    //     });
    // }

    // // Draw map preview after initial page load
    // drawMapPreview();

});