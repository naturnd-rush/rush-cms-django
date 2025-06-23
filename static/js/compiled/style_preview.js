import{g as h}from"./graphql.js";import{e as p}from"./utils.js";function w(t){let o=0,n=0;for(let i of t)o+=i.x,n+=i.y;return{x:o/=t.length,y:n/=t.length}}function v(t){let o="";for(let n of t)o+=n.x+","+n.y+" ";return o}function N(t){const l=[{x:20,y:20},{x:100,y:40},{x:140,y:80},{x:60,y:120},{x:20,y:80}];let a=`
    <svg 
        width="200px"
        height="150px"
        xmlns="http://www.w3.org/2000/svg"
    >
    <polygon 
        points="${v(l)}"
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
        `:a+='fill="none"',a+="/>";const e=w(l);return t.drawMarker&&t.markerOptions.data!==null&&(a+=`
        <circle 
            id="marker-centroid"
            r="16px"
            fill=${t.markerOptions.bgColor}
            opacity=${t.markerOptions.opacity}
            cx=${e.x}
            cy=${e.y}
        />
        `),a+="</svg>",t.drawMarker&&t.markerOptions.data!==null&&(a+=`
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
        `),a}function u(t){let o=t.parentElement;for(;o!==null&&!o.classList.contains("form-row");)o=o.parentElement;return o}function d(t,o,n){var r;(r=u(o))==null||r.style.setProperty("background-color","#FFFFFF");for(let l of f(t,n)){const a=u(l);a!==null&&(a.style.display="none")}}function m(t,o,n){var r;(r=u(o))==null||r.style.setProperty("background-color","#E2DBC4");for(let l of f(t,n)){const a=u(l);a!==null&&(a.style.display="block")}}function f(t,o){let n=[];for(let i of o)i.groupName===t&&i.el!==null&&n.push(i.el);return n}function g(t){return new Promise((o,n)=>{const i=new FileReader;i.onload=()=>o(i.result),i.onerror=()=>n(i.error),i.readAsDataURL(t)})}document.addEventListener("DOMContentLoaded",()=>{(async()=>{var a;const t=document.querySelector("form");t&&t.addEventListener("submit",function(){console.log("Form is being submitted!")});const o=p("style_preview"),n=p("injected-style-id").innerHTML,i=p("injected-media-url").innerHTML;let r={drawStroke:!1,drawFill:!1,drawMarker:!1,strokeOptions:{color:"#FFFFFF",opacity:1,weight:1,lineJoin:"",lineCap:"ROUND",dashArray:"",dashOffset:"0"},fillOptions:{color:"#FFFFFF",opacity:1},markerOptions:{bgColor:"#FFFFFF",opacity:1,data:null}};const l=[{groupName:"Toggle",el:document.querySelector("#id_draw_stroke"),update:e=>{e.checked?m("Stroke",e,l):d("Stroke",e,l),r.drawStroke=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_fill"),update:e=>{e.checked?m("Fill",e,l):d("Fill",e,l),r.drawFill=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_marker"),update:e=>{e.checked?m("Marker",e,l):d("Marker",e,l),r.drawMarker=e.checked},eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_color"),update:e=>r.strokeOptions.color=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_weight"),update:e=>r.strokeOptions.weight=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_opacity"),update:e=>r.strokeOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_cap"),update:e=>r.strokeOptions.lineCap=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_join"),update:e=>r.strokeOptions.lineJoin=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_array"),update:e=>r.strokeOptions.dashArray=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_offset"),update:e=>r.strokeOptions.dashOffset=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_color"),update:e=>r.fillOptions.color=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_opacity"),update:e=>r.fillOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_icon"),update:async e=>{let s=null;if(e.files&&(s=e.files[0]),s){const c=await g(s);r.markerOptions.data=c}else{const c=await h(n);if(c!==null){const k=i+c.markerIcon,y=await fetch(k);console.log(y,k);const O=await y.blob(),_=await g(O);r.markerOptions.data=_}}},eventName:"change"},{groupName:"Marker",el:document.querySelector("#id_marker_icon_opacity"),update:e=>r.markerOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_color"),update:e=>r.markerOptions.bgColor=e.value,eventName:"input"}];for(let e of l){const s=async()=>{e.el!==null&&(await e.update(e.el),o.innerHTML=N(r))};(a=e==null?void 0:e.el)==null||a.addEventListener(e.eventName,s),await s()}})()});
