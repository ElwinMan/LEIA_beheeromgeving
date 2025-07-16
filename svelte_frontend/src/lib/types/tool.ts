export interface Tool {
  id: number;
  name: string;
  content: any;
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

// Cesium
export interface Cesium {
  id: number;
  url: string;
  vertexNormals?: string;
  content?: any;
}

// Story
export interface Story {
  id: number;
  name: string;
  description?: string;
  content?: any;
}
