import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import LoginPage from './pages/LoginPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import DashboardPage from './pages/DashboardPage';
import UploadDocumentPage from './pages/UploadDocumentPage';
import PendingSignaturesPage from './pages/PendingSignaturesPage';
import CompletedDocumentsPage from './pages/CompletedDocumentsPage';
import AuditLogsPage from './pages/AuditLogsPage';
import AdminSettingsPage from './pages/AdminSettingsPage';
import UsersPage from './pages/UsersPage';
import SignServerSettingsPage from './pages/SignServerSettingsPage';
import LdapSettingsPage from './pages/LdapSettingsPage';
import SmtpSettingsPage from './pages/SmtpSettingsPage';
import DocumentPreviewPage from './pages/DocumentPreviewPage';
import FailedDocumentsPage from './pages/FailedDocumentsPage';
import MyDocumentsPage from './pages/MyDocumentsPage';
import BrandingSettingsPage from './pages/BrandingSettingsPage';
import SystemHealthPage from './pages/SystemHealthPage';
import AppLayout from './layouts/AppLayout';
import { api } from './api/client';

type Me = { id:number; username:string; role:string; must_change_password:boolean } | null;

const Protected = ({me,children,adminOnly=false}:{me:Me,children:any,adminOnly?:boolean}) => {
  const loc = useLocation();
  if(!localStorage.getItem('token')) return <Navigate to='/login' state={{from:loc.pathname}} replace />;
  if(!me) return <div className='p-6'>Loading session...</div>;
  if(me.must_change_password && loc.pathname !== '/change-password') return <Navigate to='/change-password' replace />;
  if(adminOnly && me.role !== 'admin') return <Navigate to='/dashboard' replace />;
  return children;
}

export default function App() {
  const [me,setMe] = useState<Me>(null);
  const token = localStorage.getItem('token');

  useEffect(()=>{
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      api.get('/auth/me').then(r=>setMe(r.data)).catch(()=>setMe(null));
    } else setMe(null);
  },[token]);

  const Wrap = (c: any, adminOnly=false) => (
    <Protected me={me} adminOnly={adminOnly}>
      <AppLayout admin={me?.role === 'admin'}>{c}</AppLayout>
    </Protected>
  );

  return <Routes>
    <Route path='/login' element={<LoginPage />} />
    <Route path='/change-password' element={Wrap(<ChangePasswordPage />)} />
    <Route path='/dashboard' element={Wrap(<DashboardPage />)} />
    <Route path='/upload-document' element={Wrap(<UploadDocumentPage />)} />
    <Route path='/pending-signatures' element={Wrap(<PendingSignaturesPage />)} />
    <Route path='/completed-documents' element={Wrap(<CompletedDocumentsPage />)} />
    <Route path='/audit-logs' element={Wrap(<AuditLogsPage />)} />
    <Route path='/my-documents' element={Wrap(<MyDocumentsPage />)} />
    <Route path='/failed-documents' element={Wrap(<FailedDocumentsPage />)} />
    <Route path='/document-preview/:id' element={Wrap(<DocumentPreviewPage />)} />

    <Route path='/admin-settings' element={Wrap(<AdminSettingsPage />, true)} />
    <Route path='/users' element={Wrap(<UsersPage />, true)} />
    <Route path='/signserver-settings' element={Wrap(<SignServerSettingsPage />, true)} />
    <Route path='/ldap-settings' element={Wrap(<LdapSettingsPage />, true)} />
    <Route path='/smtp-settings' element={Wrap(<SmtpSettingsPage />, true)} />
    <Route path='/branding-settings' element={Wrap(<BrandingSettingsPage />, true)} />
    <Route path='/system-health' element={Wrap(<SystemHealthPage />, true)} />

    <Route path='/logout' element={<Navigate to='/login' />} />
    <Route path='*' element={<Navigate to={token ? '/dashboard' : '/login'} />} />
  </Routes>;
}
