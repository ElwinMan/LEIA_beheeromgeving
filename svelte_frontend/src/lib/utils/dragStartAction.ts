export function dragStartAction<T extends object>(
  node: HTMLElement,
  params: {
    item: T;
    type: string;
    dataKey?: string; // e.g. 'application/json'
    effectAllowed?: DataTransfer['effectAllowed'];
    globalKey?: string; // e.g. 'catalogDragData'
    onDragStart?: (item: T) => void;
  }
) {
  let currentParams = params;

  function handleDragStart(e: DragEvent) {
    // Use the current params to get the latest item data
    const currentItem = currentParams.item;
    
    if (e.dataTransfer) {
      e.dataTransfer.effectAllowed = currentParams.effectAllowed ?? 'move';
      if (currentParams.dataKey) {
        e.dataTransfer.setData(currentParams.dataKey, JSON.stringify(currentItem));
      }
      // For Firefox compatibility
      e.dataTransfer.setData('text/plain', '');
    }
    if (currentParams.globalKey) {
      (window as any)[currentParams.globalKey] = currentItem;
    }
    if (currentParams.onDragStart) {
      currentParams.onDragStart(currentItem);
    }
  }

  node.addEventListener('dragstart', handleDragStart);

  return {
    update(newParams: typeof params) {
      currentParams = newParams;
    },
    destroy() {
      node.removeEventListener('dragstart', handleDragStart);
    }
  };
}