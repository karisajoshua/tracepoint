import {useEffect,useRef,useState} from 'react';

/** 3D map powered by MapLibre GL JS and OpenFreeMap vector tiles.
 * Real buildings are extruded where OpenStreetMap height information is available.
 * No simulated attack positions are displayed in live mode.
 */
type GLMap={
 on:(event:string,callback:()=>void)=>void;
 addLayer:(layer:Record<string,unknown>)=>void;
 getSource:(id:string)=>unknown;
 getLayer:(id:string)=>unknown;
 flyTo:(opts:Record<string,unknown>)=>void;
 fitBounds:(bounds:[[number,number],[number,number]],opts:Record<string,unknown>)=>void;
 resize:()=>void;remove:()=>void;
};
type MapLibre={Map:new(opts:Record<string,unknown>)=>GLMap;NavigationControl:new(opts?:Record<string,unknown>)=>unknown;Marker:new(opts?:Record<string,unknown>)=>{setLngLat:(coords:[number,number])=>{setPopup:(popup:unknown)=>{addTo:(map:GLMap)=>unknown}}};Popup:new(opts?:Record<string,unknown>)=>{setText:(text:string)=>unknown}};
declare global{interface Window{maplibregl?:MapLibre}}
const JS='https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js';
const CSS='https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css';
let loader:Promise<MapLibre>|undefined;
function loadMapLibre():Promise<MapLibre>{
 if(window.maplibregl)return Promise.resolve(window.maplibregl);
 if(loader)return loader;
 loader=new Promise<MapLibre>((resolve,reject)=>{
  if(!document.querySelector('link[data-tracepoint-maplibre]')){
   const link=document.createElement('link');link.rel='stylesheet';link.href=CSS;link.dataset.tracepointMaplibre='1';document.head.appendChild(link);
  }
  const script=document.createElement('script');script.src=JS;script.async=true;
  script.onload=()=>window.maplibregl?resolve(window.maplibregl):reject(new Error('3D map library failed to initialize'));
  script.onerror=()=>reject(new Error('3D map library could not be downloaded'));
  document.head.appendChild(script);
 }).catch(err=>{loader=undefined;throw err;});
 return loader;
}
const samples:[number,number,string][]=[[-74.01,40.71,'New York'],[-0.13,51.51,'London'],[36.82,-1.29,'Nairobi'],[103.82,1.35,'Singapore'],[139.69,35.68,'Tokyo'],[151.21,-33.87,'Sydney']];
type Place={display_name:string;lat:string;lon:string;boundingbox:string[]};
export default function Map3D({demo}:{demo:boolean}){
 const container=useRef<HTMLDivElement>(null);
 const map=useRef<GLMap|null>(null);
 const [error,setError]=useState('');
 const [query,setQuery]=useState('');
 const [results,setResults]=useState<Place[]>([]);
 const [searching,setSearching]=useState(false);
 const [place,setPlace]=useState('');
 useEffect(()=>{
 let cancelled=false;let active:GLMap|null=null;
 loadMapLibre().then(gl=>{
  if(cancelled||!container.current)return;
  active=new gl.Map({container:container.current,style:'https://tiles.openfreemap.org/styles/liberty',center:[8,18],zoom:1.6,pitch:55,bearing:-15,antialias:true,attributionControl:true,maxZoom:19});
  map.current=active;
  active.on('load',()=>{
   if(cancelled||!active)return;
   try{
    // OpenFreeMap Liberty exposes OpenMapTiles building geometry.
    if(active.getSource('openmaptiles')&&!active.getLayer('tracepoint-3d-buildings')){
     active.addLayer({id:'tracepoint-3d-buildings',source:'openmaptiles','source-layer':'building',type:'fill-extrusion',minzoom:14,paint:{'fill-extrusion-color':'#7395a7','fill-extrusion-height':['coalesce',['get','render_height'],['get','height'],0],'fill-extrusion-base':['coalesce',['get','render_min_height'],0],'fill-extrusion-opacity':0.72}});
    }
   }catch{/* Base map remains available when the provider has no building layer. */}
   if(demo)samples.forEach(([lon,lat,city])=>{
    const dot=document.createElement('span');dot.className='map3d-demo-dot';dot.title='Synthetic demonstration location: '+city;
    new gl.Marker({element:dot}).setLngLat([lon,lat]).setPopup(new gl.Popup().setText('Sample location: '+city+' (not a live threat)')).addTo(active!);
   });
   active.resize();
  });
 }).catch(e=>{if(!cancelled)setError(e instanceof Error?e.message:'3D map unavailable');});
 return()=>{cancelled=true;active?.remove();map.current=null;};
 },[demo]);
 async function search(e:React.FormEvent<HTMLFormElement>){
  e.preventDefault();if(query.trim().length<2)return;
  setSearching(true);setResults([]);setError('');
  try{
   const response=await fetch('https://nominatim.openstreetmap.org/search?format=jsonv2&limit=5&q='+encodeURIComponent(query.trim()),{headers:{Accept:'application/json'}});
   if(!response.ok)throw new Error('Location search unavailable');
   const places=await response.json() as Place[];setResults(places);
   if(!places.length)setError('No matching locations found');
  }catch(e){setError(e instanceof Error?e.message:'Location search failed');}
  finally{setSearching(false);}
 }
 function navigate(p:Place){
  const b=p.boundingbox.map(Number);
  if(b.length===4&&b.every(Number.isFinite))map.current?.fitBounds([[b[2],b[0]],[b[3],b[1]]],{padding:45,maxZoom:17,pitch:55});
  else map.current?.flyTo({center:[Number(p.lon),Number(p.lat)],zoom:15,pitch:55,bearing:-15});
  setPlace(p.display_name);setResults([]);
 }
 return <div className="world-map real-world-map map3d" aria-label="Interactive three-dimensional geographic map">
  <div className="map3d-canvas" ref={container}/>
  <div className="map-search"><form onSubmit={search}><input aria-label="Search 3D map location" placeholder="Country, city, street…" value={query} onChange={e=>setQuery(e.target.value)}/><button type="submit" disabled={searching}>{searching?'…':'Search'}</button></form>
  {results.length>0&&<div className="map-results">{results.map((p,i)=><button key={i} onClick={()=>navigate(p)}>{p.display_name}</button>)}</div>}</div>
  <div className="map-tools"><button onClick={()=>{map.current?.flyTo({center:[8,18],zoom:1.6,pitch:55,bearing:-15});setPlace('');}}>World</button><button onClick={()=>map.current?.flyTo({pitch:60,bearing:0})}>Tilt 60°</button><button onClick={()=>map.current?.flyTo({pitch:0,bearing:0})}>Top view</button></div>
  {place&&<div className="map-selected" title={place}>Viewing: {place}</div>}
  {error&&<div className="map-error" role="status">{error}</div>}
  <div className="map-status">{demo?'● 3D DEMO — SAMPLE MARKERS':'○ 3D MAP — NO LIVE GEOLOCATED EVENTS'}</div>
 </div>;
}
