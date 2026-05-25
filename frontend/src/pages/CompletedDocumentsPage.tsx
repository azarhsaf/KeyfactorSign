import { useEffect, useState } from 'react';
import { api } from '../api/client';
import DocumentTable from '../components/DocumentTable';

const dl = async (url:string,name:string)=>{
  const r = await api.get(url,{responseType:'blob'});
  const u=URL.createObjectURL(r.data); const a=document.createElement('a'); a.href=u; a.download=name; a.click(); URL.revokeObjectURL(u);
}

export default function CompletedDocumentsPage(){
  const [rows,setRows]=useState<any[]>([]);
  useEffect(()=>{api.get('/documents/completed').then(r=>setRows(r.data))},[])
  return <div className='space-y-4'>
    <h2 className='text-2xl font-semibold'>Completed Documents</h2>
    <DocumentTable rows={rows} actions={(r)=><div className='flex gap-2 flex-wrap'>
      <a className='text-blue-600' href={`/document-preview/${r.id}`}>View Signed</a>
      <button className='text-indigo-600' onClick={()=>dl(`/documents/${r.id}/download-original`,`${r.document_name}-original.pdf`)}>Download Original</button>
      <button className='text-emerald-600' onClick={()=>dl(`/documents/${r.id}/download-signed`,`${r.document_name}-signed.pdf`)}>Download Signed</button>
      <a className='text-slate-700' href={`/audit-logs?document=${r.id}`}>Audit Trail</a>
    </div>}/>
  </div>
}
