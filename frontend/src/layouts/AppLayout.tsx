import Sidebar from '../components/Sidebar';import Topbar from '../components/Topbar';
export default function AppLayout({children,admin}:{children:any,admin:boolean}){return <div className='flex'><Sidebar admin={admin}/><main className='flex-1'><Topbar/><div className='p-6'>{children}</div></main></div>}
