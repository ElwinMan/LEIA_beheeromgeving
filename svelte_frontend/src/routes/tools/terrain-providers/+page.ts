import { fetchTerrainProviders } from '$lib/api';
import type { LoadEvent } from '@sveltejs/kit';

export async function load({ fetch }: LoadEvent) {
  try {
    const terrain_providers = await fetchTerrainProviders(fetch);
    return {
      terrain_providers,
      error: null
    };
  } catch (error) {
    console.error('Failed to load terrain providers:', error);
    return {
      terrain_providers: [],
      error: 'Kon de terrain providers niet laden. Controleer of de API server draait.'
    };
  }
}