import type { Group } from '$lib/types/group';

export interface LayerAssociation {
  layer_id: number
  is_default: boolean
  sort_order: number
  group_id: number | null
}

export interface LayerWithAssociation extends LayerAssociation {
  title: string
  beschrijving: string
  featureName: string
  isNew: boolean
}

export interface GroupWithLayers extends Group {
  layers: LayerWithAssociation[]
  subgroups: GroupWithLayers[]
  depth: number
}

export interface ToolAssociation {
  tool_id: number;
}

// Bulk operations for associated tools
export interface BulkToolPayload {
  operations: BulkToolOperation[];
}

export interface BulkToolOperation {
  tool_id: number;
  action: "create" | "delete";
}

// Bulk operations for association layers and groups
export interface BulkAssociationsPayload {
  layer_payload: { operations: LayerBulkOperation[] };
  group_payload: { operations: GroupBulkOperation[] };
}

export interface LayerBulkOperation {
  action: 'create' | 'update' | 'delete';
  layer_id: number;
  is_default?: boolean;
  sort_order?: number | null;
  group_id?: number | null;
}

export interface GroupBulkOperation extends Group {
  action: 'create' | 'update' | 'delete';
}