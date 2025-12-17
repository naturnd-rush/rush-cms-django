import{l as p,g as v}from"./utils/math.js";import{g as N}from"./graphql.js";import{e as m,a as h}from"./utils/timing.js";function S(r){let a="";for(let i of r)a+=i.x+","+i.y+" ";return a}function F(r){const n=r.markerOptions.markerSize,l=Math.sqrt(Math.pow(n/2,2)+Math.pow(n/2,2)),t=[new p.Point(40,40),new p.Point(200,80),new p.Point(280,160),new p.Point(120,240),new p.Point(40,160)];let o=`
    <svg
        width="400px"
        height="400px"
        xmlns="http://www.w3.org/2000/svg"
    >
    <polygon 
        points="${S(t)}"
    `;r.drawStroke&&(o+=`
            stroke="${r.strokeOptions.color}"
            stroke-width="${r.strokeOptions.weight}"
            stroke-opacity="${r.strokeOptions.opacity}"
            stroke-linecap="${r.strokeOptions.lineCap}"
            stroke-linejoin="${r.strokeOptions.lineJoin}"
            stroke-dasharray="${r.strokeOptions.dashArray}"
            stroke-dashoffset="${r.strokeOptions.dashOffset}"
        `),r.drawFill?o+=`
            fill="${r.fillOptions.color}"
            fill-opacity="${r.fillOptions.opacity}"
        `:o+='fill="none"',o+="/>";const s=v(t);return r.drawMarker&&(o+=`
        <circle 
            id="marker-centroid"
            r="${l}px"
            fill=${r.markerOptions.bgColor}
            opacity=${r.markerOptions.bgOpacity}
            cx=${s.x}
            cy=${s.y}
        />
        `),o+="</svg>",r.drawMarker&&r.markerOptions.data!==null&&(o+=`
        <img 
            id="marker-image"
            src="${r.markerOptions.data}"
            width="${n}"
            height="${n}"
            style='
                position: absolute;
                left: ${s.x-n/2}px;
                top: ${s.y-n/2}px;
                opacity: ${r.markerOptions.markerOpacity}
            '
        />'
        `),o}function d(r){let a=r.parentElement;for(;a!==null&&!a.classList.contains("form-row");)a=a.parentElement;return a}function k(r,a,i){var l;(l=d(a))==null||l.style.setProperty("background-color","#FFFFFF");for(let t of f(r,i)){const o=d(t);o!==null&&(o.style.display="none")}}function y(r,a,i){var l;(l=d(a))==null||l.style.setProperty("background-color","#E2DBC4");for(let t of f(r,i)){const o=d(t);o!==null&&(o.style.display="block")}}function f(r,a){let i=[];for(let n of a)n.groupName===r&&n.el!==null&&i.push(n.el);return i}function g(r){return new Promise((a,i)=>{const n=new FileReader;n.onload=()=>a(n.result),n.onerror=()=>i(n.error),n.readAsDataURL(r)})}document.addEventListener("DOMContentLoaded",()=>{(async()=>{var s;const r=document.querySelector("form");r&&r.addEventListener("submit",function(){console.log("Form is being submitted!")});const a=m("style_preview"),i=m("injected-style-id").innerHTML,n=m("injected-media-url").innerHTML,l=h(document,".field-style_preview");console.log(l);let t={drawStroke:!1,drawFill:!1,drawMarker:!1,strokeOptions:{color:"#FFFFFF",opacity:1,weight:1,lineJoin:"",lineCap:"ROUND",dashArray:"",dashOffset:"0"},fillOptions:{color:"#FFFFFF",opacity:1},markerOptions:{bgColor:"#FFFFFF",bgOpacity:1,data:null,markerOpacity:1,markerSize:22}};const o=[{groupName:"Toggle",el:document.querySelector("#id_draw_stroke"),update:e=>{e.checked?y("Stroke",e,o):k("Stroke",e,o),t.drawStroke=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_fill"),update:e=>{e.checked?y("Fill",e,o):k("Fill",e,o),t.drawFill=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_marker"),update:e=>{e.checked?y("Marker",e,o):k("Marker",e,o),t.drawMarker=e.checked},eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_color"),update:e=>t.strokeOptions.color=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_weight"),update:e=>t.strokeOptions.weight=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_opacity"),update:e=>t.strokeOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_cap"),update:e=>t.strokeOptions.lineCap=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_join"),update:e=>t.strokeOptions.lineJoin=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_array"),update:e=>t.strokeOptions.dashArray=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_offset"),update:e=>t.strokeOptions.dashOffset=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_color"),update:e=>t.fillOptions.color=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_opacity"),update:e=>t.fillOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_icon"),update:async e=>{let u=null;if(e.files&&(u=e.files[0]),u){const c=await g(u);t.markerOptions.data=c}else if(i!==""){const c=await N(i);if(c!==null){const O=n+c.markerIcon,w=await(await fetch(O)).blob(),_=await g(w);t.markerOptions.data=_}}else t.markerOptions.data=null},eventName:"change"},{groupName:"Marker",el:document.querySelector("#id_marker_icon_opacity"),update:e=>t.markerOptions.markerOpacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_color"),update:e=>t.markerOptions.bgColor=e.value,eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_opacity"),update:e=>t.markerOptions.bgOpacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_size"),update:e=>{t.markerOptions.markerSize=Number(e.value)},eventName:"input"}];for(let e of o){const u=async()=>{e.el!==null&&(await e.update(e.el),a.innerHTML=F(t))};(s=e==null?void 0:e.el)==null||s.addEventListener(e.eventName,u),await u()}})()});
