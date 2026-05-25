
import { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';

export default function UploadDocumentPage(){
  const [users,setUsers]=useState<any[]>([]); const [msg,setMsg]=useState(''); const [err,setErr]=useState('');
  const [document_name,setName]=useState(''); const [description,setDesc]=useState(''); const [workflow_type,setType]=useState('single'); const [selected,setSelected]=useState<number[]>([]); const [file,setFile]=useState<File|null>(null)
  const [dueDate,setDueDate]=useState(''); const [signerMessage,setSignerMessage]=useState(''); const [sendEmail,setSendEmail]=useState(true);
  useEffect(()=>{api.get('/admin/users').then(r=>setUsers(r.data.filter((u:any)=>u.is_active))).catch(()=>setUsers([]))},[])
  const signer_ids = useMemo(()=>selected.join(','),[selected])
  const toggle=(id:number)=>setSelected(prev=>prev.includes(id)?prev.filter(x=>x!==id):[...prev,id])
  const move=(id:number,dir:number)=>setSelected(prev=>{const i=prev.indexOf(id); if(i<0)return prev; const j=i+dir; if(j<0||j>=prev.length)return prev; const n=[...prev]; [n[i],n[j]]=[n[j],n[i]]; return n;})

  const submit=async()=>{setErr('');setMsg(''); try{if(!file) throw new Error('Please select a PDF file'); if(!selected.length) throw new Error('Select at least one signer'); const d=new FormData(); d.append('document_name',document_name); d.append('description',`${description}
Due:${dueDate||'-'}
Message:${signerMessage||'-'}
SendEmail:${sendEmail}`); d.append('workflow_type',workflow_type); d.append('signer_ids',signer_ids); d.append('file',file); const r=await api.post('/documents/upload',d); setMsg(`Uploaded document ${r.data.document_id}`); setSelected([]); setFile(null);}catch(e:any){setErr(e?.response?.data?.detail||e?.message||'Upload failed')}}

  return <div className='space-y-4'><h2 className='text-2xl font-semibold'>Upload Document</h2>
    <div className='bg-white rounded-xl border p-4 grid md:grid-cols-2 gap-4'>
      <input className='border p-2 rounded' placeholder='Document Title' value={document_name} onChange={e=>setName(e.target.value)}/>
      <select className='border p-2 rounded' value={workflow_type} onChange={e=>setType(e.target.value)}><option value='single'>Single Signer</option><option value='sequential'>Sequential Multi-Signer</option></select>
      <input className='border p-2 rounded md:col-span-2' placeholder='Description' value={description} onChange={e=>setDesc(e.target.value)}/>
      <input type='date' className='border p-2 rounded' value={dueDate} onChange={e=>setDueDate(e.target.value)} />
      <label className='flex items-center gap-2'><input type='checkbox' checked={sendEmail} onChange={e=>setSendEmail(e.target.checked)} /> Send email notification</label>
      <input className='border p-2 rounded md:col-span-2' placeholder='Message to signers' value={signerMessage} onChange={e=>setSignerMessage(e.target.value)} />
      <div className='md:col-span-2 border rounded p-3'><p className='font-medium mb-2'>Select Signers (use arrows for order)</p><div className='space-y-2'>{users.map((u:any)=>{const chosen=selected.includes(u.id); return <div key={u.id} className='border rounded p-2 flex justify-between items-center'><label className='flex gap-2 items-center'><input type='checkbox' checked={chosen} onChange={()=>toggle(u.id)} /><span>{u.display_name} ({u.username}) - #{u.id}</span></label>{chosen&&<div className='flex gap-1'><button className='px-2 border rounded' onClick={()=>move(u.id,-1)}>↑</button><button className='px-2 border rounded' onClick={()=>move(u.id,1)}>↓</button></div>}</div>})}</div><p className='text-xs text-slate-500 mt-2'>Signer order IDs: {signer_ids || '-'}</p></div>
      <input type='file' accept='application/pdf' onChange={e=>setFile(e.target.files?.[0]||null)} className='md:col-span-2'/>
      <button onClick={submit} className='bg-slate-900 text-white rounded px-4 py-2'>Submit for Signing</button>
      {msg&&<div className='text-emerald-600'>{msg}</div>}{err&&<div className='text-rose-600'>{err}</div>}
    </div></div>
}
