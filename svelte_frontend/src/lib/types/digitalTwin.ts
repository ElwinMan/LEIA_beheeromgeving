export interface LayerAssociation {
  layer_id: number
  is_default: boolean
  sort_order: number
  group_id: number | null
}

export interface Layer {
  id: number
  type: string
  title: string
  url: string
  featureName: string
  isBackground: boolean
  content: any
}

export interface Group {
  id: number
  title: string
  parent_id: number | null
  sort_order: number
  digital_twin_id: number
}

export interface LayerWithAssociation extends LayerAssociation {
  title: string
  beschrijving: string
  featureName: string
}

export interface GroupWithLayers extends Group {
  layers: LayerWithAssociation[]
  subgroups: GroupWithLayers[]
  depth: number
}

export interface DigitalTwin {
  id: number
  name: string
  title: string
  subtitle: string
  owner: string
  private: boolean
  last_updated: Date
  layer_associations: LayerAssociation[]
  tool_associations: Array<{ tool_id: number }>
}

export interface LayerBulkOperation {
  action: 'create' | 'update' | 'delete';
  layer_id: number;
  is_default?: boolean;
  sort_order?: number | null;
  group_id?: number | null;
}

export interface GroupBulkOperation extends Group {
  action: 'create' | 'update' | 'delete';
}

export interface BulkAssociationsPayload {
  layer_payload: { operations: LayerBulkOperation[] };
  group_payload: { operations: GroupBulkOperation[] };
}