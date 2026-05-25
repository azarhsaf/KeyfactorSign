import { useEffect, useState } from 'react';
import { api } from '../api/client';
export default function AuthLayout({children}:{children:any}){
  const [b,setB]=useState<any>({brand_product_name:'Keyfactor SignPortal',brand_login_background_text:'Secure signing workflows powered by SignServer',brand_footer_text:'Keyfactor SignPortal'})
  useEffect(()=>{api.get('/branding').then(r=>setB((x:any)=>({...x,...r.data}))).catch(()=>{})},[])
  return <div className='min-h-screen grid md:grid-cols-2'><div className='bg-slate-900 text-white p-16 flex items-center'><div><h1 className='text-4xl font-bold mb-4'>{b.brand_product_name}</h1><p>{b.brand_login_background_text}</p></div></div><div className='flex items-center justify-center'><div className='w-full max-w-xl'>{children}<p className='text-center text-xs text-slate-500 mt-6'>{b.brand_footer_text}</p></div></div></div>
}
