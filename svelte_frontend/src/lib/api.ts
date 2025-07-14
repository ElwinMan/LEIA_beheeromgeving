const API_BASE = import.meta.env.VITE_API_BASE_URL;
import type { DigitalTwin, DigitalTwinViewerResponse, ViewerContent, CreateDigitalTwinInput } from '$lib/types/digitalTwin';
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

export async function createDigitalTwin(data: CreateDigitalTwinInput): Promise<DigitalTwin> {
  const response = await fetch(`${API_BASE}/digital-twins/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error('Failed to create digital twin');
  }

  const result = await response.json();
  return {
    ...result,
    last_updated: new Date(result.last_updated)
  };
}

export async function createViewer(digitalTwinId: number) {
  const payload = {
    digital_twin_id: digitalTwinId,
    content: {
      logo: "",
      thumbnail: "",
      startPosition: {
        x: 3.62121,
        y: 51.45503,
        z: 3096.9614,
        heading: 360,
        pitch: -34.77193,
        duration: 1.5
      },
      colors: {
        "ui-background": "#ffffff",
        "interactive-01": "#214170",
        "interactive-02": "#171717",
        "interactive-03": "#0062ff",
        "interactive-04": "#0062ff",
        "ui-01": "#f3f3f3",
        "ui-02": "#ffffff",
        "ui-03": "#dcdcdc",
        "ui-04": "#8c8c8c",
        "ui-05": "#171717",
        "text-01": "#171717",
        "text-02": "#565656",
        "text-03": "#8c8c8c",
        "text-04": "#ffffff",
        "link-01": "#0062ff",
        "icon-01": "#171717",
        "icon-02": "#565656",
        "icon-03": "#ffffff",
        "field-01": "#f3f3f3",
        "field-02": "#ffffff",
        "inverse-01": "#ffffff",
        "inverse-02": "#3d3d3d",
        "support-01": "#da1e28",
        "support-02": "#24a148",
        "support-03": "#fdd13a",
        "support-04": "#054ada",
        "inverse-support-01": "#fb4b53",
        "inverse-support-02": "#3dbb61",
        "inverse-support-03": "#fdd13a",
        "inverse-support-04": "#408bfc",
        "overlay-01": "#171717CC",
        "interaction-tokens": "#0062ff",
        "hover-primary": "#376dbc",
        "hover-primary-text": "#054ada",
        "hover-secondary": "#4c4c4c",
        "hover-tertiary": "#4cabd8",
        "hover-ui": "#e5e5e5",
        "hover-selected-ui": "#cacaca",
        "hover-danger": "#ba1b23",
        "hover-row": "#e5e5e5",
        "active-primary": "#376dbc",
        "active-secondary": "#6f6f6f",
        "active-tertiary": "#0530ad",
        "active-ui": "#bebebe",
        "active-danger": "#750e13",
        "selected-ui": "#dcdcdc",
        "highlight": "#C9deff",
        "skeleton-01": "#e5e5e5",
        "skeleton-02": "#bebebe",
        "visited-link": "#0062ff",
        "disabled-01": "#f3f3f3",
        "disabled-02": "#bebebe",
        "disabled-03": "#8c8c8c"
      }
    }
  };

  const response = await fetch(`${API_BASE}/digital-twins/${digitalTwinId}/viewer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error('Failed to create viewer');
  }

  return await response.json();
}

export async function createLayer(data: {
  title: string;
  type: string;
  url: string;
  featureName?: string;
  isBackground: boolean;
}) {
  const res = await fetch(`${API_BASE}/layers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Failed to create layer: ${errText}`);
  }

  return res.json();
}

export function digitalTwinExport(digitalTwinId: number | string): string {
  return `${API_BASE}/digital-twins/${digitalTwinId}/export/download.json`;
}