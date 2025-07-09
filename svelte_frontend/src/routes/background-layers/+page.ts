import { fetchLayers } from '$lib/api';
import type { Layer } from '$lib/types/layer';

export async function load() {
  try {
    const layers = await fetchLayers();
    return {
      layers: layers.filter((layer: Layer) => layer.isBackground),
      error: null
    };
  } catch (error) {
    console.error('Failed to load layers:', error);
    return {
      layers: [],
      error: 'Kon de lagen niet laden. Controleer of de API server draait op localhost:8000.'
    };
  }
}
