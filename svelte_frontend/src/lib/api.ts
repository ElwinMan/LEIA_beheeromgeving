const API_BASE = import.meta.env.VITE_API_BASE_URL;
import type { DigitalTwin, DigitalTwinViewerResponse, ViewerContent } from '$lib/types/digitalTwin';
import type { BulkAssociationsPayload, BulkToolOperation } from '$lib/types/digitalTwinAssociation';
import type { Layer } from '$lib/types/layer';

export async function fetchDigitalTwins() {
  const res = await fetch(`${API_BASE}/digital-twins`);
  if (!res.ok) throw new Error('Failed to fetch digital twins');
  return await res.json();
}

export async function fetchDigitalTwin(id: string) {
  const res = await fetch(`${API_BASE}/digital-twins/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch digital twin with ID ${id}`);
  return await res.json();
}

export async function updateDigitalTwin(digitalTwinId: string, data: Partial<DigitalTwin>) {
  try {
    const res = await fetch(`${API_BASE}/digital-twins/${digitalTwinId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!res.ok) throw new Error(`Failed to update digital twin with ID ${digitalTwinId}`);
    return await res.json();
  } catch (error) {
    console.error('Error updating digital twin:', error);
    throw error;
  }
}

export async function fetchDigitalTwinViewer(id: string): Promise<DigitalTwinViewerResponse> {
  const res = await fetch(`${API_BASE}/digital-twins/${id}/viewer`);
  if (!res.ok) throw new Error(`Failed to load viewer data (status: ${res.status})`);
  return await res.json();
}

export async function updateDigitalTwinViewer(
  id: string,
  content: ViewerContent
): Promise<DigitalTwinViewerResponse> {
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
  const res = await fetch(`${API_BASE}/layers`);
  if (!res.ok) throw new Error('Failed to fetch layers');
  return await res.json();
}

export async function fetchLayer(id: string) {
  const res = await fetch(`${API_BASE}/layers/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch layer with ID ${id}`);
  return await res.json();
}

export async function updateLayer(layerId: string, data: Partial<Layer>) {
  const res = await fetch(`${API_BASE}/layers/${layerId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error(`Failed to update layer with ID ${layerId}`);
  return await res.json();
}

export async function fetchGroups(digitalTwinId: string) {
  const res = await fetch(`${API_BASE}/digital-twins/${digitalTwinId}/groups`);
  if (!res.ok) throw new Error('Failed to fetch groups');
  return await res.json();
}

export async function fetchTools() {
  const res = await fetch(`${API_BASE}/tools`);
  if (!res.ok) throw new Error('Failed to fetch layers');
  return await res.json();
}

export async function fetchTool(id: string) {
  const res = await fetch(`${API_BASE}/tools/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch tool with ID ${id}`);
  return await res.json();
}

export async function bulkUpdateDigitalTwinAssociations(
  digitalTwinId: string,
  payload: BulkAssociationsPayload
) {
  return fetch(`${API_BASE}/digital-twins/${digitalTwinId}/associations/bulk`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }).then((res) => {
    if (!res.ok) throw new Error(`Failed to save: ${res.statusText}`);
    return res.json();
  });
}

export async function bulkModifyToolAssociations(
  digitalTwinId: number | string,
  operations: BulkToolOperation[]
) {
  const payload = { operations };

  const res = await fetch(`${API_BASE}/digital-twins/${digitalTwinId}/tools/bulk`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Failed to bulk modify tool associations: ${errText}`);
  }

  return res.json();
}

export async function createGroup(
  digitalTwinId: number,
  data: { title: string; parent_id: number | null; digital_twin_id: number }
) {
  const res = await fetch(`${API_BASE}/digital-twins/${digitalTwinId}/groups`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to create group');
  return await res.json();
}

export async function deleteLayer(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/layers/${id}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to delete layer (${response.status}): ${errorText}`);
  }
}