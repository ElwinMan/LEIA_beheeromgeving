<script lang="ts">
  import { onMount } from 'svelte';
  import {
    fetchDigitalTwin,
    fetchBookmarks,
    fetchDigitalTwinBookmarks,
    bulkUpdateDigitalTwinBookmarks
  } from '$lib/api';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import type { Bookmark } from '$lib/types/tool';
  import type { BookmarkWithAssociation, BookmarkBulkOperation, BookmarkAssociationResponse } from '$lib/types/digitalTwinAssociation';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import DeleteModal from '$lib/components/modals/DeleteModal.svelte';
  import { dragStartAction } from '$lib/utils/dragStartAction';
  import { getDropZone } from '$lib/utils/dropZoneUtils';

  interface Props {
    digitalTwin: DigitalTwin | null;
    digitalTwinId: string;
  }

  let { digitalTwin, digitalTwinId }: Props = $props();

  // Deep clone function
  function deepClone<T>(obj: T): T {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T;
    if (obj instanceof Array) return obj.map((item) => deepClone(item)) as unknown as T;
    if (typeof obj === 'object') {
      const clonedObj = {} as T;
      for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          clonedObj[key] = deepClone(obj[key]);
        }
      }
      return clonedObj;
    }
    return obj;
  }

  // State
  let allBookmarks = $state<Bookmark[]>([]);
  let bookmarksWithDetails = $state<BookmarkWithAssociation[]>([]);
  let hasChanges = $state(false);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let originalData: BookmarkWithAssociation[] = [];
  let isSaving = $state(false);

  // Delete modal state
  let deleteBookmarkModalShow = $state(false);
  let bookmarkToDelete: BookmarkWithAssociation | null = null;
  let skipDeleteBookmarkConfirm = false;

  // Drag and drop state
  let draggedItem = $state<{
    type: 'bookmark' | 'catalog-bookmark';
    id: number;
    bookmark?: Bookmark;
  } | null>(null);
  let draggedOverItem = $state<{
    type: 'bookmark';
    id: number;
    zone: 'top' | 'middle' | 'bottom';
  } | null>(null);

  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;

  // Catalog state
  let catalogBookmarks = $state<Bookmark[]>([]);
  let catalogSearchTerm = $state('');
  let catalogIsLoading = $state(true);
  let catalogError = $state<string | null>(null);

  // Get used bookmark IDs for filtering catalog
  let usedBookmarkIds = $derived(bookmarksWithDetails.map((b) => b.content_id));

  onMount(() => {
    // Restore skipDeleteBookmarkConfirm from sessionStorage if set
    const stored = sessionStorage.getItem('skipDeleteBookmarkConfirm');
    skipDeleteBookmarkConfirm = stored === 'true';
  });

  // Filter catalog bookmarks
  const filteredCatalogBookmarks = $derived.by(() => {
    if (catalogSearchTerm.trim() === '') {
      return catalogBookmarks.filter((bookmark) => !usedBookmarkIds.includes(bookmark.id));
    } else {
      const term = catalogSearchTerm.toLowerCase();
      return catalogBookmarks.filter(
        (bookmark) =>
          !usedBookmarkIds.includes(bookmark.id) &&
          (bookmark.title.toLowerCase().includes(term) ||
            bookmark.description?.toLowerCase().includes(term))
      );
    }
  });

  async function fetchAllData() {
    isLoading = true;
    try {
      digitalTwin = await fetchDigitalTwin(digitalTwinId);
      allBookmarks = await fetchBookmarks();
      
      // Fetch bookmark associations using the new API
      const bookmarkAssociations = await fetchDigitalTwinBookmarks(digitalTwinId);

      if (bookmarkAssociations && bookmarkAssociations.length > 0) {
        bookmarksWithDetails = bookmarkAssociations
          .sort((a: BookmarkAssociationResponse, b: BookmarkAssociationResponse) => a.sort_order - b.sort_order)
          .map((association: BookmarkAssociationResponse) => {
            const bookmarkDetails = allBookmarks.find((bookmark) => bookmark.id === association.content_id);
            return {
              tool_id: association.tool_id,
              content_type_id: association.content_type_id,
              content_id: association.content_id,
              sort_order: association.sort_order, // Use the actual sort_order from API
              title: bookmarkDetails?.title || `Bookmark ${association.content_id}`,
              description: bookmarkDetails?.description || '',
              x: bookmarkDetails?.x || 0,
              y: bookmarkDetails?.y || 0,
              z: bookmarkDetails?.z || 0,
              heading: bookmarkDetails?.heading || 0,
              pitch: bookmarkDetails?.pitch || 0,
              duration: bookmarkDetails?.duration || 0,
              isNew: false
            };
          });

        originalData = deepClone(bookmarksWithDetails);
      } else {
        bookmarksWithDetails = [];
      }

      catalogIsLoading = true;
      catalogBookmarks = allBookmarks;
      catalogIsLoading = false;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error occurred';
    } finally {
      isLoading = false;
    }
  }

  onMount(fetchAllData);

  // Helper function to create bookmark association
  function createBookmarkAssociation(bookmark: Bookmark, sortOrder: number): BookmarkWithAssociation {
    return {
      tool_id: 6, // Bookmark tool ID
      content_type_id: 1, // Bookmark content type ID
      content_id: bookmark.id,
      sort_order: sortOrder,
      title: bookmark.title,
      description: bookmark.description || '',
      x: bookmark.x,
      y: bookmark.y,
      z: bookmark.z,
      heading: bookmark.heading,
      pitch: bookmark.pitch,
      duration: bookmark.duration,
      isNew: true
    };
  }

  function addBookmarkToDigitalTwin(bookmark: Bookmark) {
    // Check if this bookmark was previously deleted
    let wasDeleted = false;
    if ((window as any)._deletedBookmarkIds && Array.isArray((window as any)._deletedBookmarkIds)) {
      const deletedIndex = (window as any)._deletedBookmarkIds.indexOf(bookmark.id);
      if (deletedIndex > -1) {
        // Remove it from the deleted list
        (window as any)._deletedBookmarkIds.splice(deletedIndex, 1);
        wasDeleted = true;
      }
    }

    // Create the bookmark association
    const newBookmarkAssociation = createBookmarkAssociation(bookmark, bookmarksWithDetails.length);
    
    // If it was previously deleted, mark it as an update (not new)
    if (wasDeleted) {
      newBookmarkAssociation.isNew = false;
    }
    
    // Add to the end of the list
    bookmarksWithDetails.push(newBookmarkAssociation);

    // Force reactivity and ensure sort orders are correct
    bookmarksWithDetails = [...bookmarksWithDetails];
    updateBookmarkSortOrders();
    hasChanges = true;
  }

  function handleCatalogAddBookmark(bookmark: Bookmark) {
    addBookmarkToDigitalTwin(bookmark);
  }

  function handleDragOver(e: DragEvent, type: 'bookmark', id: number) {
    e.preventDefault();

    // Try to parse catalog drag data if no draggedItem
    if (!draggedItem) {
      const dragData = e.dataTransfer?.getData('application/json');
      if (dragData) {
        try {
          const parsedData = JSON.parse(dragData);
          if (parsedData.type === 'catalog-bookmark') {
            draggedItem = parsedData;
          }
        } catch (err) {
          if ((window as any).catalogDragData) {
            draggedItem = (window as any).catalogDragData;
          }
        }
      } else if ((window as any).catalogDragData) {
        draggedItem = (window as any).catalogDragData;
      }
    }

    if (!draggedItem) return;

    const zone = getDropZone(e, e.currentTarget as HTMLElement);
    draggedOverItem = { type, id, zone };
  }

  function handleDragLeave() {
    draggedOverItem = null;
  }

  function handleDrop(e: DragEvent, dropType: 'bookmark', dropId: number) {
    e.preventDefault();

    // Try to get drag data if no draggedItem
    if (!draggedItem) {
      const dragData = e.dataTransfer?.getData('application/json');
      if (dragData) {
        try {
          draggedItem = JSON.parse(dragData);
        } catch (err) {
          if ((window as any).catalogDragData) {
            draggedItem = (window as any).catalogDragData;
          }
        }
      } else if ((window as any).catalogDragData) {
        draggedItem = (window as any).catalogDragData;
      }
    }

    if (!draggedItem || !draggedOverItem) return;

    const zone = draggedOverItem.zone;

    if (draggedItem.type === 'catalog-bookmark') {
      handleCatalogBookmarkDrop(dropId, zone);
    } else if (draggedItem.type === 'bookmark') {
      handleBookmarkDrop(dropId, zone);
    }

    draggedItem = null;
    draggedOverItem = null;

    // Clean up global fallback
    if ((window as any).catalogDragData) {
      delete (window as any).catalogDragData;
    }

    hasChanges = true;
  }

  function handleCatalogBookmarkDrop(dropId: number, zone: string) {
    if (!draggedItem || draggedItem.type !== 'catalog-bookmark' || !draggedItem.bookmark) return;

    const bookmark = draggedItem.bookmark;
    
    // Check if this bookmark was previously deleted
    let wasDeleted = false;
    if ((window as any)._deletedBookmarkIds && Array.isArray((window as any)._deletedBookmarkIds)) {
      const deletedIndex = (window as any)._deletedBookmarkIds.indexOf(bookmark.id);
      if (deletedIndex > -1) {
        // Remove it from the deleted list
        (window as any)._deletedBookmarkIds.splice(deletedIndex, 1);
        wasDeleted = true;
      }
    }
    
    // Find the target index for insertion
    const targetIndex = bookmarksWithDetails.findIndex((b) => b.content_id === dropId);
    const insertIndex = zone === 'top' ? targetIndex : targetIndex + 1;
    
    // Create the bookmark association using our helper (sort_order will be updated by updateBookmarkSortOrders)
    const newBookmarkAssociation = createBookmarkAssociation(bookmark, 0);

    // If it was previously deleted, mark it as an update (not new)
    if (wasDeleted) {
      newBookmarkAssociation.isNew = false;
    }

    // Insert at the calculated position
    bookmarksWithDetails.splice(insertIndex, 0, newBookmarkAssociation);
    bookmarksWithDetails = [...bookmarksWithDetails];

    // Update sort orders to reflect the new arrangement
    updateBookmarkSortOrders();
  }

  function handleBookmarkDrop(dropId: number, zone: string) {
    if (!draggedItem || draggedItem.type !== 'bookmark') return;

    const bookmarkId = draggedItem.id;

    // Find the current index of the dragged bookmark
    const currentIndex = bookmarksWithDetails.findIndex((b) => b.content_id === bookmarkId);
    if (currentIndex === -1) return;

    // Find the target index BEFORE removing the item
    const targetIndex = bookmarksWithDetails.findIndex((b) => b.content_id === dropId);
    if (targetIndex === -1) return;

    // Calculate the final insert position
    let insertIndex = zone === 'top' ? targetIndex : targetIndex + 1;

    // If we're moving an item from above the target to below it,
    // we need to adjust for the removal
    if (currentIndex < targetIndex) {
      insertIndex -= 1;
    }

    // Remove the bookmark from its current location
    const bookmark = bookmarksWithDetails.splice(currentIndex, 1)[0];

    // Insert at the calculated position
    bookmarksWithDetails.splice(insertIndex, 0, bookmark);

    updateBookmarkSortOrders();
  }

  function updateBookmarkSortOrders() {
    console.log('updateBookmarkSortOrders - before:', bookmarksWithDetails.map(b => ({ id: b.content_id, sort_order: b.sort_order })));
    
    bookmarksWithDetails.forEach((bookmark, index) => {
      bookmark.sort_order = index;
    });

    // Force reactivity
    bookmarksWithDetails = [...bookmarksWithDetails];
    
    console.log('updateBookmarkSortOrders - after:', bookmarksWithDetails.map(b => ({ id: b.content_id, sort_order: b.sort_order })));
  }

  function getDropIndicatorStyle(type: 'bookmark', id: number) {
    if (!draggedOverItem || draggedOverItem.type !== type || draggedOverItem.id !== id) {
      return { show: false, zone: null };
    }

    return { show: true, zone: draggedOverItem.zone };
  }

  // Save changes to the API
  async function saveChanges() {
    if (!hasChanges) return;

    isSaving = true;
    try {
      const bookmarkOperations: BookmarkBulkOperation[] = [];

      console.log('saveChanges - current bookmarks:', bookmarksWithDetails.map(b => ({ id: b.content_id, sort_order: b.sort_order, isNew: b.isNew })));

      bookmarksWithDetails.forEach((bookmark) => {
        bookmarkOperations.push({
          action: bookmark.isNew ? 'create' : 'update',
          tool_id: bookmark.tool_id,
          content_id: bookmark.content_id,
          sort_order: bookmark.sort_order
        });
      });

      // Add deleted bookmarks
      if ((window as any)._deletedBookmarkIds && Array.isArray((window as any)._deletedBookmarkIds)) {
        console.log('saveChanges - deleted bookmark IDs:', (window as any)._deletedBookmarkIds);
        for (const deletedId of (window as any)._deletedBookmarkIds) {
          bookmarkOperations.push({
            action: 'delete',
            tool_id: 6, // Bookmark tool ID
            content_id: deletedId
          } as BookmarkBulkOperation);
        }
      }

      console.log('saveChanges - operations to send:', bookmarkOperations);

      await bulkUpdateDigitalTwinBookmarks(digitalTwinId, { operations: bookmarkOperations });

      // After successful save, mark all bookmarks as no longer new
      bookmarksWithDetails.forEach((bookmark) => {
        bookmark.isNew = false;
      });

      // Clear deleted bookmark IDs after successful save
      if ((window as any)._deletedBookmarkIds) {
        (window as any)._deletedBookmarkIds = [];
      }

      hasChanges = false;
      originalData = deepClone(bookmarksWithDetails);

      await fetchAllData();
      successBanner?.show();
    } catch (error) {
      console.error('Failed to save changes:', error);
      errorBanner?.show();
    } finally {
      isSaving = false;
    }
  }

  // Reset changes
  function resetChanges() {
    bookmarksWithDetails = deepClone(originalData);
    hasChanges = false;
  }

  function confirmDeleteBookmark(bookmark: BookmarkWithAssociation) {
    bookmarkToDelete = bookmark;
    if (sessionStorage.getItem('skipDeleteBookmarkConfirm') === 'true') {
      actuallyDeleteBookmark(bookmark);
    } else {
      deleteBookmarkModalShow = true;
    }
  }

  async function actuallyDeleteBookmark(bookmark: BookmarkWithAssociation) {
    // Remove from bookmarksWithDetails
    bookmarksWithDetails = bookmarksWithDetails.filter(b => b.content_id !== bookmark.content_id);

    // Track deleted bookmark for bulk API call (only if it's not a new bookmark)
    if (!bookmark.isNew) {
      if (!(window as any)._deletedBookmarkIds) {
        (window as any)._deletedBookmarkIds = [];
      }
      (window as any)._deletedBookmarkIds.push(bookmark.content_id);
    }

    // Update sort orders
    updateBookmarkSortOrders();
    hasChanges = true;
  }

  function handleDeleteBookmarkModalConfirm(detail: { doNotAskAgain: boolean }) {
    if (bookmarkToDelete) {
      actuallyDeleteBookmark(bookmarkToDelete);
      if (detail.doNotAskAgain) {
        skipDeleteBookmarkConfirm = true;
        sessionStorage.setItem('skipDeleteBookmarkConfirm', 'true');
      }
    }
    deleteBookmarkModalShow = false;
    bookmarkToDelete = null;
  }

  function handleDeleteBookmarkModalCancel() {
    deleteBookmarkModalShow = false;
    bookmarkToDelete = null;
  }
