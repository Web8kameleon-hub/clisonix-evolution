import { MetadataRoute } from 'next';
import { SEO_INDEXABLE_MODULE_SLUGS } from "../src/lib/modules/platform-map";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = "https://www.clisonix.com";
  const now = new Date();

  const corePages = [
    {
      url: baseUrl,
      lastModified: now,
      changeFrequency: "daily" as const,
      priority: 1.0,
    },
    {
      url: `${baseUrl}/pricing`,
      lastModified: now,
      changeFrequency: "weekly" as const,
      priority: 0.95,
    },
    {
      url: `${baseUrl}/why-clisonix`,
      lastModified: now,
      changeFrequency: "weekly" as const,
      priority: 0.9,
    },
    {
      url: `${baseUrl}/platform`,
      lastModified: now,
      changeFrequency: "weekly" as const,
      priority: 0.9,
    },
    {
      url: `${baseUrl}/company`,
      lastModified: now,
      changeFrequency: "monthly" as const,
      priority: 0.85,
    },
    {
      url: `${baseUrl}/faq`,
      lastModified: now,
      changeFrequency: "weekly" as const,
      priority: 0.85,
    },
    {
      url: `${baseUrl}/developers`,
      lastModified: now,
      changeFrequency: "weekly" as const,
      priority: 0.8,
    },
    {
      url: `${baseUrl}/security`,
      lastModified: now,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    },
    {
      url: `${baseUrl}/privacy`,
      lastModified: now,
      changeFrequency: "monthly" as const,
      priority: 0.65,
    },
    {
      url: `${baseUrl}/terms`,
      lastModified: now,
      changeFrequency: "monthly" as const,
      priority: 0.65,
    },
  ];

  const moduleRoutes = Array.from(new Set(SEO_INDEXABLE_MODULE_SLUGS)).filter(
    (module) => module !== "how-to-use",
  );

  const dashboardModules = moduleRoutes.map((module) => ({
    url: `${baseUrl}/modules/${module}`,
    lastModified: now,
    changeFrequency: "weekly" as const,
    priority: module === "curiosity-ocean" || module === "web-reader" ? 0.8 : 0.72,
  }));

  return [...corePages, ...dashboardModules];
}
