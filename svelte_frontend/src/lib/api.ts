const API_BASE = import.meta.env.VITE_API_BASE_URL
import type { DigitalTwin, BulkAssociationsPayload, DigitalTwinViewerResponse, ViewerContent, BulkToolOperation, BulkToolPayload } from '$lib/types/digitalTwin';

type LayerAssociation = {}

type Group = {}

export async function fetchDigitalTwins() {
  const res = await fetch(`${API_BASE}/digital-twins`)
  if (!res.ok) throw new Error("Failed to fetch digital twins")
  return await res.json()
}

export async function updateDigitalTwin(digitalTwinId: string, data: Partial<DigitalTwin>) {
  try {
    const res = await fetch(`${API_BASE}/digital-twins/${digitalTwinId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!res.ok) throw new Error(`Failed to update digital twin with ID ${digitalTwinId}`);
    return await res.json();
  } catch (error) {
    console.error('Error updating digital twin:', error);
    throw error;
  }
}

export async function fetchDigitalTwin(id: string) {
  const res = await fetch(`${API_BASE}/digital-twins/${id}`)
  if (!res.ok) throw new Error(`Failed to fetch digital twin with ID ${id}`)
  return await res.json()
}

export async function fetchDigitalTwinViewer(id: string): Promise<DigitalTwinViewerResponse> {
  const res = await fetch(`${API_BASE}/digital-twins/${id}/viewer`);
  if (!res.ok) throw new Error(`Failed to load viewer data (status: ${res.status})`);
  return await res.json();
}

export async function updateDigitalTwinViewer(id: string, content: ViewerContent): Promise<DigitalTwinViewerResponse> {
  const res = await fetch(`${API_BASE}/digital-twins/${id}/viewer`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ content })
  });

  if (!res.ok) {
    throw new Error(`Failed to update digital twin viewer: ${res.statusText}`);
  }

  return await res.json();
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

export async function fetchTools() {
  const res = await fetch(`${API_BASE}/tools`)
  if (!res.ok) throw new Error("Failed to fetch layers")
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

export async function bulkUpdateDigitalTwinAssociations(digitalTwinId: string, payload: BulkAssociationsPayload) {
  return fetch(`${API_BASE}/digital-twins/${digitalTwinId}/associations/bulk`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(res => {
    if (!res.ok) throw new Error(`Failed to save: ${res.statusText}`);
    return res.json();
  });
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

export async function bulkModifyToolAssociations(digitalTwinId: number | string, operations: BulkToolOperation[]) {
  const payload = { operations };

  const res = await fetch(`${API_BASE}/digital-twins/${digitalTwinId}/tools/bulk`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Failed to bulk modify tool associations: ${errText}`);
  }

  return res.json();
}