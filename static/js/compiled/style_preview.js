import{e as p,l as c,g as h}from"./utils.js";import{g as v}from"./graphql.js";function N(t){let r="";for(let i of t)r+=i.x+","+i.y+" ";return r}function F(t){const l=[new c.Point(20,20),new c.Point(100,40),new c.Point(140,80),new c.Point(60,120),new c.Point(20,80)];let n=`
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
        `:n+='fill="none"',n+="/>";const e=h(l);return t.drawMarker&&(n+=`
        <circle 
            id="marker-centroid"
            r="16px"
            fill=${t.markerOptions.bgColor}
            opacity=${t.markerOptions.opacity}
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
                opacity: ${t.markerOptions.opacity}
            '
        />'
        `),n}function d(t){let r=t.parentElement;for(;r!==null&&!r.classList.contains("form-row");)r=r.parentElement;return r}function m(t,r,i){var o;(o=d(r))==null||o.style.setProperty("background-color","#FFFFFF");for(let l of w(t,i)){const n=d(l);n!==null&&(n.style.display="none")}}function k(t,r,i){var o;(o=d(r))==null||o.style.setProperty("background-color","#E2DBC4");for(let l of w(t,i)){const n=d(l);n!==null&&(n.style.display="block")}}function w(t,r){let i=[];for(let a of r)a.groupName===t&&a.el!==null&&i.push(a.el);return i}function y(t){return new Promise((r,i)=>{const a=new FileReader;a.onload=()=>r(a.result),a.onerror=()=>i(a.error),a.readAsDataURL(t)})}document.addEventListener("DOMContentLoaded",()=>{(async()=>{var n;const t=document.querySelector("form");t&&t.addEventListener("submit",function(){console.log("Form is being submitted!")});const r=p("style_preview"),i=p("injected-style-id").innerHTML,a=p("injected-media-url").innerHTML;let o={drawStroke:!1,drawFill:!1,drawMarker:!1,strokeOptions:{color:"#FFFFFF",opacity:1,weight:1,lineJoin:"",lineCap:"ROUND",dashArray:"",dashOffset:"0"},fillOptions:{color:"#FFFFFF",opacity:1},markerOptions:{bgColor:"#FFFFFF",opacity:1,data:null}};const l=[{groupName:"Toggle",el:document.querySelector("#id_draw_stroke"),update:e=>{e.checked?k("Stroke",e,l):m("Stroke",e,l),o.drawStroke=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_fill"),update:e=>{e.checked?k("Fill",e,l):m("Fill",e,l),o.drawFill=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_marker"),update:e=>{e.checked?k("Marker",e,l):m("Marker",e,l),o.drawMarker=e.checked},eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_color"),update:e=>o.strokeOptions.color=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_weight"),update:e=>o.strokeOptions.weight=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_opacity"),update:e=>o.strokeOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_cap"),update:e=>o.strokeOptions.lineCap=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_join"),update:e=>o.strokeOptions.lineJoin=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_array"),update:e=>o.strokeOptions.dashArray=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_offset"),update:e=>o.strokeOptions.dashOffset=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_color"),update:e=>o.fillOptions.color=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_opacity"),update:e=>o.fillOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_icon"),update:async e=>{let s=null;if(console.log(e.files),e.files&&(s=e.files[0]),s){const u=await y(s);o.markerOptions.data=u}else if(console.log("Getting old marker icon data from injected style id: ",i),i!==""){const u=await v(i);if(u!==null){const g=a+u.markerIcon,f=await fetch(g);console.log(f,g);const O=await f.blob(),_=await y(O);o.markerOptions.data=_}}else o.markerOptions.data=null},eventName:"change"},{groupName:"Marker",el:document.querySelector("#id_marker_icon_opacity"),update:e=>o.markerOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_color"),update:e=>o.markerOptions.bgColor=e.value,eventName:"input"}];for(let e of l){const s=async()=>{e.el!==null&&(await e.update(e.el),r.innerHTML=F(o))};(n=e==null?void 0:e.el)==null||n.addEventListener(e.eventName,s),await s()}})()});
