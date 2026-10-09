export default function Head() {
  const title = "Clisonix Platform | AI Infrastructure, KLOUd Bridge, and ASI Stack";
  const description =
    "Explore the Clisonix platform architecture: ASI Trinity, Curiosity Ocean, KLOUd Bridge, analytics services, and developer-grade AI infrastructure.";
  const url = "https://www.clisonix.com/platform";

  return (
    <>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta
        name="keywords"
        content="Clisonix platform, AI infrastructure, ASI Trinity, KLOUd Bridge, neural intelligence platform"
      />
      <link rel="canonical" href={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:type" content="website" />
    </>
  );
}
