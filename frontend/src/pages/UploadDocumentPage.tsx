import { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';

export default function UploadDocumentPage(){
  const [users,setUsers]=useState<any[]>([]); const [msg,setMsg]=useState(''); const [err,setErr]=useState('');
  const [document_name,setName]=useState(''); const [description,setDesc]=useState(''); const [workflow_type,setType]=useState('single'); const [selected,setSelected]=useState<number[]>([]); const [file,setFile]=useState<File|null>(null)
  useEffect(()=>{api.get('/admin/users').then(r=>setUsers(r.data.filter((u:any)=>u.is_active))).catch(()=>setUsers([]))},[])
  const signer_ids = useMemo(()=>selected.join(','),[selected])
  const toggle=(id:number)=>setSelected(prev=>prev.includes(id)?prev.filter(x=>x!==id):[...prev,id])
  const submit=async()=>{setErr('');setMsg(''); try{if(!file) throw new Error('Please select a PDF file'); if(!selected.length) throw new Error('Select at least one signer'); const d=new FormData(); d.append('document_name',document_name); d.append('description',description); d.append('workflow_type',workflow_type); d.append('signer_ids',signer_ids); d.append('file',file); const r=await api.post('/documents/upload',d); setMsg(`Uploaded document ${r.data.document_id}`); setSelected([]); setFile(null);}catch(e:any){setErr(e?.response?.data?.detail||e?.message||'Upload failed')}}
  return <div className='space-y-4'><h2 className='text-2xl font-semibold'>Upload Document</h2>
    <div className='bg-white rounded-xl border p-4 grid md:grid-cols-2 gap-4'>
      <input className='border p-2 rounded' placeholder='Document Name' value={document_name} onChange={e=>setName(e.target.value)}/>
      <select className='border p-2 rounded' value={workflow_type} onChange={e=>setType(e.target.value)}><option value='single'>Single Signer</option><option value='sequential'>Sequential Multi-Signer</option></select>
      <input className='border p-2 rounded md:col-span-2' placeholder='Description' value={description} onChange={e=>setDesc(e.target.value)}/>
      <div className='md:col-span-2 border rounded p-3'><p className='font-medium mb-2'>Select Signers (order = selection order)</p><div className='grid md:grid-cols-3 gap-2'>{users.map((u:any)=><label key={u.id} className='border rounded p-2 flex gap-2 items-center'><input type='checkbox' checked={selected.includes(u.id)} onChange={()=>toggle(u.id)} /><span>{u.display_name} ({u.username}) - #{u.id}</span></label>)}</div><p className='text-xs text-slate-500 mt-2'>Selected signer IDs: {signer_ids || '-'}</p></div>
      <input type='file' accept='application/pdf' onChange={e=>setFile(e.target.files?.[0]||null)} className='md:col-span-2'/>
      <button onClick={submit} className='bg-slate-900 text-white rounded px-4 py-2'>Submit for Signing</button>
      {msg&&<div className='text-emerald-600'>{msg}</div>}{err&&<div className='text-rose-600'>{err}</div>}
    </div></div>
}
