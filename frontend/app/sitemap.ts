import { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://elyx.ai'; // Replace with your actual domain

  const routes = [
    '',
    '/dashboard',
    '/operations',
    '/comms',
    '/business',
    '/system-monitor',
    '/decision-analysis',
    '/scheduling',
    '/security',
  ].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date().toISOString(),
    changeFrequency: 'daily' as const,
    priority: route === '' ? 1 : 0.8,
  }));

  return routes;
}
