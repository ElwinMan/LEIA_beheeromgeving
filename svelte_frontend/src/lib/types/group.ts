export interface Group {
  id: number
  title: string
  parent_id: number | null
  sort_order: number
  digital_twin_id: number
}