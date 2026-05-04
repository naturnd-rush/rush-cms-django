class o extends Error{constructor(r){super(r)}}async function s(t){const r=await fetch("/graphql/",{method:"POST",headers:{"Content-Type":"application/json",Accept:"application/json"},body:t}),e=await r.json();if(r.status!==200)throw e.errors===null||e.errors===void 0?new o("GraphQL response code ("+r.status+") is not 200 but no errors were sent back in the response!"):new o(JSON.stringify(e.errors));return e}async function a(t){return(await s(JSON.stringify({query:`
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
                markerSize
                drawCircle
                circleRadius
                circleFillColor
                circleFillOpacity
                circleStrokeColor
                circleStrokeDashArray
                circleStrokeDashOffset
                circleStrokeLineCap
                circleStrokeLineJoin
                circleStrokeOpacity
                circleStrokeWeight
            }
        }
    `,variables:{id:t}}))).data.style}export{a as g};
