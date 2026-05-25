import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function BrandingSettingsPage(){
  const [cfg,setCfg]=useState<any>({});
  const [msg,setMsg]=useState('');
  useEffect(()=>{api.get('/admin/branding').then(r=>setCfg(r.data))},[])
  const save=async()=>{const d=new FormData(); Object.entries(cfg).forEach(([k,v])=>d.append(k,String(v??''))); await api.post('/admin/branding',d); setMsg('Saved')}
  const upload=async(type:'logo'|'favicon', f?:File)=>{if(!f)return; const d=new FormData(); d.append('file',f); await api.post(`/admin/branding/${type}`,d); const r=await api.get('/admin/branding'); setCfg(r.data); setMsg(`${type} uploaded`)}
  return <div className='space-y-4'>
    <h2 className='text-2xl font-semibold'>Branding</h2>
    <div className='bg-white border rounded p-4 grid md:grid-cols-2 gap-3'>
      <input className='border p-2 rounded' value={cfg.brand_product_name||''} onChange={e=>setCfg({...cfg,brand_product_name:e.target.value})} placeholder='Product name'/>
      <input className='border p-2 rounded' value={cfg.brand_company_name||''} onChange={e=>setCfg({...cfg,brand_company_name:e.target.value})} placeholder='Company name'/>
      <input className='border p-2 rounded' value={cfg.brand_primary_color||''} onChange={e=>setCfg({...cfg,brand_primary_color:e.target.value})} placeholder='Primary color'/>
      <input className='border p-2 rounded' value={cfg.brand_secondary_color||''} onChange={e=>setCfg({...cfg,brand_secondary_color:e.target.value})} placeholder='Secondary color'/>
      <input className='border p-2 rounded md:col-span-2' value={cfg.brand_login_background_text||''} onChange={e=>setCfg({...cfg,brand_login_background_text:e.target.value})} placeholder='Login background text'/>
      <input className='border p-2 rounded md:col-span-2' value={cfg.brand_footer_text||''} onChange={e=>setCfg({...cfg,brand_footer_text:e.target.value})} placeholder='Footer text'/>
      <div><p className='text-sm'>Logo</p><input type='file' onChange={e=>upload('logo',e.target.files?.[0])}/></div>
      <div><p className='text-sm'>Favicon</p><input type='file' onChange={e=>upload('favicon',e.target.files?.[0])}/></div>
      <button onClick={save} className='bg-slate-900 text-white rounded px-3 py-2'>Save Branding</button>
      {msg&&<div className='text-emerald-600'>{msg}</div>}
    </div>
  </div>
}
