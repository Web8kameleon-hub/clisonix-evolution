import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  const siteUrl = "https://www.clisonix.com";
  const publicAllowPaths = ["/", "/_next/static/", "/icons/", "/images/"];
  const privateDisallowPaths = [
    "/api/",
    "/admin/",
    "/user/",
    "/sign-in/",
    "/sign-up/",
    "/modules/",
    "/app/",
    "/dashboard/",
    "/internal/",
    "/ultra/",
  ];

  return {
    rules: [
      {
        userAgent: "*",
        allow: publicAllowPaths,
        disallow: privateDisallowPaths,
      },
      {
        userAgent: "Googlebot",
        allow: publicAllowPaths,
        disallow: privateDisallowPaths,
      },
      {
        userAgent: "Bingbot",
        allow: publicAllowPaths,
        disallow: privateDisallowPaths,
      },
      {
        userAgent: "DuckDuckBot",
        allow: publicAllowPaths,
        disallow: privateDisallowPaths,
      },
      {
        userAgent: "Slurp",
        allow: publicAllowPaths,
        disallow: privateDisallowPaths,
      },
      {
        userAgent: "Teoma",
        allow: publicAllowPaths,
        disallow: privateDisallowPaths,
      },
      {
        userAgent: "facebookexternalhit",
        allow: "/",
      },
      {
        userAgent: "Twitterbot",
        allow: "/",
      },
      {
        userAgent: "LinkedInBot",
        allow: "/",
      },
      {
        userAgent: "WhatsApp",
        allow: "/",
      },
      {
        userAgent: "Applebot",
        allow: "/",
      },
      {
        userAgent: "AhrefsBot",
        disallow: "/",
      },
      {
        userAgent: "SemrushBot",
        disallow: "/",
      },
      {
        userAgent: "DotBot",
        disallow: "/",
      },
    ],
    sitemap: `${siteUrl}/sitemap.xml`,
    host: siteUrl,
  };
}
