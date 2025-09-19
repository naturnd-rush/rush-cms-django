class t extends Error{constructor(r){super(r)}}async function s(a){const r=await fetch("/graphql/",{method:"POST",headers:{"Content-Type":"application/json",Accept:"application/json"},body:a}),e=await r.json();if(r.status!==200)throw e.errors===null||e.errors===void 0?new t("GraphQL response code ("+r.status+") is not 200 but no errors were sent back in the response!"):new t(JSON.stringify(e.errors));return e}async function n(a){return(await s(JSON.stringify({query:`
        query ($id: UUID!) {
            style(id: $id) {
                drawStroke
                strokeColor
                strokeWeight
                strokeOpacity
                strokeLineJoin
                strokeLineCap
                strokeDashArray
                strokeDashOffset
                drawFill
                fillColor
                fillOpacity
                drawMarker
                markerIcon
                markerIconOpacity
                markerBackgroundColor
            }
        }
    `,variables:{id:a}}))).data.style}async function i(a){const e=await s(JSON.stringify({query:`
        query ($name: String!) {
            mapDataByName(name: $name) {
                geojson
            }
        }
    `,variables:{name:a}}));return console.debug("getMapDataByName response: ",e),e.data.mapDataByName}export{i as a,n as g};
