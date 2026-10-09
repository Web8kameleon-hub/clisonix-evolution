export default function Head() {
  const title = 'Why Clisonix | Official AI Platform, Infrastructure, and Developer Value';
  const description =
    'See why Clisonix stands out: real AI infrastructure, Curiosity Ocean, observability, billing, SDKs, and a production-ready platform at clisonix.com.';
  const url = 'https://www.clisonix.com/why-clisonix';

  return (
    <>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta
        name="keywords"
        content="Why Clisonix, Clisonix platform, Clisonix Cloud, AI infrastructure, developer AI stack"
      />
      <link rel="canonical" href={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:type" content="website" />
    </>
  );
}