</script>

<DeleteModal
  show={deleteBookmarkModalShow}
  title="Bookmark verwijderen"
  message="Weet je zeker dat je deze bookmark wilt verwijderen uit de digital twin?"
  confirmLabel="Verwijder"
  cancelLabel="Annuleer"
  showCheckbox={true}
  checkboxLabel="Niet meer vragen deze sessie"
  onconfirm={handleDeleteBookmarkModalConfirm}
  oncancel={handleDeleteBookmarkModalCancel}
/>

<div class="flex h-full gap-4">
  <!-- Bookmark Catalog -->
  <div class="w-1/3">
    <div class="bg-base-100 border-base-300 h-full rounded-lg border p-4">
      <div class="space-y-4">
        <!-- Header -->
        <div>
          <h3 class="text-lg font-semibold">Bookmark Catalogus</h3>
          <p class="text-base-content/70 text-sm">
            Sleep bookmarks naar de digital twin of klik op + om toe te voegen
          </p>
        </div>

        <!-- Search -->
        <div class="relative">
          <img src="/icons/search.svg" alt="Zoeken" class="text-base-content/50 absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 transform" />
          <input
            type="text"
            placeholder="Zoek bookmarks..."
            class="input input-bordered input-sm w-full pl-10"
            bind:value={catalogSearchTerm}
          />
        </div>

        <!-- Bookmark List -->
        <div class="max-h-96 space-y-1 overflow-y-auto">
          {#if catalogIsLoading}
            <div class="flex items-center justify-center py-8">
              <span class="loading loading-spinner loading-sm"></span>
              <span class="ml-2 text-sm">Laden...</span>
            </div>
          {:else if catalogError}
            <div class="alert alert-error alert-sm">
              <span class="text-sm">{catalogError}</span>
            </div>
          {:else if filteredCatalogBookmarks.length === 0}
            <div class="text-base-content/50 py-8 text-center">
              <img src="/icons/bookmark.svg" alt="Geen bookmarks" class="mx-auto mb-2 h-8 w-8 opacity-50" />
              <p class="text-sm">
                {catalogSearchTerm
                  ? 'Geen bookmarks gevonden voor deze zoekopdracht'
                  : 'Alle beschikbare bookmarks zijn al toegevoegd'}
              </p>
            </div>
          {:else}
            {#each filteredCatalogBookmarks as bookmark}
              <div
                class="hover:bg-base-200 hover:border-base-300 group flex cursor-move items-center gap-2 rounded border border-transparent px-3 py-2 text-sm transition-colors"
                use:dragStartAction={{
                  item: { type: 'catalog-bookmark' as 'catalog-bookmark', id: bookmark.id, bookmark },
                  type: 'catalog-bookmark' as 'catalog-bookmark',
                  dataKey: 'application/json',
                  effectAllowed: 'copy',
                  globalKey: 'catalogDragData',
                  onDragStart: (item) => {
                    draggedItem = item;
                  }
                }}
                draggable="true"
                role="listitem"
              >
                <img src="/icons/bookmark.svg" alt="Bookmark" class="h-4 w-4 flex-shrink-0" />
                <div class="min-w-0 flex-1">
                  <div class="truncate font-medium">{bookmark.title}</div>
                  {#if bookmark.description}
                    <div class="text-base-content/60 truncate text-xs">{bookmark.description}</div>
                  {/if}
                </div>
                <button
                  class="btn btn-ghost btn-xs opacity-0 transition-opacity group-hover:opacity-100 hover:opacity-100"
                  onclick={(e) => {
                    e.stopPropagation();
                    handleCatalogAddBookmark(bookmark);
                  }}
                  onmousedown={(e) => e.stopPropagation()}
                  title="Voeg toe aan digital twin"
                >
                  <img src="/icons/plus.svg" alt="Voeg toe" class="h-3 w-3" />
                </button>
              </div>
            {/each}
          {/if}
        </div>

        <!-- Stats -->
        {#if !catalogIsLoading && !catalogError}
          <div class="text-base-content/50 border-base-300 border-t pt-2 text-xs">
            {filteredCatalogBookmarks.length} beschikbare bookmarks
            {#if usedBookmarkIds.length > 0}
              • {usedBookmarkIds.length} al toegevoegd
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Bookmarks -->
  <div class="flex-1">
    <AlertBanner
      bind:this={successBanner}
      type="success"
      message="Bookmark volgorde succesvol opgeslagen!"
    />
    <AlertBanner
      bind:this={errorBanner}
      type="error"
      message="Fout bij het opslaan van wijzigingen."
    />

    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold">Bookmarks</h2>
          <p class="text-base-content/70 text-sm">
            Sleep bookmarks om ze te herordenen
          </p>
        </div>

        {#if hasChanges}
          <div class="flex gap-2">
            <button class="btn btn-ghost btn-sm" onclick={resetChanges} disabled={isSaving}>
              <img src="/icons/rotate-ccw.svg" alt="Reset" class="h-4 w-4" />
              Reset
            </button>
            <button class="btn btn-primary btn-sm" onclick={saveChanges} disabled={isSaving}>
              {#if isSaving}
                <span class="loading loading-spinner loading-xs"></span>
              {:else}
                <img src="/icons/save.svg" alt="Opslaan" class="h-4 w-4" />
              {/if}
              Opslaan
            </button>
          </div>
        {/if}
      </div>

      <div class="bg-base-100 border-base-300 rounded-lg border p-4">
        <div class="space-y-4 h-[calc(100vh-200px)] overflow-y-auto">
          <div class="space-y-1">
            <!-- Bookmarks List -->
            <div class="mb-4">
              <h3 class="text-base-content/80 mb-2 flex items-center gap-2 text-sm font-semibold">
                <img src="/icons/bookmark.svg" alt="Bookmark" class="h-4 w-4" />
                Bookmarks ({bookmarksWithDetails.length})
              </h3>
              <div class="space-y-1">
                {#each bookmarksWithDetails as bookmark}
                  <div
                    use:dragStartAction={{
                      item: { type: 'bookmark' as 'bookmark', id: bookmark.content_id },
                      type: 'bookmark' as 'bookmark',
                      dataKey: 'application/json',
                      effectAllowed: 'move',
                      onDragStart: (item) => { draggedItem = item; }
                    }}
                    class="relative"
                    draggable="true"
                  >
                    <div
                      class="hover:bg-base-200 flex cursor-move items-center gap-2 rounded px-2 py-1 text-sm {draggedItem?.type ===
                        'bookmark' && draggedItem?.id === bookmark.content_id
                        ? 'opacity-50'
                        : ''}"
                      ondragover={(e) => handleDragOver(e, 'bookmark', bookmark.content_id)}
                      ondragleave={handleDragLeave}
                      ondrop={(e) => handleDrop(e, 'bookmark', bookmark.content_id)}
                      role="listitem"
                    >
                      <img src="/icons/grip-vertical.svg" alt="Grip" class="text-base-content/30 h-4 w-4 flex-shrink-0" />
                      <img src="/icons/bookmark.svg" alt="Bookmark" class="h-4 w-4 flex-shrink-0" />
                      <div class="flex-1 min-w-0">
                        <div class="font-medium truncate">{bookmark.title}</div>
                        {#if bookmark.description}
                          <div class="text-base-content/60 text-xs truncate">{bookmark.description}</div>
                        {/if}
                        <div class="text-base-content/50 text-xs truncate">
                          Position: {bookmark.x.toFixed(2)}, {bookmark.y.toFixed(2)}, {bookmark.z.toFixed(2)}
                        </div>
                      </div>
                      <span class="text-base-content/50 text-xs">#{bookmark.sort_order}</span>
                      <button
                        class="btn btn-ghost btn-xs"
                        onclick={() => confirmDeleteBookmark(bookmark)}
                        title="Verwijder bookmark"
                        aria-label="Verwijder bookmark"
                      >
                        <img src="/icons/trash-2.svg" alt="Verwijder bookmark" class="h-4 w-4" />
                      </button>
                    </div>

                    <!-- Absolute positioned drop indicators -->
                    {#if getDropIndicatorStyle('bookmark', bookmark.content_id).show}
                      {@const indicator = getDropIndicatorStyle('bookmark', bookmark.content_id)}
                      {#if indicator.zone === 'top'}
                        <div
                          class="bg-primary absolute top-0 right-0 left-0 z-10 h-1 -translate-y-0.5 rounded-full"
                        ></div>
                      {:else if indicator.zone === 'bottom'}
                        <div
                          class="bg-primary absolute right-0 bottom-0 left-0 z-10 h-1 translate-y-0.5 rounded-full"
                        ></div>
                      {:else if indicator.zone === 'middle'}
                        <div
                          class="border-primary bg-primary/10 pointer-events-none absolute inset-0 z-10 rounded border-2"
                        ></div>
                      {/if}
                    {/if}
                  </div>
                {/each}
              </div>
            </div>

            {#if bookmarksWithDetails.length === 0}
              <div class="text-base-content/50 py-8 text-center">
                <img src="/icons/bookmark.svg" alt="Geen bookmarks" class="mx-auto mb-2 h-8 w-8 opacity-50" />
                <p>Geen bookmarks gevonden voor deze digital twin.</p>
                <p class="mt-2 text-xs">Sleep bookmarks vanuit de catalogus om te beginnen.</p>
              </div>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
