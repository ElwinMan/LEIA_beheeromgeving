export interface Tool {
  id: number;
  name: string;
  description: string;
  content?: any;
  last_updated: string;
}

// Content Type for polymorphic relationships
export interface ContentType {
  id: number;
  name: string;
  table_name: string;
}

// Bookmarks
export interface Bookmark {
  id: number;
  title: string;
  description?: string;
  x: number;
  y: number;
  z: number;
  heading: number;
  pitch: number;
  duration: number;
  last_updated: string;
}

// Projects
export interface Project {
  id: number;
  name: string;
  description?: string;
  content?: any;
  last_updated: string;
}

// Terrain Provider
export interface TerrainProvider {
  id: number;
  title: string;
  url: string;
  vertexNormals?: string;
  last_updated: string;
}

// Story
export interface Story {
  id: number;
  name: string;
  description?: string;
  content?: any;
  last_updated: string;
}

// Story reusable types
export interface RequiredLayer {
  id: string;
  title: string;
  transparent: boolean;
  opacity?: number;  // Only present when transparency is enabled
  style?: string;    // Only present when style has a meaningful value
}

export interface StoryStep {
  title: string;
  html: string;
  globeOpacity: number;
  terrain: string;
  camera: {
    x: number;
    y: number;
    z: number;
    heading: number;
    pitch: number;
    duration: number;
  };
  layers: string[];
  requiredLayers: RequiredLayer[];
  _activeTab?: number;
}

export interface StoryChapter {
  id: string;
  title: string;
  buttonText: string;
  steps: StoryStep[];
}
