export default function Head() {
  const title = 'Clisonix Landing | Official Developer AI Platform and Cloud Infrastructure';
  const description =
    'Explore the Clisonix landing page for developer-first AI infrastructure, platform architecture, live modules, and production-ready cloud tooling.';
  const url = 'https://www.clisonix.com/landing';

  return (
    <>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta
        name="keywords"
        content="Clisonix landing, developer AI platform, Clisonix Cloud, cloud infrastructure, AI modules"
      />
      <link rel="canonical" href={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:type" content="website" />
    </>
  );
}
