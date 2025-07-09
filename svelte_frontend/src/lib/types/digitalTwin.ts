import type { Group } from '$lib/types/group';
import type { LayerAssociation } from '$lib/types/digitalTwinAssociation';

export interface DigitalTwin {
  id: number;
  name: string;
  title: string;
  subtitle: string;
  owner: string;
  private: boolean;
  last_updated: Date;
  layer_associations: LayerAssociation[];
  tool_associations: Array<{ tool_id: number }>;
}

// Digital Twin viewer data
export interface DigitalTwinViewerResponse {
  id: number;
  content: ViewerContent;
}

export interface ViewerContent {
  logo: string;
  thumbnail: string;
  startPosition: ViewerStartPosition;
  colors: ViewerColors;
}

export interface ViewerStartPosition {
  x: number;
  y: number;
  z: number;
  heading: number;
  pitch: number;
  duration: number;
}

export interface ViewerColors {
  [key: string]: string;
}
