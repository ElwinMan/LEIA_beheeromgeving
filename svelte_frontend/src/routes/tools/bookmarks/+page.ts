import { fetchBookmarks } from '$lib/api';
import type { LoadEvent } from '@sveltejs/kit';

export async function load({ fetch }: LoadEvent) {
  try {
    const bookmarks = await fetchBookmarks(fetch);
    return {
      bookmarks,
      error: null
    };
  } catch (error) {
    console.error('Failed to load bookmarks:', error);
    return {
      bookmarks: [],
      error: 'Kon de bookmarks niet laden. Controleer of de API server draait.'
    };
  }
}