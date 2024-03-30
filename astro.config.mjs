import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
    site: process.env.BASE_PATH || 'https://example.com',
    integrations: [mdx(), sitemap()],
});
