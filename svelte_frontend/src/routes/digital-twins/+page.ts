import { fetchDigitalTwins } from '$lib/api';

export async function load() {
  try {
    const digitalTwins = await fetchDigitalTwins();
    return {
      digitalTwins,
      error: null
    };
  } catch (error) {
    console.error('Failed to load digital twins:', error);
    return {
      digitalTwins: [],
      error: 'Kon digital twins niet laden. Controleer of de API server draait op localhost:8000.'
    };
  }
}
