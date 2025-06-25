import { fetchDigitalTwin } from '$lib/api';

export async function load({ params }) {
	const digitalTwin = await fetchDigitalTwin(params.id);
	return { digitalTwin };
}
