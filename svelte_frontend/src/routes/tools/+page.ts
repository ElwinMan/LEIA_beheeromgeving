import { fetchTools } from '$lib/api';

export async function load() {
  try {
    const tools = await fetchTools();
    return {
      tools,
      error: null
    };
  } catch (error) {
    console.error('Failed to load tools:', error);
    return {
      tools: [],
      error: 'Kon de lagen niet laden. Controleer of de API server draait op localhost:8000.'
    };
  }
}
