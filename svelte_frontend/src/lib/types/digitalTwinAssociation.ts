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

// Project associations - extending the polymorphic tool association
export interface ProjectAssociation extends ToolAssociation {
  content_type_id: number; // Always points to project content type
  content_id: number; // Points to actual project ID
  sort_order: number;
  is_default?: boolean; // For marking default project
}

// Response from API for bookmark associations
export interface BookmarkAssociationResponse {
  tool_id: number;
  content_type_id: number;
  content_id: number;
  sort_order: number;
}

// Response from API for project associations
export interface ProjectAssociationResponse {
  tool_id: number;
  content_type_id: number;
  content_id: number;
  sort_order: number;
  is_default?: boolean;
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

export interface ProjectWithAssociation extends ProjectAssociation {
  name: string;
  description?: string;
  content?: {
    polygon?: number[][];
    layers?: string[];
    cameraPosition?: {
      x: number;
      y: number;
      z: number;
      heading: number;
      pitch: number;
      duration: number;
    };
  };
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

// Project-specific bulk operations
export interface ProjectBulkOperation {
  action: 'create' | 'update' | 'delete';
  tool_id: number;
  content_id: number; // project ID
  sort_order?: number;
  is_default?: boolean;
}

// Story associations - extending the polymorphic tool association
export interface StoryAssociation extends ToolAssociation {
  content_type_id: number; // Always points to story content type
  content_id: number; // Points to actual story ID
  sort_order: number;
}

// Response from API for story associations
export interface StoryAssociationResponse {
  tool_id: number;
  content_type_id: number;
  content_id: number;
  sort_order: number;
  is_default?: boolean;
}

export interface StoryWithAssociation extends StoryAssociation {
  name: string;
  description?: string;
  content?: any;
  isNew: boolean;
}

// Story-specific bulk operations
export interface StoryBulkOperation {
  action: 'create' | 'update' | 'delete';
  tool_id: number;
  content_id: number; // story ID
  sort_order?: number;
  is_default?: boolean;
}

export interface BulkStoriesPayload {
  operations: StoryBulkOperation[];
}

export interface BulkBookmarksPayload {
  operations: BookmarkBulkOperation[];
}

export interface BulkProjectsPayload {
  operations: ProjectBulkOperation[];
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
