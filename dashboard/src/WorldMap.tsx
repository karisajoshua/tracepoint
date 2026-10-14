import type {CSSProperties} from 'react';
/** Decorative world basemap. Markers are synthetic in preview mode only. */
export default function WorldMap({demo}:{demo:boolean}){
 const land=["M55 88 73 60 113 46 141 52 161 72 151 91 131 96 119 119 95 133 83 117 62 112Z","M124 143 150 151 165 180 158 207 143 243 129 270 117 251 115 219 100 193 107 165Z","M170 58 200 46 229 54 248 70 242 95 218 101 201 88 182 93 166 77Z","M223 104 256 99 275 118 269 155 258 186 237 207 221 180 217 149 206 122Z","M260 61 297 49 326 59 348 49 395 59 431 80 445 104 423 124 396 120 378 139 359 128 344 109 316 119 292 99 271 102Z","M356 148 374 145 393 165 388 191 372 201 360 185Z","M395 204 434 194 454 206 467 229 446 244 412 240 394 223Z","M83 29 108 21 132 31 120 43 94 43Z","M281 218 289 223 285 238 276 235Z"];
 const dots:[number,number,number][]=[[105,95,5],[143,175,4],[245,116,4],[269,149,5],[345,91,4],[407,107,4],[434,215,4]];
 return <div className="world-map" aria-label={demo?'Illustrative world map with synthetic example markers':'World map without geolocated events'}>
 <svg viewBox="0 0 520 290" role="img" aria-label="World basemap" preserveAspectRatio="xMidYMid meet">
 <defs><radialGradient id="ocean"><stop offset="0" stopColor="#17364c"/><stop offset="1" stopColor="#0c1c2b"/></radialGradient></defs>
 <rect width="520" height="290" fill="url(#ocean)"/>
 {Array.from({length:11},(_,i)=><line key={'v'+i} x1={i*52} y1="0" x2={i*52} y2="290" stroke="#2a4b60" strokeWidth=".5" opacity=".55"/>)}
 {Array.from({length:7},(_,i)=><line key={'h'+i} x1="0" y1={i*48} x2="520" y2={i*48} stroke="#2a4b60" strokeWidth=".5" opacity=".55"/>)}
 {land.map((d,i)=><path key={i} d={d} fill="#224258" stroke="#426479" strokeWidth="1.2" opacity=".9"/>)}
 {demo&&<g>{dots.map(([x,y,r],i)=><g key={i}><circle cx={x} cy={y} r={r*3} fill="#f16a5e" opacity=".11"/><circle cx={x} cy={y} r={r} fill="#f16a5e" stroke="#ffc2a1" strokeWidth=".8"/></g>)}<path d="M105 95 Q180 20 245 116 M245 116 Q320 40 407 107 M269 149 Q340 110 434 215" stroke="#e7a45a" strokeDasharray="4 5" strokeWidth="1.4" fill="none" opacity=".7"/></g>}
 </svg>
 <div className="map-status" style={{'--map-status-color':demo?'#e9ad64':'#71a6b9'} as CSSProperties}>{demo?'● DEMO LOCATIONS':'○ GEOLOCATION NOT CONFIGURED'}</div>
 </div>;
}
