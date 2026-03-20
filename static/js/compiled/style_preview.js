import{l as u,g as N}from"./utils/math.js";import{g as O}from"./graphql.js";import{e as m,a as v}from"./utils/timing.js";function w(t){let o="";for(let i of t)o+=i.x+","+i.y+" ";return o}function h(t){const r=t.markerOptions.markerSize,a=Math.sqrt(Math.pow(r/2,2)+Math.pow(r/2,2)),l=[new u.Point(40,40),new u.Point(200,80),new u.Point(280,160),new u.Point(120,240),new u.Point(40,160)];let e=`
    <svg
        width="400px"
        height="400px"
        xmlns="http://www.w3.org/2000/svg"
    >
    <polygon 
        points="${w(l)}"
    `;t.drawStroke&&(e+=`
            stroke="${t.strokeOptions.color}"
            stroke-width="${t.strokeOptions.weight}"
            stroke-opacity="${t.strokeOptions.opacity}"
            stroke-linecap="${t.strokeOptions.lineCap}"
            stroke-linejoin="${t.strokeOptions.lineJoin}"
            stroke-dasharray="${t.strokeOptions.dashArray}"
            stroke-dashoffset="${t.strokeOptions.dashOffset}"
        `),t.drawFill?e+=`
            fill="${t.fillOptions.color}"
            fill-opacity="${t.fillOptions.opacity}"
        `:e+='fill="none"',e+="/>";const n=N(l);return t.drawMarker&&(e+=`
        <circle 
            id="marker-centroid"
            r="${a}px"
            fill=${t.markerOptions.bgColor}
            opacity=${t.markerOptions.bgOpacity}
            cx=${n.x}
            cy=${n.y}
        />
        `),e+="</svg>",t.drawMarker&&t.markerOptions.data!==null&&(e+=`
        <img 
            id="marker-image"
            src="${t.markerOptions.data}"
            width="${r}"
            height="${r}"
            style='
                position: absolute;
                left: ${n.x-r/2}px;
                top: ${n.y-r/2}px;
                opacity: ${t.markerOptions.markerOpacity}
            '
        />'
        `),e}function d(t){let o=t.parentElement;for(;o!==null&&!o.classList.contains("form-row");)o=o.parentElement;return o}function p(t,o,i){var a;(a=d(o))==null||a.style.setProperty("background-color","#FFFFFF");for(let l of y(t,i)){const e=d(l);e!==null&&(e.style.display="none")}}function s(t,o,i){var a;(a=d(o))==null||a.style.setProperty("background-color","#E2DBC4");for(let l of y(t,i)){const e=d(l);e!==null&&(e.style.display="block")}}function y(t,o){let i=[];for(let r of o)r.groupName===t&&r.el!==null&&i.push(r.el);return i}function k(t){return new Promise((o,i)=>{const r=new FileReader;r.onload=()=>o(r.result),r.onerror=()=>i(r.error),r.readAsDataURL(t)})}document.addEventListener("DOMContentLoaded",()=>{(async()=>{var l;const t=m("style_preview"),o=m("injected-style-id").innerHTML,i=m("injected-media-url").innerHTML;v(document,".field-style_preview");let r={drawStroke:!1,drawFill:!1,drawMarker:!1,strokeOptions:{color:"#FFFFFF",opacity:1,weight:1,lineJoin:"",lineCap:"ROUND",dashArray:"",dashOffset:"0"},fillOptions:{color:"#FFFFFF",opacity:1},markerOptions:{bgColor:"#FFFFFF",bgOpacity:1,data:null,markerOpacity:1,markerSize:22}};const a=[{groupName:"Toggle",el:document.querySelector("#id_draw_stroke"),update:e=>{e.checked?s("Stroke",e,a):p("Stroke",e,a),r.drawStroke=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_fill"),update:e=>{e.checked?s("Fill",e,a):p("Fill",e,a),r.drawFill=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_marker"),update:e=>{e.checked?s("Marker",e,a):p("Marker",e,a),r.drawMarker=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_circle"),update:e=>{e.checked?s("Circle",e,a):p("Circle",e,a),r.drawMarker=e.checked},eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_color"),update:e=>r.strokeOptions.color=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_weight"),update:e=>r.strokeOptions.weight=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_opacity"),update:e=>r.strokeOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_cap"),update:e=>r.strokeOptions.lineCap=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_join"),update:e=>r.strokeOptions.lineJoin=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_array"),update:e=>r.strokeOptions.dashArray=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_offset"),update:e=>r.strokeOptions.dashOffset=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_color"),update:e=>r.fillOptions.color=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_opacity"),update:e=>r.fillOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_icon"),update:async e=>{let n=null;if(e.files&&(n=e.files[0]),n){const c=await k(n);r.markerOptions.data=c}else if(o!==""){const c=await O(o);if(c!==null){const g=i+c.markerIcon,_=await(await fetch(g)).blob(),f=await k(_);r.markerOptions.data=f}}else r.markerOptions.data=null},eventName:"change"},{groupName:"Marker",el:document.querySelector("#id_marker_icon_opacity"),update:e=>r.markerOptions.markerOpacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_color"),update:e=>r.markerOptions.bgColor=e.value,eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_opacity"),update:e=>r.markerOptions.bgOpacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_size"),update:e=>{r.markerOptions.markerSize=Number(e.value)},eventName:"input"},{groupName:"Circle",el:document.querySelector("#id_circle_color"),update:e=>r.strokeOptions.color=e.value,eventName:"input"},{groupName:"Circle",el:document.querySelector("#id_circle_radius"),update:e=>r.strokeOptions.color=e.value,eventName:"input"},{groupName:"Circle",el:document.querySelector("#id_circle_weight"),update:e=>r.strokeOptions.weight=Number(e.value),eventName:"input"},{groupName:"Circle",el:document.querySelector("#id_circle_opacity"),update:e=>r.strokeOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Circle",el:document.querySelector("#id_circle_line_cap"),update:e=>r.strokeOptions.lineCap=e.value,eventName:"input"},{groupName:"Circle",el:document.querySelector("#id_circle_line_join"),update:e=>r.strokeOptions.lineJoin=e.value,eventName:"input"},{groupName:"Circle",el:document.querySelector("#id_circle_dash_array"),update:e=>r.strokeOptions.dashArray=e.value,eventName:"input"},{groupName:"Circle",el:document.querySelector("#id_circle_dash_offset"),update:e=>r.strokeOptions.dashOffset=e.value,eventName:"input"}];for(let e of a){const n=async()=>{e.el!==null&&(await e.update(e.el),t.innerHTML=h(r))};(l=e==null?void 0:e.el)==null||l.addEventListener(e.eventName,n),await n()}})()});
