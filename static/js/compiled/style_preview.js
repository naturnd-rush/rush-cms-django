import{l as u,g as v}from"./utils/math.js";import{g as h}from"./graphql.js";import{e as d}from"./utils/timing.js";function N(t){let o="";for(let a of t)o+=a.x+","+a.y+" ";return o}function F(t){const l=[new u.Point(20,20),new u.Point(100,40),new u.Point(140,80),new u.Point(60,120),new u.Point(20,80)];let n=`
    <svg 
        width="200px"
        height="150px"
        xmlns="http://www.w3.org/2000/svg"
    >
    <polygon 
        points="${N(l)}"
    `;t.drawStroke&&(n+=`
            stroke="${t.strokeOptions.color}"
            stroke-width="${t.strokeOptions.weight}"
            stroke-opacity="${t.strokeOptions.opacity}"
            stroke-linecap="${t.strokeOptions.lineCap}"
            stroke-linejoin="${t.strokeOptions.lineJoin}"
            stroke-dasharray="${t.strokeOptions.dashArray}"
            stroke-dashoffset="${t.strokeOptions.dashOffset}"
        `),t.drawFill?n+=`
            fill="${t.fillOptions.color}"
            fill-opacity="${t.fillOptions.opacity}"
        `:n+='fill="none"',n+="/>";const e=v(l);return t.drawMarker&&(n+=`
        <circle 
            id="marker-centroid"
            r="16px"
            fill=${t.markerOptions.bgColor}
            opacity=${t.markerOptions.bgOpacity}
            cx=${e.x}
            cy=${e.y}
        />
        `),n+="</svg>",t.drawMarker&&t.markerOptions.data!==null&&(n+=`
        <img 
            id="marker-image"
            src="${t.markerOptions.data}"
            width="26"
            height="26"
            style='
                position: absolute;
                left: ${e.x-26/2}px;
                top: ${e.y-26/2}px;
                opacity: ${t.markerOptions.markerOpacity}
            '
        />'
        `),n}function p(t){let o=t.parentElement;for(;o!==null&&!o.classList.contains("form-row");)o=o.parentElement;return o}function m(t,o,a){var r;(r=p(o))==null||r.style.setProperty("background-color","#FFFFFF");for(let l of O(t,a)){const n=p(l);n!==null&&(n.style.display="none")}}function k(t,o,a){var r;(r=p(o))==null||r.style.setProperty("background-color","#E2DBC4");for(let l of O(t,a)){const n=p(l);n!==null&&(n.style.display="block")}}function O(t,o){let a=[];for(let i of o)i.groupName===t&&i.el!==null&&a.push(i.el);return a}function y(t){return new Promise((o,a)=>{const i=new FileReader;i.onload=()=>o(i.result),i.onerror=()=>a(i.error),i.readAsDataURL(t)})}document.addEventListener("DOMContentLoaded",()=>{(async()=>{var n;const t=document.querySelector("form");t&&t.addEventListener("submit",function(){console.log("Form is being submitted!")});const o=d("style_preview"),a=d("injected-style-id").innerHTML,i=d("injected-media-url").innerHTML;let r={drawStroke:!1,drawFill:!1,drawMarker:!1,strokeOptions:{color:"#FFFFFF",opacity:1,weight:1,lineJoin:"",lineCap:"ROUND",dashArray:"",dashOffset:"0"},fillOptions:{color:"#FFFFFF",opacity:1},markerOptions:{bgColor:"#FFFFFF",bgOpacity:1,data:null,markerOpacity:1}};const l=[{groupName:"Toggle",el:document.querySelector("#id_draw_stroke"),update:e=>{e.checked?k("Stroke",e,l):m("Stroke",e,l),r.drawStroke=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_fill"),update:e=>{e.checked?k("Fill",e,l):m("Fill",e,l),r.drawFill=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_marker"),update:e=>{e.checked?k("Marker",e,l):m("Marker",e,l),r.drawMarker=e.checked},eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_color"),update:e=>r.strokeOptions.color=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_weight"),update:e=>r.strokeOptions.weight=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_opacity"),update:e=>r.strokeOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_cap"),update:e=>r.strokeOptions.lineCap=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_join"),update:e=>r.strokeOptions.lineJoin=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_array"),update:e=>r.strokeOptions.dashArray=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_offset"),update:e=>r.strokeOptions.dashOffset=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_color"),update:e=>r.fillOptions.color=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_opacity"),update:e=>r.fillOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_icon"),update:async e=>{let s=null;if(e.files&&(s=e.files[0]),s){const c=await y(s);r.markerOptions.data=c}else if(a!==""){const c=await h(a);if(c!==null){const g=i+c.markerIcon,f=await fetch(g);console.log(f,g);const _=await f.blob(),w=await y(_);r.markerOptions.data=w}}else r.markerOptions.data=null},eventName:"change"},{groupName:"Marker",el:document.querySelector("#id_marker_icon_opacity"),update:e=>r.markerOptions.markerOpacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_color"),update:e=>r.markerOptions.bgColor=e.value,eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_opacity"),update:e=>r.markerOptions.bgOpacity=Number(e.value),eventName:"input"}];for(let e of l){const s=async()=>{e.el!==null&&(await e.update(e.el),o.innerHTML=F(r))};(n=e==null?void 0:e.el)==null||n.addEventListener(e.eventName,s),await s()}})()});
