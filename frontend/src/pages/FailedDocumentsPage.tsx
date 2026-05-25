import { useEffect, useState } from 'react'; import { api } from '../api/client'; import DocumentTable from '../components/DocumentTable';
export default function FailedDocumentsPage(){const [rows,setRows]=useState<any[]>([]); useEffect(()=>{api.get('/documents/failed').then(r=>setRows(r.data))},[])
return <div className='space-y-4'><h2 className='text-2xl font-semibold'>Failed Documents</h2><DocumentTable rows={rows}/></div>}
