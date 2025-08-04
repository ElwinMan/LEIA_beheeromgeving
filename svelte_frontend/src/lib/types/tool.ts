export interface Tool {
  id: number;
  name: string;
  content?: any;
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
}

// Projects
export interface Project {
  id: number;
  name: string;
  description?: string;
  content?: any;
}

// Terrain Provider
export interface TerrainProvider {
  id: number;
  title: string;
  url: string;
  vertexNormals?: string;
}

// Story
export interface Story {
  id: number;
  name: string;
  description?: string;
  content?: any;
}
