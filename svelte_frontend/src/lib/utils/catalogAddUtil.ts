export function addCatalogItemToList<TCatalog, TAssoc>(
  item: TCatalog,
  groupId: number | null,
  ungroupedList: TAssoc[],
  rootGroups: any[],
  findGroupById: (groups: any[], id: number) => any,
  mapToAssociation: (item: TCatalog, groupId: number | null, sortOrder: number) => TAssoc
): TAssoc {
  // Determine sort order
  let sortOrder = groupId === null
    ? ungroupedList.length
    : (() => {
        const group = findGroupById(rootGroups, groupId);
        return group ? group.layers.length : 0;
      })();

  // Create association object
  const assoc = mapToAssociation(item, groupId, sortOrder);

  if (groupId === null) {
    ungroupedList.push(assoc);
  }

  return assoc;
}