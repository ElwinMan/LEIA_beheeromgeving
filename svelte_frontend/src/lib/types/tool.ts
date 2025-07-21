export interface Tool {
  id: number;
  name: string;
  content?: any;
}

// Bookmarks
export interface Bookmark {
  id: number;
  title: string;
  description?: string;
  content?: any;
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
