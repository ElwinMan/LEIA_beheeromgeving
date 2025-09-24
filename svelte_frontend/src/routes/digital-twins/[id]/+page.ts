import { fetchDigitalTwin } from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
  try {
    const digitalTwin = await fetchDigitalTwin(params.id, fetch);
    
    return {
      id: params.id,
      digitalTwin,
      error: null
    };
  } catch (err) {
    console.error('Failed to load digital twin:', err);
    
    // Check if it's a 404 error (digital twin not found)
    if (err instanceof Error && err.message.includes('404')) {
      throw error(404, `Digital twin with ID ${params.id} not found`);
    }
    
    // For other errors, return error state instead of throwing
    return {
      id: params.id,
      digitalTwin: null,
      error: 'Kon digital twin niet laden. Controleer of de API server draait.'
    };
  }
};
