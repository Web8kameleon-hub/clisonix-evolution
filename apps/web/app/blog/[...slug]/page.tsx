import { redirect } from 'next/navigation';

interface BlogSlugPageProps {
  params: Promise<{ slug: string[] }>;
}

export default async function BlogSlugPage({ params }: BlogSlugPageProps) {
  const { slug } = await params;
  const slugPath = slug?.length ? `${slug.join('/')}/` : '';
  redirect(`https://ledjanahmati.github.io/clisonix-blog/${slugPath}`);
}
