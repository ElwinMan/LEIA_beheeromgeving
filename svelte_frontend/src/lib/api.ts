const API_BASE = import.meta.env.VITE_API_BASE_URL;

export async function fetchDigitalTwins() {
	const res = await fetch(`${API_BASE}/digital_twins`);
	if (!res.ok) throw new Error('Failed to fetch digital twins');
	return await res.json();
}

// the id arrives as string
export async function fetchDigitalTwin(id: string) {
	const res = await fetch(`${API_BASE}/digital_twins/${id}`);
	if (!res.ok) throw new Error(`Failed to fetch digital twin with ID ${id}`);
	return await res.json();
}

export async function fetchLayers() {
	const res = await fetch(`${API_BASE}/layers`);
	if (!res.ok) throw new Error(`Failed to fetch layers `);
	return await res.json();
}

export async function fetchLayer(id: string) {
	const res = await fetch(`${API_BASE}/layers/${id}`);
	if (!res.ok) throw new Error(`Failed to fetch digital twin with ID ${id}`);
	return await res.json();
}