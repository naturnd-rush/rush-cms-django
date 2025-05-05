/**
 * This script refreshes map data using the GraphQL API whenever the "map_data" Django
 * admin field is changed and injects it into the page as a hidden element so it can be
 * used to render the Layer's map preview.
 */
document.addEventListener('DOMContentLoaded', function () {
    const mapDataEl = document.getElementById('id_map_data');
    if (mapDataEl) {
        mapDataEl.addEventListener('change', function () {
            const selectedId = this.value;
            if (!selectedId) return;
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
                    variables: {id: selectedId},
                }),
            })
            .then((res) => res.json())
            .then((response) => {
                const mapData = response.data.mapData;
                console.log("GeoJSON data:", mapData.geojson);
                // You can now use it in Leaflet or wherever you want
            })
            .catch((err) => {
                console.error("GraphQL error:", err);
            });
            // fetch(`/admin/api/related-object/${selectedId}/`)  // Match your URL pattern
            //     .then(response => response.json())
            //     .then(data => {
            //         // Render the data somewhere on the page
            //         let previewBox = document.getElementById('related-preview');
            //         if (!previewBox) {
            //             previewBox = document.createElement('div');
            //             previewBox.id = 'related-preview';
            //             mapDataEl.parentElement.appendChild(previewBox);
            //         }
            //         previewBox.innerHTML = `
            //             <strong>Preview:</strong><br>
            //             Field 1: ${data.field1}<br>
            //             Field 2: ${data.field2}<br>
            //             Field 3: ${data.field3}
            //         `;
            // });
        });
    }
});