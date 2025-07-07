import { fetchLayer } from '$lib/api';

export async function load({ params }) {
	try {
		const layer = await fetchLayer( params.id );
		return {
			id: params.id,
			layer,
			error: null
		};
	} catch (error) {
		console.error('Failed to load layer:', error);
		return {
			layer: [],
			error: 'Kon de lagen niet laden. Controleer of de API server draait op localhost:8000.'
		};
	}
}
