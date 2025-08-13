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
  import CreateBookmarkModal from '$lib/components/modals/CreateBookmarkModal.svelte';
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
  let createBookmarkModalRef: InstanceType<typeof CreateBookmarkModal>;

  // Catalog state
  let catalogBookmarks = $state<Bookmark[]>([]);
  let catalogSearchTerm = $state('');
  let catalogIsLoading = $state(true);
  let catalogError = $state<string | null>(null);

  // Get used bookmark IDs for filtering catalog
  let usedBookmarkIds = $derived(bookmarksWithDetails.map((b) => b.content_id));

  onMount(async () => {
    const stored = sessionStorage.getItem('skipDeleteBookmarkConfirm');
    skipDeleteBookmarkConfirm = stored === 'true';
    
    // Load catalog bookmarks first, then load associations
    await loadCatalogBookmarks();
    await loadBookmarks();
  });

  // Filter catalog bookmarks
  let filteredCatalogBookmarks = $derived(
    catalogBookmarks.filter(bookmark => 
      !usedBookmarkIds.includes(bookmark.id) &&
      (catalogSearchTerm === '' || 
       bookmark.title.toLowerCase().includes(catalogSearchTerm.toLowerCase()) ||
       (bookmark.description && bookmark.description.toLowerCase().includes(catalogSearchTerm.toLowerCase()))
      )
    )
  );

  async function loadBookmarks() {
    isLoading = true;
    error = null;
    try {
      // Fetch bookmark associations using the API
      const bookmarkAssociations = await fetchDigitalTwinBookmarks(digitalTwinId);

      if (bookmarkAssociations && bookmarkAssociations.length > 0) {
        bookmarksWithDetails = bookmarkAssociations
          .sort((a: any, b: any) => a.sort_order - b.sort_order)
          .map((association: any) => {
            const bookmarkDetails = allBookmarks.find((bookmark) => bookmark.id === association.content_id);
            return {
              tool_id: association.tool_id,
              content_type_id: association.content_type_id,
              content_id: association.content_id,
              sort_order: association.sort_order,
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
      } else {
        bookmarksWithDetails = [];
      }
      
      originalData = deepClone(bookmarksWithDetails);
      hasChanges = false;
    } catch (err) {
      error = 'Failed to load bookmarks';
      console.error('Error loading bookmarks:', err);
    } finally {
      isLoading = false;
    }
  }

  async function loadCatalogBookmarks() {
    catalogIsLoading = true;
    catalogError = null;
    try {
      const bookmarks = await fetchBookmarks();
      allBookmarks = bookmarks;
      catalogBookmarks = bookmarks;
    } catch (err) {
      catalogError = 'Failed to load bookmark catalog';
      console.error('Error loading catalog bookmarks:', err);
    } finally {
      catalogIsLoading = false;
    }
  }

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

  function handleDragStart(bookmark: Bookmark) {
    draggedItem = { type: 'bookmark', id: bookmark.id, bookmark };
  }

  function handleDragEnd() {
    draggedItem = null;
    draggedOverItem = null;
  }

  function handleDragOver(e: DragEvent, index: number) {
    e.preventDefault();
    if (!draggedItem) return;

    const bookmark = bookmarksWithDetails[index];
    const listItem = (e.currentTarget as HTMLElement);
    const zone = getDropZone(e, listItem);
    draggedOverItem = { type: 'bookmark', id: bookmark.content_id, zone };
  }

  function handleDragLeave() {
    draggedOverItem = null;
  }

  function moveBookmarkInList(fromIndex: number, toIndex: number) {
    const item = bookmarksWithDetails[fromIndex];
    
    // Adjust target index if moving forward (to account for removal shifting indices)
    let adjustedToIndex = toIndex;
    if (fromIndex < toIndex) {
      adjustedToIndex = toIndex - 1;
    }
    
    bookmarksWithDetails.splice(fromIndex, 1);
    bookmarksWithDetails.splice(adjustedToIndex, 0, item);
    
    // Update sort_order for all items
    bookmarksWithDetails.forEach((bookmark, index) => {
      bookmark.sort_order = index;
    });
    
    hasChanges = true;
  }

  function handleDrop(e: DragEvent, targetIndex: number) {
    e.preventDefault();
    
    if (!draggedItem) return;

    const sourceBookmark = draggedItem.bookmark;
    if (!sourceBookmark) return;

    const existingBookmark = allBookmarks.find(b => b.id === sourceBookmark.id);
    if (!existingBookmark) return;

    const zone = draggedOverItem?.zone || 'middle';
    let insertIndex = targetIndex;
    
    // Check if bookmark is already in the list to determine direction
    const existingIndex = bookmarksWithDetails.findIndex(b => b.content_id === sourceBookmark.id);
    
    if (zone === 'bottom') {
      insertIndex = targetIndex + 1;
    } else if (zone === 'middle' && existingIndex !== -1) {
      // For middle drops of existing items, adjust based on direction
      if (existingIndex < targetIndex) {
        // Moving down: place item below target (target moves up)
        insertIndex = targetIndex + 1;
      }
      // Moving up: place item above target (use targetIndex as-is)
    }

    if (existingIndex !== -1 && draggedItem.type === 'bookmark') {
      // Move existing bookmark
      moveBookmarkInList(existingIndex, insertIndex);
    } else if (draggedItem.type === 'catalog-bookmark') {
      // Add new bookmark from catalog
      const newBookmark = createBookmarkAssociation(sourceBookmark, insertIndex);

      bookmarksWithDetails.splice(insertIndex, 0, newBookmark);
      
      // Update sort_order for all items
      bookmarksWithDetails.forEach((bookmark, index) => {
        bookmark.sort_order = index;
      });
      
      hasChanges = true;
    }

    handleDragEnd();
  }

  function handleCatalogDrop(e: DragEvent) {
    e.preventDefault();
    
    const dragData = (window as any).catalogDragData;
    if (!dragData) return;

    const bookmark = dragData as Bookmark;
    const existingBookmark = allBookmarks.find(b => b.id === bookmark.id);
    if (!existingBookmark) return;

    const newBookmark = createBookmarkAssociation(existingBookmark, bookmarksWithDetails.length);

    bookmarksWithDetails.push(newBookmark);
    hasChanges = true;
    
    // Clean up
    delete (window as any).catalogDragData;
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
      const operations: BookmarkBulkOperation[] = [];

      // Handle new bookmarks (create)
      const newBookmarks = bookmarksWithDetails.filter(b => b.isNew);
      for (const bookmark of newBookmarks) {
        operations.push({
          action: 'create',
          tool_id: 6, // Bookmark tool ID
          content_id: bookmark.content_id,
          sort_order: bookmark.sort_order
        });
      }

      // Handle existing bookmarks (update)
      const existingBookmarks = bookmarksWithDetails.filter(b => !b.isNew);
      for (const bookmark of existingBookmarks) {
        const original = originalData.find(o => o.content_id === bookmark.content_id);
        if (original && original.sort_order !== bookmark.sort_order) {
          operations.push({
            action: 'update',
            tool_id: bookmark.tool_id,
            content_id: bookmark.content_id,
            sort_order: bookmark.sort_order
          });
        }
      }

      // Handle deleted bookmarks
      for (const original of originalData) {
        const exists = bookmarksWithDetails.find(b => b.content_id === original.content_id);
        if (!exists) {
          operations.push({
            action: 'delete',
            tool_id: original.tool_id,
            content_id: original.content_id
          });
        }
      }

      if (operations.length > 0) {
        await bulkUpdateDigitalTwinBookmarks(digitalTwinId, { operations });
      }

      // Reload to get fresh data
      await loadBookmarks();
      
      successBanner?.show();
      setTimeout(() => successBanner?.hide(), 3000);
      
    } catch (err) {
      console.error('Failed to save bookmarks:', err);
      errorBanner?.show();
      setTimeout(() => errorBanner?.hide(), 5000);
    } finally {
      isSaving = false;
    }
  }

  // Reset changes
  function resetChanges() {
    bookmarksWithDetails = deepClone(originalData);
    hasChanges = false;
  }

  function showDeleteConfirmation(bookmark: BookmarkWithAssociation) {
    if (skipDeleteBookmarkConfirm) {
      removeBookmark(bookmark);
      return;
    }
    
    bookmarkToDelete = bookmark;
    deleteBookmarkModalShow = true;
  }

  function handleDeleteBookmarkModalCancel() {
    deleteBookmarkModalShow = false;
    bookmarkToDelete = null;
  }

  function handleDeleteBookmarkModalConfirm(detail: { doNotAskAgain: boolean }) {
    if (detail.doNotAskAgain) {
      skipDeleteBookmarkConfirm = true;
      sessionStorage.setItem('skipDeleteBookmarkConfirm', 'true');
    }
    
    if (bookmarkToDelete) {
      removeBookmark(bookmarkToDelete);
    }
    deleteBookmarkModalShow = false;
    bookmarkToDelete = null;
  }

  function removeBookmark(bookmark: BookmarkWithAssociation) {
    const index = bookmarksWithDetails.findIndex(b => b.content_id === bookmark.content_id);
    if (index > -1) {
      bookmarksWithDetails.splice(index, 1);
      
      // Update sort_order for remaining items
      bookmarksWithDetails.forEach((bmark, idx) => {
        bmark.sort_order = idx;
      });
      
      hasChanges = true;
    }
  }

  function handleBookmarkCreated(event: CustomEvent<Bookmark>) {
    const newBookmark = event.detail;
    loadCatalogBookmarks(); // Refresh catalog
    
    // Optionally add to current list
    const bookmarkWithAssociation = createBookmarkAssociation(newBookmark, bookmarksWithDetails.length);
    
    bookmarksWithDetails.push(bookmarkWithAssociation);
    hasChanges = true;
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

<CreateBookmarkModal
  bind:this={createBookmarkModalRef}
  on:created={handleBookmarkCreated}
/>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Bookmarks succesvol opgeslagen!"
/>

<AlertBanner
  bind:this={errorBanner}
  type="error"
  message="Er is een fout opgetreden bij het opslaan van de bookmarks."
/>

<div class="flex h-full gap-4">
  <!-- Main content -->
  <div class="flex-1 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold">Bookmarks</h2>
        <p class="text-base-content/70">Beheer bookmarks voor deze digital twin.</p>
      </div>
      
      <div class="flex gap-4">
        <!-- Create action - separate group -->
        <button 
          class="btn btn-primary"
          onclick={() => createBookmarkModalRef.showModal()}
        >
          <img src="/icons/plus.svg" alt="Voeg toe" class="h-4 w-4" />
          Nieuwe Bookmark
        </button>
        
        <!-- Save/Reset actions - grouped together -->
        <div class="flex gap-2">
          {#if hasChanges}
            <button class="btn btn-ghost" onclick={resetChanges}>
              <img src="/icons/rotate-ccw.svg" alt="Reset" class="h-4 w-4" />
              Reset
            </button>
          {:else}
            <div class="btn btn-ghost invisible">
              <img src="/icons/rotate-ccw.svg" alt="Reset" class="h-4 w-4" />
              Reset
            </div>
          {/if}
          
          <button class="btn btn-primary" onclick={saveChanges} disabled={isSaving || !hasChanges}>
            {#if isSaving}
              <span class="loading loading-spinner loading-xs"></span>
            {:else}
              <img src="/icons/save.svg" alt="Opslaan" class="h-4 w-4" />
            {/if}
            Opslaan
          </button>
        </div>
      </div>
    </div>

    {#if isLoading}
      <div class="flex justify-center py-8">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
    {:else if error}
      <div class="alert alert-error">
        <span>{error}</span>
      </div>
    {:else}
      <div class="card bg-base-100 border-base-300 border">
        <div class="card-body">
          <h3 class="card-title">Actieve Bookmarks</h3>
          
          {#if bookmarksWithDetails.length === 0}
            <div 
              class="border-2 border-dashed border-base-300 rounded-lg p-8 text-center text-base-content/50 transition-colors {draggedItem?.type === 'catalog-bookmark' ? 'border-primary bg-primary/5' : ''}"
              role="region"
              ondragover={(e) => {
                e.preventDefault();
                // Try to set draggedItem from catalog data if not already set
                if (!draggedItem && (window as any).catalogDragData) {
                  const catalogData = (window as any).catalogDragData;
                  draggedItem = { type: 'catalog-bookmark', id: catalogData.id, bookmark: catalogData };
                }
              }}
              ondrop={handleCatalogDrop}
            >
              <p>Geen bookmarks gevonden. Sleep een bookmark hierheen uit de catalogus.</p>
            </div>
          {:else}
            <div class="space-y-2">
              {#each bookmarksWithDetails as bookmark, index (bookmark.content_id)}
                <div class="relative">
                  <div 
                    class="flex items-center gap-3 p-3 border border-base-300 rounded-lg hover:bg-base-50 transition-colors {draggedItem?.type === 'bookmark' && draggedItem?.id === bookmark.content_id ? 'opacity-50' : ''}"
                    draggable="true"
                    role="listitem"
                    ondragstart={() => {
                      const foundBookmark = allBookmarks.find(b => b.id === bookmark.content_id);
                      if (foundBookmark) handleDragStart(foundBookmark);
                    }}
                    ondragend={handleDragEnd}
                    ondragover={(e) => handleDragOver(e, index)}
                    ondragleave={handleDragLeave}
                    ondrop={(e) => handleDrop(e, index)}
                  >
                    <!-- Drag handle -->
                    <div class="cursor-move text-base-content/40">
                      <img src="/icons/grip-vertical.svg" alt="Grip" class="text-base-content/30 h-4 w-4 flex-shrink-0" />
                    </div>

                    <!-- Bookmark icon -->
                    <img src="/icons/bookmark.svg" alt="Bookmark" class="h-5 w-5 flex-shrink-0 text-blue-600" />

                    <!-- Bookmark info -->
                    <div class="flex-1">
                      <div class="flex items-center gap-2">
                        <div class="font-medium">{bookmark.title}</div>
                        {#if bookmark.isNew}
                          <span class="badge badge-primary badge-sm">nieuw</span>
                        {/if}
                      </div>
                      {#if bookmark.description}
                        <div class="text-sm text-base-content/70">{bookmark.description}</div>
                      {/if}
                      <div class="text-xs text-base-content/50">
                        Position: {bookmark.x.toFixed(2)}, {bookmark.y.toFixed(2)}, {bookmark.z.toFixed(2)}
                      </div>
                    </div>

                    <!-- Sort order -->
                    <span class="text-base-content/50 text-xs">#{bookmark.sort_order}</span>

                    <!-- Actions -->
                    <div class="flex gap-2">
                      <button 
                        class="btn btn-ghost btn-xs text-error hover:bg-error/10"
                        onclick={() => showDeleteConfirmation(bookmark)}
                        title="Bookmark verwijderen"
                        aria-label="Bookmark verwijderen"
                      >
                        <img src="/icons/trash-2.svg" alt="Verwijder" class="h-5 w-5" />
                      </button>
                    </div>
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
          {/if}
        </div>
      </div>
    {/if}
  </div>

  <!-- Catalog sidebar -->
  <div class="w-80 space-y-4">
    <div class="card bg-base-100 border-base-300 border">
      <div class="card-body">
        <h3 class="card-title">Bookmark Catalogus</h3>
        
        <!-- Search -->
        <input 
          class="input input-bordered input-sm w-full" 
          placeholder="Zoek bookmarks..."
          bind:value={catalogSearchTerm}
        />

        {#if catalogIsLoading}
          <div class="flex justify-center py-4">
            <span class="loading loading-spinner"></span>
          </div>
        {:else if catalogError}
          <div class="alert alert-error alert-sm">
            <span>{catalogError}</span>
          </div>
        {:else}
          <div class="space-y-2 max-h-96 overflow-y-auto">
            {#each filteredCatalogBookmarks as bookmark (bookmark.id)}
              <div 
                class="p-2 border border-base-300 rounded cursor-move hover:bg-base-50 transition-colors"
                draggable="true"
                use:dragStartAction={{
                  item: bookmark,
                  type: 'bookmark',
                  globalKey: 'catalogDragData',
                  onDragStart: (catalogBookmark) => {
                    draggedItem = { type: 'catalog-bookmark', id: catalogBookmark.id, bookmark: catalogBookmark };
                  }
                }}
              >
                <div class="font-medium text-sm">{bookmark.title}</div>
                {#if bookmark.description}
                  <div class="text-xs text-base-content/70">{bookmark.description}</div>
                {/if}
                <div class="text-xs text-base-content/50">
                  Position: {bookmark.x.toFixed(2)}, {bookmark.y.toFixed(2)}, {bookmark.z.toFixed(2)}
                </div>
              </div>
            {:else}
              <div class="text-center py-4 text-base-content/50">
                <p>Geen bookmarks beschikbaar</p>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>
