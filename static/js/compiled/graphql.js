class t extends Error{constructor(e){super(e)}}async function o(s){const e=await fetch("/graphql/",{method:"POST",headers:{"Content-Type":"application/json",Accept:"application/json"},body:s}),r=await e.json();if(e.status!==200)throw r.errors===null||r.errors===void 0?new t("GraphQL response code ("+e.status+") is not 200 but no errors were sent back in the response!"):new t(JSON.stringify(r.errors));return r}async function a(s){return(await o(JSON.stringify({query:`
        query ($id: UUID!) {
            stylesOnLayer(id: $id) {
                id
                style {
                    drawStroke
                    strokeColor
                    strokeWeight
                    strokeOpacity
                    strokeLineJoin
                    strokeDashArray
                    strokeDashOffset
                    drawFill
                    fillColor
                    fillOpacity
                    drawMarker
                    markerIcon
                    markerIconOpacity
                }
            }
        }
    `,variables:{id:s}}))).data.stylesOnLayer}export{a as g};
