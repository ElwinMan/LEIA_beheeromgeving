import tailwindcss from '@tailwindcss/vite';
import devtoolsJson from 'vite-plugin-devtools-json';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { viteStaticCopy } from 'vite-plugin-static-copy';

const cesiumSource = 'node_modules/cesium/Build/Cesium';

export default defineConfig({
  plugins: [
    tailwindcss(), 
    sveltekit(), 
    devtoolsJson(),
    // Copy Cesium Assets, Widgets, and Workers to a static directory
    viteStaticCopy({
      targets: [
        { src: `${cesiumSource}/ThirdParty`, dest: 'cesium' },
        { src: `${cesiumSource}/Workers`, dest: 'cesium' },
        { src: `${cesiumSource}/Assets`, dest: 'cesium' },
        { src: `${cesiumSource}/Widgets`, dest: 'cesium' },
      ],
    }),
  ],
  define: {
    CESIUM_BASE_URL: JSON.stringify('/cesium/')
  },
  optimizeDeps: {
    include: ['cesium']
  }
});
