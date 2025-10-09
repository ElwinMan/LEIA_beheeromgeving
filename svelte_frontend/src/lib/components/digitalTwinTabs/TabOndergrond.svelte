<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchLayers, fetchDigitalTwin, bulkUpdateDigitalTwinAssociations } from '$lib/api';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import type { Layer } from '$lib/types/layer';
  import type { BulkAssociationsPayload, LayerBulkOperation, LayerWithAssociation } from '$lib/types/digitalTwinAssociation';
  import { dragStartAction } from '$lib/utils/dragStartAction';
  import { getDropZone } from '$lib/utils/dropZoneUtils';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import CreateLayerModal from '$lib/components/modals/CreateLayerModal.svelte';
  import EditLayerPropertiesModal from '$lib/components/modals/EditLayerPropertiesModal.svelte';

  interface Props {
    digitalTwin: DigitalTwin | null;
    digitalTwinId: string;
  }

  let { digitalTwin, digitalTwinId }: Props = $props();

  let backgroundLayers = $state<Layer[]>([]);
  let selectedBackgroundLayers = $state<LayerWithAssociation[]>([]);
  let defaultLayerId = $state<number | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let isSaving = $state(false);
  let associatedLayerIds = $state<Set<number>>(new Set());
  let hasChanges = $state(false);
  let originalData: LayerWithAssociation[] = [];
  let originalDefaultLayerId: number | null = null;

  // Export methods for parent component
  export function getHasChanges() {
    return hasChanges;
  }

  export function saveTabChanges() {
    return saveBackgroundLayers();
  }

  export function resetTabChanges() {
    resetChanges();
  }

  // Alert banner refs
  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let createLayerModalRef: InstanceType<typeof CreateLayerModal>;
  let editLayerPropertiesModalRef: InstanceType<typeof EditLayerPropertiesModal>;

  // Simple drag state
  let draggedLayer = $state<Layer | null>(null);
  let draggedFrom = $state<'selected' | 'unselected' | null>(null);
  let dragOverIndex = $state<number | null>(null);
  let dragOverSection = $state<'selected' | 'unselected' | null>(null);
  let dragOverZone = $state<'top' | 'middle' | 'bottom' | null>(null);

  // Derived computed arrays for selected and unselected layers
  let selectedLayers = $derived(selectedBackgroundLayers);
  let unselectedLayers = $derived(
    backgroundLayers.filter(layer => !selectedBackgroundLayers.find(sl => sl.layer_id === layer.id))
  );

  onMount(async () => {
    try {
      const [layers, twin] = await Promise.all([
        fetchLayers(),
        fetchDigitalTwin(digitalTwinId)
      ]);

  // Build associatedLayerIds from the digital twin's layer_associations - only background layers with group_id = null
      associatedLayerIds = new Set<number>(
        (twin.layer_associations ?? [])
          .filter((a: { group_id: number | null; layer_id: number }) => {
            const layer = layers.find((l: Layer) => l.id === a.layer_id);
            return a.group_id === null && layer?.isBackground;
          })
          .map((a: { layer_id: number }) => a.layer_id)
      );

      backgroundLayers = layers.filter((layer: Layer) => layer.isBackground);
      
      // Get selected background layers from associations with sort order
      const layerAssociations = (twin.layer_associations ?? [])
        .filter((a: { group_id: number | null; layer_id: number }) => {
          const layer = layers.find((l: Layer) => l.id === a.layer_id);
          return a.group_id === null && layer?.isBackground;
        })
        .sort((a: { sort_order: number }, b: { sort_order: number }) => a.sort_order - b.sort_order); // Sort by sort_order
      
      selectedBackgroundLayers = layerAssociations.map((assoc: any) => {
        const layer = backgroundLayers.find(layer => layer.id === assoc.layer_id);
        if (!layer) return null;
        
        return {
          layer_id: layer.id,
          is_default: assoc.is_default,
          sort_order: assoc.sort_order,
          group_id: null,
          title: layer.title,
          beschrijving: layer.type || '',
          featureName: layer.featureName || '',
          isNew: false,
          content: assoc.content,
          layerContent: layer.content
        } as LayerWithAssociation;
      }).filter(Boolean); // Remove any undefined layers
      
      defaultLayerId =
        (twin.layer_associations ?? []).find((a: { is_default: boolean; group_id: number | null; layer_id: number }) => {
          const layer = layers.find((l: Layer) => l.id === a.layer_id);
          return a.is_default && a.group_id === null && layer?.isBackground;
        })?.layer_id ?? null;
        
      // Deep clone for change tracking
      originalData = JSON.parse(JSON.stringify(selectedBackgroundLayers));
      originalDefaultLayerId = defaultLayerId;
      hasChanges = false;
    } catch (err) {
      error = 'Fout bij laden van ondergrondlagen.';
      console.error(err);
    } finally {
      loading = false;
    }
  });

  // Simple drag and drop functions
  function handleDragStart(event: DragEvent, layer: Layer, from: 'selected' | 'unselected') {
    if (!event.dataTransfer) return;
    
    draggedLayer = layer;
    draggedFrom = from;
    
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', layer.id.toString());
    
    // Add visual feedback
    const target = event.target as HTMLElement;
    target.classList.add('dragging');
  }

  function handleDragEnd(event: DragEvent) {
    const target = event.target as HTMLElement;
    target.classList.remove('dragging');
    
    draggedLayer = null;
    draggedFrom = null;
    dragOverIndex = null;
    dragOverSection = null;
    dragOverZone = null;
  }

  function handleDragOver(event: DragEvent, section: 'selected' | 'unselected', index?: number) {
    event.preventDefault();
    if (!event.dataTransfer) return;
    
    event.dataTransfer.dropEffect = 'move';
    dragOverSection = section;
    dragOverIndex = index ?? null;
    
    // Calculate drop zone for better visual feedback
    if (event.target instanceof HTMLElement && index !== undefined) {
      dragOverZone = getDropZone(event, event.target);
    } else {
      dragOverZone = null;
    }
  }

  function handleDragLeave() {
    dragOverSection = null;
    dragOverIndex = null;
    dragOverZone = null;
  }

  function handleDrop(event: DragEvent, section: 'selected' | 'unselected', index?: number) {
    event.preventDefault();
    
    if (!draggedLayer || !draggedFrom) return;
    
    if (draggedFrom === 'unselected' && section === 'selected') {
      // Add to selected
      if (index !== undefined) {
        // Calculate the actual insert position based on drop zone
        let insertIndex = index;
        if (dragOverZone === 'bottom') {
          insertIndex = index + 1;
        }
        
        // Insert at specific position
        const layerToAdd = backgroundLayers.find(layer => layer.id === draggedLayer!.id);
        if (layerToAdd) {
          const newAssociation: LayerWithAssociation = {
            layer_id: layerToAdd.id,
            is_default: false,
            sort_order: insertIndex,
            group_id: null,
            title: layerToAdd.title,
            beschrijving: layerToAdd.type || '',
            featureName: layerToAdd.featureName || '',
            isNew: true,
            content: {},
            layerContent: layerToAdd.content
          };
          const newArray = [...selectedBackgroundLayers];
          newArray.splice(insertIndex, 0, newAssociation);
          selectedBackgroundLayers = newArray;
          hasChanges = true;
        }
      } else {
        // Add to end (empty drop zone)
        toggleLayer(draggedLayer.id);
      }
    } else if (draggedFrom === 'selected' && section === 'unselected') {
      // Remove from selected
      toggleLayer(draggedLayer.id);
    } else if (draggedFrom === 'selected' && section === 'selected' && index !== undefined) {
      // Reorder within selected
      const currentIndex = selectedBackgroundLayers.findIndex(l => l.layer_id === draggedLayer!.id);
      if (currentIndex !== -1) {
        let targetIndex = index;
        if (dragOverZone === 'bottom') {
          targetIndex = index + 1;
        } else if (dragOverZone === 'middle') {
          // For middle drops, adjust based on direction
          if (currentIndex < targetIndex) {
            // Moving down: place item below target (target moves up)
            targetIndex = index + 1;
          }
          // Moving up: place item above target (use index as-is)
        }
        
        // Adjust target index if moving down (to account for removal shifting indices)
        if (currentIndex < targetIndex) {
          targetIndex--;
        }
        
        if (currentIndex !== targetIndex) {
          const newArray = [...selectedBackgroundLayers];
          const [movedItem] = newArray.splice(currentIndex, 1);
          newArray.splice(targetIndex, 0, movedItem);
          selectedBackgroundLayers = newArray;
          hasChanges = true;
        }
      }
    }
    
    draggedLayer = null;
    draggedFrom = null;
    dragOverIndex = null;
    dragOverSection = null;
    dragOverZone = null;
  }

  function toggleLayer(layerId: number) {
    const existingIndex = selectedBackgroundLayers.findIndex(layer => layer.layer_id === layerId);
    
    if (existingIndex !== -1) {
      // Remove from selected - using immutable filter
      selectedBackgroundLayers = selectedBackgroundLayers.filter(layer => layer.layer_id !== layerId);
      // Remove from associated set when removing from selection
      associatedLayerIds.delete(layerId);
    } else {
      // Add to selected - using immutable spread
      const layerToAdd = backgroundLayers.find(layer => layer.id === layerId);
      if (layerToAdd) {
        const newAssociation: LayerWithAssociation = {
          layer_id: layerToAdd.id,
          is_default: false,
          sort_order: selectedBackgroundLayers.length,
          group_id: null,
          title: layerToAdd.title,
          beschrijving: layerToAdd.type || '',
          featureName: layerToAdd.featureName || '',
          isNew: true,
          content: {},
          layerContent: layerToAdd.content
        };
        selectedBackgroundLayers = [...selectedBackgroundLayers, newAssociation];
        // Add to associated set when adding to selection
        associatedLayerIds.add(layerId);
      }
    }
    
    hasChanges = true;
  }

  function setDefaultLayer(layerId: number) {
    defaultLayerId = layerId;
    
    // Ensure the layer is selected
    const existingIndex = selectedBackgroundLayers.findIndex(layer => layer.layer_id === layerId);
    if (existingIndex === -1) {
      const layerToAdd = backgroundLayers.find(layer => layer.id === layerId);
      if (layerToAdd) {
        const newAssociation: LayerWithAssociation = {
          layer_id: layerToAdd.id,
          is_default: true,
          sort_order: selectedBackgroundLayers.length,
          group_id: null,
          title: layerToAdd.title,
          beschrijving: layerToAdd.type || '',
          featureName: layerToAdd.featureName || '',
          isNew: true,
          content: {},
          layerContent: layerToAdd.content
        };
        selectedBackgroundLayers = [...selectedBackgroundLayers, newAssociation]; // Trigger reactivity
        // Add to associated set when adding to selection
        associatedLayerIds.add(layerId);
      }
    }
    
    hasChanges = true;
  }

  async function saveBackgroundLayers() {
    if (!hasChanges) return true;

    isSaving = true;
    error = null;
    try {
      const operations: LayerBulkOperation[] = [];

      // Track which layers are currently selected
      const currentSelectedIds = new Set(selectedBackgroundLayers.map(l => l.layer_id));
      
      // Handle selected layers (create/update) with proper sort order
      for (let i = 0; i < selectedBackgroundLayers.length; i++) {
        const layer = selectedBackgroundLayers[i];
        // A layer should be updated if it was already associated in the original data
        const wasOriginallyAssociated = originalData.some((origLayer: LayerWithAssociation) => origLayer.layer_id === layer.layer_id);
        const action = wasOriginallyAssociated ? 'update' : 'create';
        
        operations.push({
          action,
          layer_id: layer.layer_id,
          is_default: layer.layer_id === defaultLayerId,
          sort_order: i, // Use the array index as sort order
          group_id: null,
          content: layer.content
        });
      }

      // Handle deleted layers (layers that were in originalData but not in current selection)
      for (const originalLayer of originalData) {
        if (!currentSelectedIds.has(originalLayer.layer_id)) {
          operations.push({
            action: 'delete',
            layer_id: originalLayer.layer_id,
            is_default: false,
            sort_order: 0,
            group_id: null,
          });
        }
      }

      const payload: BulkAssociationsPayload = {
        layer_payload: { operations },
        group_payload: { operations: [] }
      };

      await bulkUpdateDigitalTwinAssociations(digitalTwinId, payload);
      
      // Update originalData and associatedLayerIds after successful save
      originalData = JSON.parse(JSON.stringify(selectedBackgroundLayers));
      associatedLayerIds = new Set(selectedBackgroundLayers.map(l => l.layer_id));
      hasChanges = false;
      
      // Show success banner
      successBanner?.show();
      return true;
    } catch (err) {
      // Show error banner
      errorBanner?.show();
      console.error('Save error:', err);
      return false;
    } finally {
      isSaving = false;
    }
  }

  // Reset changes
  function resetChanges() {
    selectedBackgroundLayers = JSON.parse(JSON.stringify(originalData));
    defaultLayerId = originalDefaultLayerId;
    hasChanges = false;
  }

  function handleLayerCreated(event: CustomEvent<Layer>) {
    const newLayer = event.detail;
    // Add the new background layer to the available layers
    backgroundLayers = [...backgroundLayers, newLayer];
  }

  function handleEditLayerProperties(layer: LayerWithAssociation) {
    editLayerPropertiesModalRef.show(layer);
  }

  function handleLayerPropertiesSaved(event: CustomEvent<{ layer: LayerWithAssociation; properties: { transparent?: boolean; opacity?: number } }>) {
    const { layer, properties } = event.detail;
    
    // Update the layer's content with the custom properties
    const updatedContent = {
      ...layer.content,
      transparent: properties.transparent,
      opacity: properties.opacity
    };
    
    layer.content = updatedContent;
    
    // Mark as changed to trigger save
    hasChanges = true;
  }

  // Helper function to check if a layer has custom transparency/opacity settings
  function hasCustomSettings(layer: LayerWithAssociation): boolean {
    const content = layer.content || {};
    return content.transparent !== undefined || content.opacity !== undefined;
  }
