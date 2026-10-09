export default function Head() {
  const title = "Clisonix Developers | API Reference, Endpoints, and Integration Docs";
  const description =
    "Official developer page for Clisonix APIs, endpoint coverage, integration guidance, and production-ready AI platform tooling.";
  const url = "https://www.clisonix.com/developers";

  return (
    <>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta
        name="keywords"
        content="Clisonix API, Clisonix developers, Curiosity Ocean API, AI API platform, developer docs"
      />
      <link rel="canonical" href={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:type" content="website" />
    </>
  );
}
