import type { Group } from '$lib/types/group';

export interface LayerAssociation {
  layer_id: number;
  is_default: boolean;
  sort_order: number;
  group_id: number | null;
}

export interface LayerWithAssociation extends LayerAssociation {
  title: string;
  beschrijving: string;
  featureName: string;
  isNew: boolean;
}

export interface GroupWithLayers extends Group {
  layers: LayerWithAssociation[];
  subgroups: GroupWithLayers[];
  depth: number;
}

export interface ToolAssociation {
  tool_id: number;
}

// Bookmark associations - extending the polymorphic tool association
export interface BookmarkAssociation extends ToolAssociation {
  content_type_id: number; // Always points to bookmark content type
  content_id: number; // Points to actual bookmark ID
  sort_order: number;
}

// Response from API for bookmark associations
export interface BookmarkAssociationResponse {
  tool_id: number;
  content_type_id: number;
  content_id: number;
  sort_order: number;
}

export interface BookmarkWithAssociation extends BookmarkAssociation {
  title: string;
  description?: string;
  x: number;
  y: number;
  z: number;
  heading: number;
  pitch: number;
  duration: number;
  isNew: boolean;
}

// Bulk operations for associated tools
export interface BulkToolPayload {
  operations: BulkToolOperation[];
}

export interface BulkToolOperation {
  tool_id: number;
  content_type_id?: number;
  content_id?: number;
  sort_order?: number;
  action: 'create' | 'update' | 'delete';
}

// Bookmark-specific bulk operations
export interface BookmarkBulkOperation {
  action: 'create' | 'update' | 'delete';
  tool_id: number;
  content_id: number; // bookmark ID
  sort_order?: number;
}

export interface BulkBookmarksPayload {
  operations: BookmarkBulkOperation[];
}

// Bulk operations for association layers and groups
export interface BulkAssociationsPayload {
  layer_payload: { operations: LayerBulkOperation[] };
  group_payload: { operations: GroupBulkOperation[] };
}

export interface LayerBulkOperation extends LayerAssociation {
  action: 'create' | 'update' | 'delete';
}

export interface GroupBulkOperation extends Group {
  action: 'create' | 'update' | 'delete';
}