</script>

<CreateLayerModal
  bind:this={createLayerModalRef}
  on:created={handleLayerCreated}
  isBackgroundPage={true}
/>

<EditLayerPropertiesModal
  bind:this={editLayerPropertiesModalRef}
  on:saved={handleLayerPropertiesSaved}
/>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Ondergrondlagen succesvol opgeslagen!"
/>

<AlertBanner
  bind:this={errorBanner}
  type="error"
  message="Er is een fout opgetreden bij het opslaan van de ondergrondlagen."
/>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h2 class="text-2xl font-bold">Ondergrond</h2>
      <p class="text-base-content/70">Beheer Ondergrond voor deze digital twin.</p>
    </div>
    
    <div class="flex gap-4">
      <!-- Create action - separate group -->
      <button 
        class="btn btn-primary"
        onclick={() => createLayerModalRef.showModal()}
      >
        <img src="/icons/plus.svg" alt="Voeg toe" class="h-4 w-4" />
        Nieuwe Ondergrondlaag
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
        
        <button class="btn btn-primary" onclick={saveBackgroundLayers} disabled={isSaving || !hasChanges}>
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

  {#if loading}
    <div class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if error}
    <div class="alert alert-error">
      <span>{error}</span>
    </div>
  {:else}
    <div class="space-y-6">
      <!-- Selected Background Layers -->
      <div class="card bg-base-100 border-base-300 border">
        <div class="card-body">
          <h3 class="card-title text-success">Geselecteerde Ondergrondlagen ({selectedLayers.length})</h3>
          
          {#if selectedLayers.length === 0}
            <div 
              class="border-2 border-dashed border-base-300 rounded-lg p-8 text-center text-base-content/50 transition-colors hover:border-success min-h-[100px] flex items-center justify-center {dragOverSection === 'selected' ? 'border-success bg-success/10' : ''}"
              role="region"
              aria-label="Drop zone voor geselecteerde ondergrondlagen"
              ondragover={(e) => handleDragOver(e, 'selected')}
              ondragleave={handleDragLeave}
              ondrop={(e) => handleDrop(e, 'selected')}
            >
              <p>Sleep ondergrondlagen hierheen om ze te selecteren</p>
            </div>
          {:else}
            <div 
              class="space-y-2"
              role="list"
              aria-label="Geselecteerde ondergrondlagen lijst met drag en drop functionaliteit"
              ondragover={(e) => {
                // Allow dropping at the end of the list
                if (draggedFrom === 'unselected') {
                  handleDragOver(e, 'selected', selectedLayers.length);
                }
              }}
              ondrop={(e) => {
                if (draggedFrom === 'unselected') {
                  handleDrop(e, 'selected', selectedLayers.length);
                }
              }}
            >
              {#each selectedLayers as layer, index (layer.layer_id)}
                <div 
                  class="flex items-center justify-between p-3 border rounded-lg hover:bg-base-50 transition-colors cursor-move drag-item {draggedLayer?.id === layer.layer_id ? 'opacity-50 scale-98' : ''} {dragOverSection === 'selected' && dragOverIndex === index ? dragOverZone === 'top' ? 'border-t-4 border-t-success' : dragOverZone === 'bottom' ? 'border-b-4 border-b-success' : 'border-success bg-success/10' : ''}"
                  role="button"
                  tabindex="0"
                  aria-label="Verplaatsbare ondergrondlaag: {layer.title}"
                  draggable="true"
                  ondragstart={(e) => {
                    const backgroundLayer = backgroundLayers.find(l => l.id === layer.layer_id);
                    if (backgroundLayer) handleDragStart(e, backgroundLayer, 'selected');
                  }}
                  ondragend={handleDragEnd}
                  ondragover={(e) => handleDragOver(e, 'selected', index)}
                  ondragleave={handleDragLeave}
                  ondrop={(e) => handleDrop(e, 'selected', index)}
                >
                  <div class="flex items-center gap-3">
                    <img src="/icons/grip-vertical.svg" alt="Grip" class="text-base-content/30 h-4 w-4 flex-shrink-0" />
                    <input
                      type="checkbox"
                      checked={true}
                      onchange={() => toggleLayer(layer.layer_id)}
                      class="checkbox checkbox-success"
                    />
                    <span class="font-medium">{layer.title}</span>
                  </div>

                  <div class="flex items-center gap-2">
                    <button
                      class="btn btn-xs"
                      class:btn-primary={hasCustomSettings(layer)}
                      class:btn-ghost={!hasCustomSettings(layer)}
                      onclick={() => handleEditLayerProperties(layer)}
                      title="Bewerk laageigenschappen"
                      aria-label="Bewerk laageigenschappen"
                    >
                      <img src="/icons/settings.svg" alt="Edit" class="w-4 h-4" />
                    </button>
                    <button
                      class="btn btn-sm btn-circle"
                      class:btn-secondary={defaultLayerId === layer.layer_id}
                      class:btn-outline={defaultLayerId !== layer.layer_id}
                      onclick={() => setDefaultLayer(layer.layer_id)}
                      title={defaultLayerId === layer.layer_id ? 'Standaard laag' : 'Instellen als standaard'}
                      aria-label={defaultLayerId === layer.layer_id ? 'Standaard laag' : 'Instellen als standaard'}
                    >
                      <img src="/icons/eye.svg" alt="Eye" class="w-4 h-4" />
                    </button>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>

      <!-- Unselected Background Layers -->
      <div class="card bg-base-100 border-base-300 border">
        <div class="card-body">
          <h3 class="card-title text-base-content/70">Beschikbare Ondergrondlagen ({unselectedLayers.length})</h3>
          
          {#if unselectedLayers.length === 0}
            <div 
              class="border-2 border-dashed border-base-300 rounded-lg p-8 text-center text-base-content/50 transition-colors min-h-[100px] flex items-center justify-center {dragOverSection === 'unselected' ? 'border-base-300 bg-base-100' : ''}"
              role="region"
              aria-label="Drop zone voor beschikbare ondergrondlagen"
              ondragover={(e) => handleDragOver(e, 'unselected')}
              ondragleave={handleDragLeave}
              ondrop={(e) => handleDrop(e, 'unselected')}
            >
              <p>Alle ondergrondlagen zijn geselecteerd</p>
            </div>
          {:else}
            <div class="space-y-2">
              {#each unselectedLayers as layer (layer.id)}
                <div 
                  class="flex items-center justify-between p-3 border rounded-lg hover:bg-base-50 transition-colors cursor-move drag-item {draggedLayer?.id === layer.id ? 'opacity-50 scale-98' : ''}"
                  role="button"
                  tabindex="0"
                  aria-label="Verplaatsbare ondergrondlaag: {layer.title}"
                  draggable="true"
                  ondragstart={(e) => handleDragStart(e, layer, 'unselected')}
                  ondragend={handleDragEnd}
                  ondragover={(e) => handleDragOver(e, 'unselected')}
                  ondragleave={handleDragLeave}
                  ondrop={(e) => handleDrop(e, 'unselected')}
                >
                  <div class="flex items-center gap-3">
                    <img src="/icons/grip-vertical.svg" alt="Grip" class="text-base-content/30 h-4 w-4 flex-shrink-0" />
                    <input
                      type="checkbox"
                      checked={false}
                      onchange={() => toggleLayer(layer.id)}
                      class="checkbox"
                    />
                    <span class="text-base-content/70">{layer.title}</span>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>