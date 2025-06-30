const API_BASE = import.meta.env.VITE_API_BASE_URL
import type { LayerBulkOperation } from '$lib/types/digitalTwin';

const operations: LayerBulkOperation[] = [];

type LayerAssociation = {}

type Group = {}

export async function fetchDigitalTwins() {
  const res = await fetch(`${API_BASE}/digital-twins`)
  if (!res.ok) throw new Error("Failed to fetch digital twins")
  return await res.json()
}

export async function fetchDigitalTwin(id: string) {
  const res = await fetch(`${API_BASE}/digital-twins/${id}`)
  if (!res.ok) throw new Error(`Failed to fetch digital twin with ID ${id}`)
  return await res.json()
}

export async function fetchLayers() {
  const res = await fetch(`${API_BASE}/layers`)
  if (!res.ok) throw new Error("Failed to fetch layers")
  return await res.json()
}

export async function fetchLayer(id: string) {
  const res = await fetch(`${API_BASE}/layers/${id}`)
  if (!res.ok) throw new Error(`Failed to fetch layer with ID ${id}`)
  return await res.json()
}

export async function fetchGroups(digitalTwinId: string) {
  const res = await fetch(`${API_BASE}/digital-twins/${digitalTwinId}/groups`)
  if (!res.ok) throw new Error("Failed to fetch groups")
  return await res.json()
}

export async function updateDigitalTwinLayerOrder(digitalTwinId: string, layerAssociations: LayerAssociation[]) {
  try {
    const res = await fetch(`${API_BASE}/digital-twins/${digitalTwinId}/layers`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ layer_associations: layerAssociations }),
    })
    if (!res.ok) throw new Error("Failed to update layer order")
    return await res.json()
  } catch (error) {
    console.error("Error updating layer order:", error)
    throw error
  }
}

export async function bulkUpdateDigitalTwinLayers(digitalTwinId: string, operations: LayerBulkOperation[]) {
  try {
    const res = await fetch(`${API_BASE}/digital-twins/${digitalTwinId}/layer-associations/bulk`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ operations }),
    });
    if (!res.ok) throw new Error("Failed to update layer associations");
    return await res.json();
  } catch (error) {
    console.error("Error updating layer associations:", error);
    throw error;
  }
}

export async function updateGroupOrder(digitalTwinId: string, groups: Group[]) {
  try {
    const res = await fetch(`${API_BASE}/digital-twins/${digitalTwinId}/groups`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ groups }),
    })
    if (!res.ok) throw new Error("Failed to update group order")
    return await res.json()
  } catch (error) {
    console.error("Error updating group order:", error)
    throw error
  }
}
