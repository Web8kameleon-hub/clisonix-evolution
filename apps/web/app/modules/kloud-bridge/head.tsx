export default function Head() {
  const title = "KLOUd Bridge | Clisonix";
  const description =
    "KLOUd Bridge real-time infrastructure, telemetry, and container synchronization dashboard on Clisonix.";
  const url = "https://www.clisonix.com/modules/kloud-bridge";

  return (
    <>
      <title>{title}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:type" content="website" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="robots" content="index,follow" />
    </>
  );
}
