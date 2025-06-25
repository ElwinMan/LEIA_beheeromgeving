import { fetchLayers } from '$lib/api';

export async function load() {
    const layers = await fetchLayers();
    return { layers };
}
