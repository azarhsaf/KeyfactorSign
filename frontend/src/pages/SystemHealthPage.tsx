import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function SystemHealthPage(){
  const [d,setD]=useState<any>(null); const [h,setH]=useState<any>(null);
  useEffect(()=>{api.get('/admin/system/diagnostics').then(r=>setD(r.data)); api.get('/health').then(r=>setH(r.data))},[])
  return <div className='space-y-4'>
    <h2 className='text-2xl font-semibold'>System Health / Diagnostics</h2>
    <div className='bg-white border rounded-xl p-4'>
      <div className='font-medium mb-2'>Application Version: Keyfactor SignPortal v{h?.version||'dev'}</div>
      <pre className='text-sm whitespace-pre-wrap'>{JSON.stringify(d,null,2)}</pre>
    </div>
  </div>
}
