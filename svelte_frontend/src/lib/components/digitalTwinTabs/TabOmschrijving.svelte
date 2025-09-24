<script lang="ts">
  import { onMount } from 'svelte';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import { fetchDigitalTwin, updateDigitalTwin } from '$lib/api';

  interface Props {
    digitalTwinId: string;
    digitalTwin?: DigitalTwin; // Optional, not used by this component
  }

  let { digitalTwinId }: Props = $props();

  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';
  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let requiredBanner: InstanceType<typeof AlertBanner> | null = null;
  let requiredFieldMessage = $state('');
  let errorMessage = $state('Fout bij het opslaan!');

  let digitalTwin: DigitalTwin | null = null;
  let isReady = $state(false);

  let title = $state('');
  let name = $state('');
  let subtitle = $state('');
  let owner = $state('');
  let isPrivate = $state(false);
  let hasChanges = $state(false);
  
  // Track original values for change detection
  let originalValues = $state({
    title: '',
    name: '',
    subtitle: '',
    owner: '',
    isPrivate: false
  });

  // Export methods for parent component
  export function getHasChanges() {
    return hasChanges;
  }

  export function saveTabChanges() {
    return handleSubmitInternal();
  }

  export function resetTabChanges() {
    title = originalValues.title;
    name = originalValues.name;
    subtitle = originalValues.subtitle;
    owner = originalValues.owner;
    isPrivate = originalValues.isPrivate;
    hasChanges = false;
  }

  // Check for changes
  $effect(() => {
    hasChanges = 
      title !== originalValues.title ||
      name !== originalValues.name ||
      subtitle !== originalValues.subtitle ||
      owner !== originalValues.owner ||
      isPrivate !== originalValues.isPrivate;
  });

  async function loadDigitalTwin() {
    try {
      digitalTwin = await fetchDigitalTwin(digitalTwinId);
      if (digitalTwin) {
        title = digitalTwin.title ?? '';
        name = digitalTwin.name ?? '';
        subtitle = digitalTwin.subtitle ?? '';
        owner = digitalTwin.owner ?? '';
        isPrivate = digitalTwin.isPrivate ?? false;
        
        // Store original values for change detection
        originalValues = {
          title,
          name,
          subtitle,
          owner,
          isPrivate
        };
        
        hasChanges = false;
        isReady = true;
      } else {
        console.error('DigitalTwin is null');
      }
    } catch (e) {
      console.error('Failed to load digital twin:', e);
    }
  }

  onMount(() => {
    loadDigitalTwin();
  });

  function getMissingRequiredFields(): string[] {
    const requiredFields = [
      { label: 'Titel', value: title },
      { label: 'Naam', value: name }
    ];

    return requiredFields.filter((field) => !field.value.trim()).map((field) => field.label);
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    return await handleSubmitInternal();
  }

  async function handleSubmitInternal() {
    const missingFields = getMissingRequiredFields();

    if (missingFields.length > 0) {
      requiredFieldMessage = `Verplichte velden niet ingevuld: ${missingFields.join(', ')}`;
      requiredBanner?.show();
      return false;
    }

    try {
      await updateDigitalTwin(digitalTwinId, {
        title,
        name,
        subtitle,
        owner,
        isPrivate: isPrivate
      });
      
      // Update original values after successful save
      originalValues = {
        title,
        name,
        subtitle,
        owner,
        isPrivate
      };
      hasChanges = false;
      
      successBanner?.show();
      return true;
    } catch (err: any) {
      console.error(err);
      // Check for duplicate name error (status 409 or message contains known phrases)
      if (
        err?.status === 409 ||
        (err?.message && (
          err.message.includes('duplicate key')
        ))
      ) {
        errorMessage = 'Deze naam is al in gebruik. Kies een andere naam.';
      } else {
        errorMessage = 'Fout bij het opslaan!';
      }
      errorBanner?.show();
      return false;
    }
  }
</script>

<!-- AlertBanners that are only visable after the submit button is pressed -->
<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Digital Twin omschrijving bijgewerkt!"
/>
<AlertBanner bind:this={errorBanner} type="error" message={errorMessage} />
<AlertBanner bind:this={requiredBanner} type="error" message={requiredFieldMessage} />

{#if isReady}
  <form onsubmit={handleSubmit} class="space-y-4">
    <div class="flex flex-col">
      <label for="title" class="mb-1 font-semibold flex items-center gap-2">
        Titel <span class="text-error">*</span>
        <HelpTooltip tip="De titel van de digital twin, zichtbaar in de applicatie en op de homepage." />
      </label>
      <input
        id="title"
        class="input input-bordered { !title.trim() ? 'border-error' : '' }"
        bind:value={title}
      />
      {#if !title.trim()}
        <span class="text-error mt-1 text-sm">Titel is verplicht</span>
      {/if}
    </div>

    <div class="flex flex-col">
      <label for="name" class="mb-1 font-semibold flex items-center gap-2">
        Naam <span class="opacity-50">(bestandsnaam)</span> <span class="text-error">*</span>
        <HelpTooltip tip="Unieke bestandsnaam voor export (zonder .config.json)." />
      </label>
      <input id="name" class="input input-bordered { !name.trim() ? 'border-error' : '' }" bind:value={name} />
      {#if !name.trim()}
        <span class="text-error mt-1 text-sm">Naam is verplicht</span>
      {/if}
    </div>

    <div class="flex flex-col">
      <label for="subtitle" class="mb-1 font-semibold flex items-center gap-2">
        Subtitle
        <HelpTooltip tip="Optionele ondertitel voor extra context of beschrijving." />
      </label>
      <input id="subtitle" class="input input-bordered" bind:value={subtitle} />
    </div>

    <div class="flex flex-col">
      <label for="owner" class="mb-1 font-semibold flex items-center gap-2">
        Eigenaar
        <HelpTooltip tip="Naam van de eigenaar of verantwoordelijke van deze digital twin." />
      </label>
      <input id="owner" class="input input-bordered" bind:value={owner} />
    </div>

    <div class="flex items-center space-x-2">
      <input id="isPrivate" type="checkbox" class="checkbox checkbox-primary" bind:checked={isPrivate} />
      <label for="isPrivate" class="font-semibold flex items-center gap-2">
        Privé
        <HelpTooltip tip="Indien aangevinkt is deze digital twin alleen te bereiken via de URL en niet zichtbaar in het overzicht." />
      </label>
    </div>

    <button type="submit" class="btn btn-primary">Opslaan</button>
  </form>
{:else}
  <div class="flex items-center justify-center py-12">
    <span class="loading loading-spinner loading-lg"></span>
    <span class="ml-3">Laden...</span>
  </div>
{/if}
