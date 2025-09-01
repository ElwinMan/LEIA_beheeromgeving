import type { LayerAssociation } from '$lib/types/digitalTwinAssociation';

export interface DigitalTwin {
  id: number;
  name: string;
  title: string;
  subtitle: string;
  owner: string;
  isPrivate: boolean;
  last_updated: string;
  layer_associations: LayerAssociation[];
  tool_associations: Array<{ 
    tool_id: number;
    content?: Record<string, any>;
  }>;
}

export interface CreateDigitalTwinInput {
  name: string;
  title: string;
  subtitle: string;
  owner: string;
  isPrivate: boolean;
  last_updated: string;
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
