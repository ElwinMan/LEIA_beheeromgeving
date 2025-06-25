import { fetchLayer } from '$lib/api';

export async function load({ params }) {
    const layer = await fetchLayer(params.id);
    return { layer };
}
