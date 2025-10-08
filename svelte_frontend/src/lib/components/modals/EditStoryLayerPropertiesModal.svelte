<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { RequiredLayer } from '$lib/types/tool';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';
  import AlertBanner from '$lib/components/AlertBanner.svelte';

  const dispatch = createEventDispatcher<{
    saved: {
      layer: RequiredLayer;
      properties: {
        transparent?: boolean;
        opacity?: number;
        style?: string;
      };
    };
  }>();

  let modalRef: HTMLDialogElement;
  let currentLayer: RequiredLayer | null = null;

  // Form fields
  let transparent = false;
  let opacity = 100;
  let style = '';
  let isSaving = false;

  // Alert banners
  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;

  // Store context for the parent component to use
  export let currentContext: any = null;

  export function show(layer: RequiredLayer) {
    currentLayer = layer;
    
    // Initialize form with current values
    transparent = layer.transparent || false;
    opacity = layer.opacity || 100;
    style = layer.style || '';
    
    modalRef?.showModal();
  }

  function resetModal() {
    currentLayer = null;
    transparent = false;
    opacity = 100;
    style = '';
    isSaving = false;
    currentContext = null;
    successBanner?.hide?.();
    errorBanner?.hide?.();
  }

  function handleSave() {
    if (!currentLayer || isSaving) return;
    
    isSaving = true;

    try {
      const properties: { transparent?: boolean; opacity?: number; style?: string } = {
        transparent,
        opacity: Number(opacity),
        style
      };

      dispatch('saved', {
        layer: currentLayer,
        properties
      });

      successBanner?.show();
      
      // Close modal after successful dispatch
      setTimeout(() => {
        modalRef?.close();
        resetModal();
      }, 300);
    } catch (error) {
      console.error('Failed to save story layer properties:', error);
      errorBanner?.show();
      isSaving = false;
    }
  }

  function handleCancel() {
    modalRef?.close();
    resetModal();
  }

  // Reactive statement to handle opacity when transparent changes
  $: if (!transparent) {
    opacity = 100;
  }
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Story layer eigenschappen opgeslagen!"
/>

<AlertBanner
  bind:this={errorBanner}
  type="error"
  message="Fout bij het opslaan van story layer eigenschappen!"
/>

<dialog bind:this={modalRef} class="modal">
  <form method="dialog" class="modal-box w-full max-w-2xl">
    <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2" onclick={handleCancel}>✕</button>
    
    <h3 class="text-lg font-bold mb-4">
      Story Layer Eigenschappen: {currentLayer?.title || 'Onbekende Layer'}
    </h3>

    <div class="space-y-6">
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
          oninput={() => { if (opacity > 100) opacity = 100; if (opacity < 0) opacity = 0; }}
          disabled={!transparent}
          placeholder="0-100"
        />
        {#if !transparent}
          <div class="label">
            <span class="label-text-alt text-gray-500">Ondoorzichtigheid is alleen beschikbaar wanneer transparantie is ingeschakeld.</span>
          </div>
        {/if}
      </div>

      <div class="form-control">
        <label class="label" for="style">
          <div class="flex items-center gap-2">
            <span class="label-text font-semibold">Style</span>
            <HelpTooltip tip="Aangepaste stijlinstellingen voor deze layer in de story. Bijvoorbeeld SLD styling parameters." />
          </div>
        </label>
        <textarea 
          id="style"
          class="textarea textarea-bordered w-full" 
          bind:value={style}
          placeholder="Voer aangepaste stijlinstellingen in..."
          rows="3"
        ></textarea>
      </div>
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