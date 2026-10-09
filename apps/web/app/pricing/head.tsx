export default function Head() {
  const title = "Clisonix Pricing | AI Plans, Access Tiers, and Subscription Options";
  const description =
    "Review Clisonix pricing for AI tools, research workflows, Curiosity Ocean access, and subscription plans for individuals and teams.";
  const url = "https://www.clisonix.com/pricing";

  return (
    <>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta
        name="keywords"
        content="Clisonix pricing, AI subscription plans, Curiosity Ocean pricing, Clisonix Cloud plans"
      />
      <link rel="canonical" href={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:type" content="website" />
    </>
  );
}
