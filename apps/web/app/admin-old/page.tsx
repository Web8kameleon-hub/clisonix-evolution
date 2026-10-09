import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default async function AdminOldPage() {
  const cookieStore = await cookies();
  const gateCookie = cookieStore.get('clx_legacy_gate');

  if (gateCookie?.value !== 'granted') {
    redirect('/');
  }

  redirect('/dashboard');
}
