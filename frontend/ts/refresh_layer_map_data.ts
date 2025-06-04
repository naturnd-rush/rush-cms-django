import { getStyleData, StyleNotFound, Style } from "./graphql.js";
import * as L from "leaflet";
/// <reference types="leaflet" />

/************
 * This script refreshes map data using the GraphQL API whenever the "map_data" Django
 * admin field is changed and injects it into the page as a hidden element so it can be
 * used to render the Layer's map preview.
 ************/


async function getLayerStyleData(): Promise<Array<Style>> {
    
    const styles: Array<Style> = [];
    const stylesOnLayerSelector = "[id^='id_stylesonlayer_set-'][id$='-style']";
    const stylesOnLayerEls = document.querySelectorAll(stylesOnLayerSelector);

    for(const stylesOnLayerEl of stylesOnLayerEls){
        if (!(stylesOnLayerEl instanceof HTMLSelectElement)) {
            console.error("Expected element to be an HTMLSelectElement: ", stylesOnLayerEl);
            continue;
        }
        const styleModelId = stylesOnLayerEl.value;
        if (styleModelId === ""){
            // empty style dropdown
            continue;
        }
        const style = await getStyleData(styleModelId);
        if (style instanceof StyleNotFound){
            console.error("Style not found.", {"id": styleModelId});
            continue;
        }
        styles.push(style);
    }
    
    return styles;
}

document.addEventListener('DOMContentLoaded', function () {

    getLayerStyleData().then(styleList => console.log(styleList))

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