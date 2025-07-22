import{l as c,g as h}from"./utils/math.js";import{g as v}from"./graphql.js";import{e as d}from"./utils/timing.js";function N(o){let r="";for(let i of o)r+=i.x+","+i.y+" ";return r}function F(o){const l=[new c.Point(20,20),new c.Point(100,40),new c.Point(140,80),new c.Point(60,120),new c.Point(20,80)];let n=`
    <svg 
        width="200px"
        height="150px"
        xmlns="http://www.w3.org/2000/svg"
    >
    <polygon 
        points="${N(l)}"
    `;o.drawStroke&&(n+=`
            stroke="${o.strokeOptions.color}"
            stroke-width="${o.strokeOptions.weight}"
            stroke-opacity="${o.strokeOptions.opacity}"
            stroke-linecap="${o.strokeOptions.lineCap}"
            stroke-linejoin="${o.strokeOptions.lineJoin}"
            stroke-dasharray="${o.strokeOptions.dashArray}"
            stroke-dashoffset="${o.strokeOptions.dashOffset}"
        `),o.drawFill?n+=`
            fill="${o.fillOptions.color}"
            fill-opacity="${o.fillOptions.opacity}"
        `:n+='fill="none"',n+="/>";const e=h(l);return o.drawMarker&&(n+=`
        <circle 
            id="marker-centroid"
            r="16px"
            fill=${o.markerOptions.bgColor}
            opacity=${o.markerOptions.opacity}
            cx=${e.x}
            cy=${e.y}
        />
        `),n+="</svg>",o.drawMarker&&o.markerOptions.data!==null&&(n+=`
        <img 
            id="marker-image"
            src="${o.markerOptions.data}"
            width="26"
            height="26"
            style='
                position: absolute;
                left: ${e.x-26/2}px;
                top: ${e.y-26/2}px;
                opacity: ${o.markerOptions.opacity}
            '
        />'
        `),n}function p(o){let r=o.parentElement;for(;r!==null&&!r.classList.contains("form-row");)r=r.parentElement;return r}function m(o,r,i){var t;(t=p(r))==null||t.style.setProperty("background-color","#FFFFFF");for(let l of w(o,i)){const n=p(l);n!==null&&(n.style.display="none")}}function k(o,r,i){var t;(t=p(r))==null||t.style.setProperty("background-color","#E2DBC4");for(let l of w(o,i)){const n=p(l);n!==null&&(n.style.display="block")}}function w(o,r){let i=[];for(let a of r)a.groupName===o&&a.el!==null&&i.push(a.el);return i}function y(o){return new Promise((r,i)=>{const a=new FileReader;a.onload=()=>r(a.result),a.onerror=()=>i(a.error),a.readAsDataURL(o)})}document.addEventListener("DOMContentLoaded",()=>{(async()=>{var n;const o=document.querySelector("form");o&&o.addEventListener("submit",function(){console.log("Form is being submitted!")});const r=d("style_preview"),i=d("injected-style-id").innerHTML,a=d("injected-media-url").innerHTML;let t={drawStroke:!1,drawFill:!1,drawMarker:!1,strokeOptions:{color:"#FFFFFF",opacity:1,weight:1,lineJoin:"",lineCap:"ROUND",dashArray:"",dashOffset:"0"},fillOptions:{color:"#FFFFFF",opacity:1},markerOptions:{bgColor:"#FFFFFF",opacity:1,data:null}};const l=[{groupName:"Toggle",el:document.querySelector("#id_draw_stroke"),update:e=>{e.checked?k("Stroke",e,l):m("Stroke",e,l),t.drawStroke=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_fill"),update:e=>{e.checked?k("Fill",e,l):m("Fill",e,l),t.drawFill=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_marker"),update:e=>{e.checked?k("Marker",e,l):m("Marker",e,l),t.drawMarker=e.checked},eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_color"),update:e=>t.strokeOptions.color=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_weight"),update:e=>t.strokeOptions.weight=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_opacity"),update:e=>t.strokeOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_cap"),update:e=>t.strokeOptions.lineCap=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_join"),update:e=>t.strokeOptions.lineJoin=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_array"),update:e=>t.strokeOptions.dashArray=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_offset"),update:e=>t.strokeOptions.dashOffset=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_color"),update:e=>t.fillOptions.color=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_opacity"),update:e=>t.fillOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_icon"),update:async e=>{let s=null;if(console.log(e.files),e.files&&(s=e.files[0]),s){const u=await y(s);t.markerOptions.data=u}else if(console.log("Getting old marker icon data from injected style id: ",i),i!==""){const u=await v(i);if(u!==null){const g=a+u.markerIcon,f=await fetch(g);console.log(f,g);const O=await f.blob(),_=await y(O);t.markerOptions.data=_}}else t.markerOptions.data=null},eventName:"change"},{groupName:"Marker",el:document.querySelector("#id_marker_icon_opacity"),update:e=>t.markerOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_color"),update:e=>t.markerOptions.bgColor=e.value,eventName:"input"}];for(let e of l){const s=async()=>{e.el!==null&&(await e.update(e.el),r.innerHTML=F(t))};(n=e==null?void 0:e.el)==null||n.addEventListener(e.eventName,s),await s()}})()});
