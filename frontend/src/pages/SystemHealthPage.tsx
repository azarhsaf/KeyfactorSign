import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function SystemHealthPage(){
  const [d,setD]=useState<any>(null);
  useEffect(()=>{api.get('/admin/system/diagnostics').then(r=>setD(r.data))},[])
  return <div className='space-y-4'>
    <h2 className='text-2xl font-semibold'>System Health / Diagnostics</h2>
    <div className='bg-white border rounded p-4'>{d?<pre className='text-sm whitespace-pre-wrap'>{JSON.stringify(d,null,2)}</pre>:'Loading diagnostics...'}</div>
  </div>
}
