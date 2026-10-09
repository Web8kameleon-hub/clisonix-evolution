export default function Head() {
  const title = "Curiosity Ocean | Clisonix AI Research and Multimodal Chat";
  const description =
    "Use Curiosity Ocean on Clisonix for AI chat, streaming research, voice, vision, document analysis, and multimodal exploration workflows.";
  const url = "https://www.clisonix.com/modules/curiosity-ocean";

  return (
    <>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta
        name="keywords"
        content="Curiosity Ocean, Clisonix AI chat, Clisonix research assistant, multimodal AI, voice AI, document analysis"
      />
      <link rel="canonical" href={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:type" content="website" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
    </>
  );
}
