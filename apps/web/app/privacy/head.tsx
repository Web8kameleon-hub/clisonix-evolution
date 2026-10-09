export default function Head() {
  const title = 'Privacy Policy | Clisonix Cloud';
  const description =
    'Read the Clisonix Cloud privacy policy covering Google sign-in, account data, platform usage, analytics, and security practices.';
  const url = 'https://www.clisonix.com/privacy';

  return (
    <>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content="Clisonix privacy, Clisonix Cloud privacy policy, Google sign-in privacy" />
      <link rel="canonical" href={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:type" content="website" />
    </>
  );
}
