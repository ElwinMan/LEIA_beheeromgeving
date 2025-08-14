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

// Terrain Provider associations - extending the polymorphic tool association
export interface TerrainProviderAssociation extends ToolAssociation {
  content_type_id: number; // Always points to terrain provider content type
  content_id: number; // Points to actual terrain provider ID
  sort_order: number;
}

// Response from API for terrain provider associations
export interface TerrainProviderAssociationResponse {
  tool_id: number;
  content_type_id: number;
  content_id: number;
  sort_order: number;
}

export interface TerrainProviderWithAssociation extends TerrainProviderAssociation {
  title: string;
  url: string;
  vertexNormals: string;
  isNew: boolean;
}

// Terrain Provider-specific bulk operations
export interface TerrainProviderBulkOperation {
  action: 'create' | 'update' | 'delete';
  tool_id: number;
  content_id: number; // terrain provider ID
  sort_order?: number;
}

export interface BulkTerrainProvidersPayload {
  operations: TerrainProviderBulkOperation[];
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

// Cesium tool configuration for digital twin based on viewer documentation
export interface CesiumConfiguration {
  // Date and time settings
  dateTime?: number; // unix timestamp - determines sun position, default: 1657450800 (10-07-2022 11:00:00)
  
  // Visual quality and rendering
  shadows?: boolean; // shadows enabled/disabled, default: false
  fxaa?: boolean; // FXAA enabled, default: false
  msaa?: number; // MSAA samples, default: 4
  lighting?: boolean; // enable lighting the globe with scene's light source, default: true
  animate?: boolean; // enable animated models, default: false
  resolutionScale?: number; // scaling factor for rendering resolution, default: window.devicePixelRatio
  
  // Level of detail and performance
  maximumScreenSpaceError?: number; // max screen space error for 3D tiles, default: 1.5
  
  // Atmospheric effects
  groundAtmosphere?: boolean; // ground atmosphere enabled, default: true
  fog?: boolean; // fog enabled, default: true
  highDynamicRange?: boolean; // HDR enabled, default: true
  
  // Point cloud settings
  pointCloudAttenuation?: boolean; // point cloud attenuation enabled, default: true
  pointCloudAttenuationMaximum?: number; // maximum point attenuation in pixels, default: 0
  pointCloudAttenuationErrorScale?: number; // scale for geometric error, default: 1
  pointCloudAttenuationBaseResolution?: number; // base resolution in meters, default: 0
  pointCloudEDL?: boolean; // Eye Dome Lighting enabled, default: true
  pointCloudEDLStrength?: number; // Eye dome lighting strength, default: 1
  pointCloudEDLRadius?: number; // thickness of contours from eye dome lighting, default: 1
  
  // Globe settings
  globeOpacity?: number; // opacity percentage of globe, default: 100
  
  // Debug and development
  showMouseCoordinates?: boolean; // debug window showing mouse coordinates, default: false
  showCameraPosition?: boolean; // debug window showing camera position, default: false
  showLoadingWidget?: boolean; // show loading progress bar, default: false
}
