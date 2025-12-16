class s extends Error{constructor(e){super(e)}}async function a(r){const e=await fetch("/graphql/",{method:"POST",headers:{"Content-Type":"application/json",Accept:"application/json"},body:r}),t=await e.json();if(e.status!==200)throw t.errors===null||t.errors===void 0?new s("GraphQL response code ("+e.status+") is not 200 but no errors were sent back in the response!"):new s(JSON.stringify(t.errors));return t}async function n(r){return(await a(JSON.stringify({query:`
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
                markerBackgroundOpacity
            }
        }
    `,variables:{id:r}}))).data.style}async function i(r){return(await a(JSON.stringify({query:`
        query ($id: UUID!) {
            mapData(id: $id) {
                geojson
                providerState
            }
        }
    `,variables:{id:r}}))).data.mapData}export{i as a,n as g};
