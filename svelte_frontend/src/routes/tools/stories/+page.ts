import { fetchStories } from '$lib/api';
import type { LoadEvent } from '@sveltejs/kit';

export async function load({ fetch }: LoadEvent) {
  try {
    const stories = await fetchStories(fetch);
    return {
      stories,
      error: null
    };
  } catch (error) {
    console.error('Failed to load stories:', error);
    return {
      stories: [],
      error: 'Kon de stories niet laden. Controleer of de API server draait.'
    };
  }
}