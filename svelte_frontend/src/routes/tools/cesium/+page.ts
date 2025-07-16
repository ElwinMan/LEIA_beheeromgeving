import { fetchCesiums } from '$lib/api';
import type { LoadEvent } from '@sveltejs/kit';

export async function load({ fetch }: LoadEvent) {
  try {
    const cesiums = await fetchCesiums(fetch);
    return {
      cesiums,
      error: null
    };
  } catch (error) {
    console.error('Failed to load cesiums:', error);
    return {
      cesiums: [],
      error: 'Kon de Cesiums niet laden. Controleer of de API server draait.'
    };
  }
}