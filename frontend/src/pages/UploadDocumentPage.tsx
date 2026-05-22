import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function UploadDocumentPage(){
  const [users,setUsers]=useState<any[]>([]); const [msg,setMsg]=useState(''); const [err,setErr]=useState('');
  const [document_name,setName]=useState(''); const [description,setDesc]=useState(''); const [workflow_type,setType]=useState('single'); const [signer_ids,setSignerIds]=useState(''); const [file,setFile]=useState<File|null>(null)
  useEffect(()=>{api.get('/admin/users').then(r=>setUsers(r.data)).catch(()=>{})},[])
  const submit=async()=>{setErr('');setMsg(''); try{const d=new FormData(); d.append('document_name',document_name); d.append('description',description); d.append('workflow_type',workflow_type); d.append('signer_ids',signer_ids); if(file)d.append('file',file); const r=await api.post('/documents/upload',d); setMsg(`Uploaded document ${r.data.document_id}`)}catch(e:any){setErr(e?.response?.data?.detail||'Upload failed')}}
  return <div className='space-y-4'><h2 className='text-2xl font-semibold'>Upload Document</h2>
    <div className='bg-white rounded-xl border p-4 grid md:grid-cols-2 gap-4'>
      <input className='border p-2 rounded' placeholder='Document Name' value={document_name} onChange={e=>setName(e.target.value)}/>
      <select className='border p-2 rounded' value={workflow_type} onChange={e=>setType(e.target.value)}><option value='single'>Single Signer</option><option value='sequential'>Sequential Multi-Signer</option></select>
      <input className='border p-2 rounded md:col-span-2' placeholder='Description' value={description} onChange={e=>setDesc(e.target.value)}/>
      <div className='md:col-span-2'><p className='text-sm mb-1'>Signer IDs (comma separated in order)</p><input className='border p-2 rounded w-full' value={signer_ids} onChange={e=>setSignerIds(e.target.value)} placeholder='e.g. 2,3'/><p className='text-xs text-slate-500 mt-1'>Available: {users.map(u=>`${u.id}:${u.username}`).join(', ')}</p></div>
      <input type='file' accept='application/pdf' onChange={e=>setFile(e.target.files?.[0]||null)} className='md:col-span-2'/>
      <button onClick={submit} className='bg-slate-900 text-white rounded px-4 py-2'>Submit for Signing</button>
      {msg&&<div className='text-emerald-600'>{msg}</div>}{err&&<div className='text-rose-600'>{err}</div>}
    </div></div>
}
