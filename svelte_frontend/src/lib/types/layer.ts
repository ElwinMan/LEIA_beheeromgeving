export interface Layer {
  id: number;
  type: string;
  title: string;
  url: string;
  featureName: string;
  isBackground: boolean;
  content: any;
  last_updated: string;
}
