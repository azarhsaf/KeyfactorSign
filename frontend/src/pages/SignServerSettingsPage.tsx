import { useEffect, useState } from 'react'; import { api } from '../api/client';
export default function SignServerSettingsPage(){const [cfg,setCfg]=useState<any>({}); const [health,setHealth]=useState<any>(null);
useEffect(()=>{api.get('/admin/settings/signserver').then(r=>setCfg(r.data))},[])
return <div className='space-y-4'><h2 className='text-2xl font-semibold'>SignServer Settings</h2><div className='bg-white border rounded p-4 text-sm space-y-2'>{Object.entries(cfg).map(([k,v])=><div key={k}><b>{k}</b>: {String(v)}</div>)}<button onClick={async()=>setHealth((await api.get('/admin/signserver/health')).data)} className='bg-slate-900 text-white px-3 py-2 rounded'>Test Connection</button>{health&&<pre className='bg-slate-50 p-2 mt-2'>{JSON.stringify(health,null,2)}</pre>}</div></div>}
