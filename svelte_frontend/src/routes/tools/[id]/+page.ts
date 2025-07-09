import { fetchTool } from '$lib/api';

export async function load({ params }) {
  try {
    const tool = await fetchTool(params.id);
    return {
      tool,
      error: null
    };
  } catch (error) {
    console.error('Failed to load tool:', error);
    return {
      tool: [],
      error: 'Kon de lagen niet laden. Controleer of de API server draait op localhost:8000.'
    };
  }
}
