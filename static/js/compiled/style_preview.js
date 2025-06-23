import{g}from"./graphql.js";function _(t){const o=[{x:20,y:20},{x:100,y:40},{x:140,y:80},{x:60,y:120},{x:20,y:80}];let n="";for(let e of o)n+=e.x+","+e.y+" ";let r=`
    <svg 
        width="200" 
        height="150" 
        xmlns="http://www.w3.org/2000/svg"
    >
    <polygon 
        points="${n}"
    `;if(t.drawStroke&&(r+=`
            stroke="${t.strokeOptions.color}"
            stroke-width="${t.strokeOptions.weight}"
            stroke-opacity="${t.strokeOptions.opacity}"
            stroke-linecap="${t.strokeOptions.lineCap}"
            stroke-linejoin="${t.strokeOptions.lineJoin}"
            stroke-dasharray="${t.strokeOptions.dashArray}"
            stroke-dashoffset="${t.strokeOptions.dashOffset}"
        `),t.drawFill?r+=`
            fill="${t.fillOptions.color}"
            fill-opacity="${t.fillOptions.opacity}"
        `:r+='fill="none"',r+="/>",t.drawMarker&&t.markerOptions.data!==null){let a=0,i=0;for(let p of o)a+=p.x,i+=p.y;const l={x:a/=o.length,y:i/=o.length};r+=`
        <circle 
            id="marker-centroid"
            r="20px"
            fill=${t.markerOptions.bgColor}
            opacity=${t.markerOptions.opacity}
            cx=${l.x}
            cy=${l.y}
        />
        `}return r+="</svg>",console.log("Marker icon data: ",t.markerOptions.data),t.drawMarker&&t.markerOptions.data!==null&&(r+=`
        <img 
            id="marker-image"
            src="${t.markerOptions.data}"
            x="0" 
            y="0" 
            width="20" 
            height="20"
        />
        `),r}function s(t){let o=t.parentElement;for(;o!==null&&!o.classList.contains("form-row");)o=o.parentElement;return o}function u(t,o,n){var e;(e=s(o))==null||e.style.setProperty("background-color","#FFFFFF");for(let a of m(t,n)){const i=s(a);i!==null&&(i.style.display="none")}}function c(t,o,n){var e;(e=s(o))==null||e.style.setProperty("background-color","#E2DBC4");for(let a of m(t,n)){const i=s(a);i!==null&&(i.style.display="block")}}function m(t,o){let n=[];for(let r of o)r.groupName===t&&r.el!==null&&n.push(r.el);return n}function d(t){return new Promise((o,n)=>{const r=new FileReader;r.onload=()=>o(r.result),r.onerror=()=>n(r.error),r.readAsDataURL(t)})}document.addEventListener("DOMContentLoaded",()=>{(async()=>{var r;const t=document.getElementById("style_preview");if(t===null)throw new Error("Expected DOM element with id 'style_preview' to exist!");let o={drawStroke:!1,drawFill:!1,drawMarker:!1,strokeOptions:{color:"#FFFFFF",opacity:1,weight:1,lineJoin:"",lineCap:"ROUND",dashArray:"",dashOffset:"0"},fillOptions:{color:"#FFFFFF",opacity:1},markerOptions:{bgColor:"#FFFFFF",opacity:1,data:null}};const n=[{groupName:"Toggle",el:document.querySelector("#id_draw_stroke"),update:e=>{e.checked?c("Stroke",e,n):u("Stroke",e,n),o.drawStroke=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_fill"),update:e=>{e.checked?c("Fill",e,n):u("Fill",e,n),o.drawFill=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_marker"),update:e=>{e.checked?c("Marker",e,n):u("Marker",e,n),o.drawMarker=e.checked},eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_color"),update:e=>o.strokeOptions.color=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_weight"),update:e=>o.strokeOptions.weight=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_opacity"),update:e=>o.strokeOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_cap"),update:e=>o.strokeOptions.lineCap=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_join"),update:e=>o.strokeOptions.lineJoin=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_array"),update:e=>o.strokeOptions.dashArray=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_offset"),update:e=>o.strokeOptions.dashOffset=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_color"),update:e=>o.fillOptions.color=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_opacity"),update:e=>o.fillOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#live_image_input_marker_icon"),update:async e=>{var i;let a=null;if(e.files&&(a=e.files[0]),a){const l=await d(a);o.markerOptions.data=l}else{const l=(i=document.getElementById("injected-style-id"))==null?void 0:i.innerHTML;if(l!==void 0){const p=await g(l);if(p!==null){const k=p.markerIcon,y=await(await fetch(k)).blob(),f=await d(y);o.markerOptions.data=f}}}},eventName:"change"},{groupName:"Marker",el:document.querySelector("#id_marker_icon_opacity"),update:e=>o.markerOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_color"),update:e=>o.markerOptions.bgColor=e.value,eventName:"input"}];for(let e of n){const a=async()=>{e.el!==null&&(await e.update(e.el),t.innerHTML=_(o))};(r=e==null?void 0:e.el)==null||r.addEventListener(e.eventName,a),await a()}})()});
