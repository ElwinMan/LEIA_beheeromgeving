/**
 * Determines the drop zone based on the mouse position within an element
 * @param e - The drag event
 * @param element - The HTML element being dragged over
 * @returns The drop zone: 'top', 'middle', or 'bottom'
 */
export function getDropZone(e: DragEvent, element: HTMLElement): 'top' | 'middle' | 'bottom' {
  const rect = element.getBoundingClientRect();
  const y = e.clientY - rect.top;
  const height = rect.height;

  const topThreshold = height * 0.35;
  const bottomThreshold = height * 0.65;

  if (y < topThreshold) return 'top';
  if (y > bottomThreshold) return 'bottom';
  return 'middle';
}
