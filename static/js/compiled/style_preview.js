import{l as p,g as _}from"./utils/math.js";import{g as w}from"./graphql.js";import{e as c,a as v}from"./utils/timing.js";function N(t){let o="";for(let n of t)o+=n.x+","+n.y+" ";return o}function h(t){const r=t.markerOptions.markerSize,a=Math.sqrt(Math.pow(r/2,2)+Math.pow(r/2,2)),l=[new p.Point(40,40),new p.Point(200,80),new p.Point(280,160),new p.Point(120,240),new p.Point(40,160)];let e=`
    <svg
        width="400px"
        height="400px"
        xmlns="http://www.w3.org/2000/svg"
    >
    <polygon 
        points="${N(l)}"
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
        `:e+='fill="none"',e+="/>";const i=_(l);return t.drawMarker&&(e+=`
        <circle 
            id="marker-centroid"
            r="${a}px"
            fill=${t.markerOptions.bgColor}
            opacity=${t.markerOptions.bgOpacity}
            cx=${i.x}
            cy=${i.y}
        />
        `),e+="</svg>",t.drawMarker&&t.markerOptions.data!==null&&(e+=`
        <img 
            id="marker-image"
            src="${t.markerOptions.data}"
            width="${r}"
            height="${r}"
            style='
                position: absolute;
                left: ${i.x-r/2}px;
                top: ${i.y-r/2}px;
                opacity: ${t.markerOptions.markerOpacity}
            '
        />'
        `),e}function u(t){let o=t.parentElement;for(;o!==null&&!o.classList.contains("form-row");)o=o.parentElement;return o}function d(t,o,n){var a;(a=u(o))==null||a.style.setProperty("background-color","#FFFFFF");for(let l of y(t,n)){const e=u(l);e!==null&&(e.style.display="none")}}function m(t,o,n){var a;(a=u(o))==null||a.style.setProperty("background-color","#E2DBC4");for(let l of y(t,n)){const e=u(l);e!==null&&(e.style.display="block")}}function y(t,o){let n=[];for(let r of o)r.groupName===t&&r.el!==null&&n.push(r.el);return n}function k(t){return new Promise((o,n)=>{const r=new FileReader;r.onload=()=>o(r.result),r.onerror=()=>n(r.error),r.readAsDataURL(t)})}document.addEventListener("DOMContentLoaded",()=>{(async()=>{var l;const t=c("style_preview"),o=c("injected-style-id").innerHTML,n=c("injected-media-url").innerHTML;v(document,".field-style_preview");let r={drawStroke:!1,drawFill:!1,drawMarker:!1,strokeOptions:{color:"#FFFFFF",opacity:1,weight:1,lineJoin:"",lineCap:"ROUND",dashArray:"",dashOffset:"0"},fillOptions:{color:"#FFFFFF",opacity:1},markerOptions:{bgColor:"#FFFFFF",bgOpacity:1,data:null,markerOpacity:1,markerSize:22}};const a=[{groupName:"Toggle",el:document.querySelector("#id_draw_stroke"),update:e=>{e.checked?m("Stroke",e,a):d("Stroke",e,a),r.drawStroke=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_fill"),update:e=>{e.checked?m("Fill",e,a):d("Fill",e,a),r.drawFill=e.checked},eventName:"input"},{groupName:"Toggle",el:document.querySelector("#id_draw_marker"),update:e=>{e.checked?m("Marker",e,a):d("Marker",e,a),r.drawMarker=e.checked},eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_color"),update:e=>r.strokeOptions.color=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_weight"),update:e=>r.strokeOptions.weight=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_opacity"),update:e=>r.strokeOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_cap"),update:e=>r.strokeOptions.lineCap=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_line_join"),update:e=>r.strokeOptions.lineJoin=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_array"),update:e=>r.strokeOptions.dashArray=e.value,eventName:"input"},{groupName:"Stroke",el:document.querySelector("#id_stroke_dash_offset"),update:e=>r.strokeOptions.dashOffset=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_color"),update:e=>r.fillOptions.color=e.value,eventName:"input"},{groupName:"Fill",el:document.querySelector("#id_fill_opacity"),update:e=>r.fillOptions.opacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_icon"),update:async e=>{let i=null;if(e.files&&(i=e.files[0]),i){const s=await k(i);r.markerOptions.data=s}else if(o!==""){const s=await w(o);if(s!==null){const g=n+s.markerIcon,f=await(await fetch(g)).blob(),O=await k(f);r.markerOptions.data=O}}else r.markerOptions.data=null},eventName:"change"},{groupName:"Marker",el:document.querySelector("#id_marker_icon_opacity"),update:e=>r.markerOptions.markerOpacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_color"),update:e=>r.markerOptions.bgColor=e.value,eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_background_opacity"),update:e=>r.markerOptions.bgOpacity=Number(e.value),eventName:"input"},{groupName:"Marker",el:document.querySelector("#id_marker_size"),update:e=>{r.markerOptions.markerSize=Number(e.value)},eventName:"input"}];for(let e of a){const i=async()=>{e.el!==null&&(await e.update(e.el),t.innerHTML=h(r))};(l=e==null?void 0:e.el)==null||l.addEventListener(e.eventName,i),await i()}})()});
