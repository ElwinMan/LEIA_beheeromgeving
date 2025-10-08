<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { LayerWithAssociation } from '$lib/types/digitalTwinAssociation';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';
  import AlertBanner from '$lib/components/AlertBanner.svelte';

  const dispatch = createEventDispatcher<{
    saved: {
      layer: LayerWithAssociation;
      properties: {
        disablePopup?: boolean;
        transparent?: boolean;
        opacity?: number;
      };
    };
  }>();

  let modalRef: HTMLDialogElement;
  let currentLayer: LayerWithAssociation | null = null;

  // Form fields
  let disablePopup = false;
  let transparent = false;
  let opacity = 100;
  let useCustomSettings = false;
  let isSaving = false; // Add saving state

  // Alert banners
  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;

  export function show(layer: LayerWithAssociation) {
    currentLayer = layer;
    
    // Initialize form with current values
    // Check if there are custom settings in the association content
    const associationContent = layer.content || {};
    const layerContent = layer.layerContent || {};
    
    // Determine if we have custom settings
    useCustomSettings = associationContent.disablePopup !== undefined || 
                       associationContent.transparent !== undefined || 
                       associationContent.opacity !== undefined;
    
    if (useCustomSettings) {
      // Use custom settings from association
      disablePopup = associationContent.disablePopup ?? false;
      transparent = associationContent.transparent ?? false;
      opacity = associationContent.opacity ?? 100;
    } else {
      // Use default settings from layer
      disablePopup = layerContent.disablePopup ?? false;
      transparent = layerContent.transparent ?? false;
      opacity = layerContent.opacity ?? 100;
    }
    
    modalRef?.showModal();
  }

  function resetModal() {
    currentLayer = null;
    disablePopup = false;
    transparent = false;
    opacity = 100;
    useCustomSettings = false;
    isSaving = false; // Reset saving state
    successBanner?.hide?.();
    errorBanner?.hide?.();
  }

  function handleSave() {
    if (!currentLayer || isSaving) return; // Prevent multiple saves
    
    isSaving = true; // Set saving state immediately

    try {
      const properties: { disablePopup?: boolean; transparent?: boolean; opacity?: number } = {};
      
      if (useCustomSettings) {
        properties.disablePopup = disablePopup;
        properties.transparent = transparent;
        properties.opacity = Number(opacity);
      }

      dispatch('saved', {
        layer: currentLayer,
        properties
      });

      successBanner?.show();
      
      // Close modal immediately after successful dispatch
      setTimeout(() => {
        modalRef?.close();
        resetModal();
      }, 300); // Reduced from 1500ms to 300ms
    } catch (error) {
      console.error('Failed to save layer properties:', error);
      errorBanner?.show();
      isSaving = false; // Reset saving state on error
    }
  }

  function handleCancel() {
    modalRef?.close();
    resetModal();
  }

  function toggleCustomSettings() {
    useCustomSettings = !useCustomSettings;
    
    if (!useCustomSettings) {
      // Reset to layer defaults when disabling custom settings
      const layerContent = currentLayer?.layerContent || {};
      disablePopup = layerContent.disablePopup ?? false;
      transparent = layerContent.transparent ?? false;
      opacity = layerContent.opacity ?? 100;
    }
  }

  function validateOpacity() {
    if (opacity > 100) opacity = 100;
    if (opacity < 0) opacity = 0;
  }
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Layer eigenschappen opgeslagen!"
/>

<AlertBanner
  bind:this={errorBanner}
  type="error"
  message="Fout bij het opslaan van layer eigenschappen!"
/>

<dialog bind:this={modalRef} class="modal">
  <form method="dialog" class="modal-box w-full max-w-2xl">
    <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2" onclick={handleCancel}>✕</button>
    
    <h3 class="text-lg font-bold mb-4">
      Layer Eigenschappen: {currentLayer?.title || 'Onbekende Layer'}
    </h3>

    <div class="space-y-6">
      <!-- Custom Settings Toggle -->
      <div class="form-control">
        <label class="label cursor-pointer justify-start gap-3">
          <input 
            type="checkbox" 
            class="checkbox checkbox-primary" 
            checked={useCustomSettings}
            onchange={toggleCustomSettings}
          />
          <div class="flex items-center gap-2">
            <span class="label-text font-semibold">Aangepaste instellingen gebruiken</span>
            <HelpTooltip tip="Schakel in om de standaard transparantie en ondoorzichtigheid van deze layer te overschrijven voor deze digital twin." />
          </div>
        </label>
      </div>

      {#if !useCustomSettings}
        <!-- Show current layer defaults when not using custom settings -->
        <div class="bg-base-200 p-4 rounded-lg">
          <h4 class="font-semibold mb-2">Huidige Layer Standaarden:</h4>
          <div class="space-y-2 text-sm">
            <div>
              <span class="font-medium">Disable Popup:</span> 
              {currentLayer?.layerContent?.disablePopup ? 'Ja' : 'Nee'}
            </div>
            <div>
              <span class="font-medium">Transparant:</span> 
              {currentLayer?.layerContent?.transparent ? 'Ja' : 'Nee'}
            </div>
            <div>
              <span class="font-medium">Opacity:</span> 
              {currentLayer?.layerContent?.opacity ?? 100}%
            </div>
          </div>
        </div>
      {:else}
        <!-- Custom settings form -->
        <div class="space-y-4">
          <div class="form-control">
            <label class="label cursor-pointer justify-start gap-3">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={disablePopup}
              />
              <div class="flex items-center gap-2">
                <span class="label-text font-semibold">Disable Popup</span>
                <HelpTooltip tip="Schakel in om feature info popups voor deze layer uit te schakelen." />
              </div>
            </label>
          </div>

          <div class="form-control">
            <label class="label cursor-pointer justify-start gap-3">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={transparent}
              />
              <div class="flex items-center gap-2">
                <span class="label-text font-semibold">Transparant</span>
                <HelpTooltip tip="Maakt de layer transparant zodat onderliggende lagen zichtbaar blijven." />
              </div>
            </label>
          </div>

          <div class="form-control">
            <label class="label" for="opacity">
              <div class="flex items-center gap-2">
                <span class="label-text font-semibold">Opacity</span>
                <HelpTooltip tip="Bepaalt hoe ondoorzichtig de layer is (0-100%). Lagere waarden maken de layer transparanter." />
              </div>
            </label>
            <input 
              id="opacity"
              type="number" 
              min="0" 
              max="100" 
              step="1" 
              class="input input-bordered w-full" 
              bind:value={opacity}
              oninput={validateOpacity}
              disabled={!transparent}
              placeholder="0-100"
            />
          </div>

          {#if !transparent}
            <div class="text-sm text-gray-500 italic">
              Ondoorzichtigheid is alleen beschikbaar wanneer transparantie is ingeschakeld.
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <div class="modal-action">
      <button type="button" class="btn btn-ghost" onclick={handleCancel} disabled={isSaving}>
        Annuleren
      </button>
      <button type="button" class="btn btn-primary" onclick={handleSave} disabled={isSaving}>
        {#if isSaving}
          <span class="loading loading-spinner loading-xs"></span>
          Opslaan...
        {:else}
          Opslaan
        {/if}
      </button>
    </div>
  </form>
</dialog>
