import { fetchProjects } from '$lib/api';
import type { LoadEvent } from '@sveltejs/kit';

export async function load({ fetch }: LoadEvent) {
  try {
    const projects = await fetchProjects(fetch);
    return {
      projects,
      error: null
    };
  } catch (error) {
    console.error('Failed to load projects:', error);
    return {
      projects: [],
      error: 'Kon de projecten niet laden. Controleer of de API server draait.'
    };
  }
}