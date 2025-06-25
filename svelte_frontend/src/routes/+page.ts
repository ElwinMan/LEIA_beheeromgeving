import { fetchDigitalTwins } from '$lib/api';

export async function load() {
	const digitalTwins = await fetchDigitalTwins();
	return { digitalTwins };
}