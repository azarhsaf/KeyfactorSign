import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function SmtpSettingsPage(){
  const [cfg,setCfg]=useState<any>({});
  const [to,setTo]=useState('');
  const [result,setResult]=useState<any>(null);
  useEffect(()=>{api.get('/admin/smtp/settings').then(r=>setCfg(r.data))},[])
  const test=async()=>setResult((await api.post('/admin/smtp/test')).data)
  const send=async()=>{const d=new FormData(); d.append('to_email',to); setResult((await api.post('/admin/smtp/send-test',d)).data)}
  return <div className='space-y-4'>
    <h2 className='text-2xl font-semibold'>SMTP / Email Relay</h2>
    <div className='bg-white border rounded p-4 space-y-2 text-sm'>
      {Object.entries(cfg).map(([k,v])=><div key={k}><b>{k}</b>: {String(v)}</div>)}
      <div className='flex gap-2'>
        <button onClick={test} className='bg-slate-900 text-white px-3 py-2 rounded'>Test Connection</button>
        <input className='border rounded p-2' placeholder='test email recipient' value={to} onChange={e=>setTo(e.target.value)}/>
        <button onClick={send} className='bg-blue-700 text-white px-3 py-2 rounded'>Send Test Email</button>
      </div>
      {result&&<pre className='bg-slate-50 p-2'>{JSON.stringify(result,null,2)}</pre>}
    </div>
  </div>
}
