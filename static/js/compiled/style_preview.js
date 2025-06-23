import{g as _}from"./graphql.js";function w(t){let o=0,n=0;for(let r of t)o+=r.x,n+=r.y;return{x:o/=t.length,y:n/=t.length}}function h(t){let o="";for(let n of t)o+=n.x+","+n.y+" ";return o}function v(t){const i=[{x:20,y:20},{x:100,y:40},{x:140,y:80},{x:60,y:120},{x:20,y:80}];let a=`
    <svg 
        width="200px"
        height="150px"
        xmlns="http://www.w3.org/2000/svg"
    >
    <polygon 
        points="${h(i)}"
    `;t.drawStroke&&(a+=`
            stroke="${t.strokeOptions.color}"
            stroke-width="${t.strokeOptions.weight}"
            stroke-opacity="${t.strokeOptions.opacity}"
            stroke-linecap="${t.strokeOptions.lineCap}"
            stroke-linejoin="${t.strokeOptions.lineJoin}"
            stroke-dasharray="${t.strokeOptions.dashArray}"
            stroke-dashoffset="${t.strokeOptions.dashOffset}"
        `),t.drawFill?a+=`
            fill="${t.fillOptions.color}"
            fill-opacity="${t.fillOptions.opacity}"
        `:a+='fill="none"',a+="/>";const e=w(i);return t.drawMarker&&t.markerOptions.data!==null&&(a+=`
        <circle 
            id="marker-centroid"
            r="20px"
            fill=${t.markerOptions.bgColor}
            opacity=${t.markerOptions.opacity}
            cx=${e.x}
            cy=${e.y}
        />
        `),a+="</svg>",t.drawMarker&&t.markerOptions.data!==null&&(a+=`
        <img 
            id="marker-image"
            src="${t.markerOptions.data}"
            width="20"
            height="20"
            style='
                position: absolute;
                left: ${e.x-20/2}px;
                top: ${e.y-20/2}px;
                opacity: ${t.markerOptions.opacity}
            '
        />'
        `),a}function u(t){let o=t.parentElement;for(;o!==null&&!o.classList.contains("form-row");)o=o.parentElement;return o}function c(t,o,n){var i;(i=u(o))==null||i.style.setProperty("background-color","#FFFFFF");for(let a of f(t,n)){const e=u(a);e!==null&&(e.style.display="none")}}function p(t,o,n){var i;(i=u(o))==null||i.style.setProperty("background-color","#E2DBC4");for(let a of f(t,n)){const e=u(a);e!==null&&(e.style.display="block")}}function f(t,o){let n=[];for(let r of o)r.groupName===t&&r.el!==null&&n.push(r.el);return n}function y(t){return new Promise((o,n)=>{const r=new FileReader;r.onload=()=>o(r.result),r.onerror=()=>n(r.error),r.readAsDataURL(t)})}function d(t){const o=document.getElementById(t);if(o===null)throw new Error("Expected DOM element with id '"+t+"' to exist!");return o}document.addEventListener("DOMContentLoaded",()=>{(async()=>{var a;const t=d("style_preview"),o=d("injected-style-id").innerHTML,n=d("injected-media-url").innerHTML;let r={drawStroke:!1,drawFill:!1,drawMarker:!1,strokeOptions:{color:"#FFFFFF",opacity:1,weight:1,lineJoin:"",lineCap:"ROUND",dashArray:"",dashOffset:"0"},fillOptions:{color:"#FFFFFF",opacity:1},markerOptions:{bgColor:"#FFFFFF",opacity:1,data:null}};const i=[{groupName:"Toggle",el:document.querySelector("#id_draw_stroke"),update:e=>{e.checked?p("Stroke",e,i):c("Stroke",e,i),r.drawStroke=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_fill"),update:e=>{e.checked?p("Fill",e,i):c("Fill",e,i),r.drawFill=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_marker"),update:e=>{e.checked?p("Marker",e,i):c("Marker",e,i),r.drawMarker=e.checked},eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_color"),update:e=>r.strokeOptions.color=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_weight"),update:e=>r.strokeOptions.weight=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_opacity"),update:e=>r.strokeOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_cap"),update:e=>r.strokeOptions.lineCap=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_join"),update:e=>r.strokeOptions.lineJoin=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_array"),update:e=>r.strokeOptions.dashArray=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_offset"),update:e=>r.strokeOptions.dashOffset=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_color"),update:e=>r.fillOptions.color=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_opacity"),update:e=>r.fillOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#live_image_input_marker_icon"),update:async e=>{let l=null;if(e.files&&(l=e.files[0]),l){const s=await y(l);r.markerOptions.data=s}else{const s=await _(o);if(s!==null){const m=n+s.markerIcon,k=await fetch(m);console.log(k,m);const g=await k.blob(),O=await y(g);r.markerOptions.data=O}}},eventName:"change"},{groupName:"Marker",el:document.querySelector("#id_marker_icon_opacity"),update:e=>r.markerOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_color"),update:e=>r.markerOptions.bgColor=e.value,eventName:"input"}];for(let e of i){const l=async()=>{e.el!==null&&(await e.update(e.el),t.innerHTML=v(r))};(a=e==null?void 0:e.el)==null||a.addEventListener(e.eventName,l),await l()}})()});
