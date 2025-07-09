<script lang="ts">
  import { onMount } from 'svelte';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import { fetchDigitalTwin, updateDigitalTwin } from '$lib/api';

  export let digitalTwinId: string;

  import AlertBanner from '$lib/components/AlertBanner.svelte';
  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let requiredBanner: InstanceType<typeof AlertBanner> | null = null;
  let requiredFieldMessage: string = '';

  let digitalTwin: DigitalTwin | null = null;
  let isReady = false;

  let title = '';
  let name = '';
  let subtitle = '';
  let owner = '';
  let isPrivate = false;

  async function loadDigitalTwin() {
    try {
      digitalTwin = await fetchDigitalTwin(digitalTwinId);
      if (digitalTwin) {
        title = digitalTwin.title ?? '';
        name = digitalTwin.name ?? '';
        subtitle = digitalTwin.subtitle ?? '';
        owner = digitalTwin.owner ?? '';
        isPrivate = digitalTwin.private ?? false;
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

    const missingFields = getMissingRequiredFields();

    if (missingFields.length > 0) {
      requiredFieldMessage = `Verplichte velden niet ingevuld: ${missingFields.join(', ')}`;
      requiredBanner?.show();
      return;
    }

    try {
      await updateDigitalTwin(digitalTwinId, {
        title,
        name,
        subtitle,
        owner,
        private: isPrivate
      });
      successBanner?.show();
    } catch (err) {
      console.error(err);
      errorBanner?.show();
    }
  }
</script>

<!-- AlertBanners that are only visable after the submit button is pressed -->
<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Digital Twin omschrijving bijgewerkt!"
/>
<AlertBanner bind:this={errorBanner} type="error" message="Fout bij het opslaan!" />
<AlertBanner bind:this={requiredBanner} type="error" message={requiredFieldMessage} />

{#if isReady}
  <form on:submit={handleSubmit} class="space-y-4">
    <div class="flex flex-col">
      <label for="title" class="mb-1 font-semibold">Titel:</label>
      <input
        id="title"
        class="input input-bordered"
        bind:value={title}
        class:error={!title.trim()}
      />
      {#if !title.trim()}
        <span class="text-error mt-1 text-sm">Titel is verplicht</span>
      {/if}
    </div>

    <div class="flex flex-col">
      <label for="name" class="mb-1 font-semibold">
        Naam <span class="opacity-50">(bestandsnaam)</span>:
      </label>
      <input id="name" class="input input-bordered" bind:value={name} class:error={!name.trim()} />
      {#if !name.trim()}
        <span class="text-error mt-1 text-sm">Naam is verplicht</span>
      {/if}
    </div>

    <div class="flex flex-col">
      <label for="subtitle" class="mb-1 font-semibold">Subtitle:</label>
      <input id="subtitle" class="input input-bordered" bind:value={subtitle} />
    </div>

    <div class="flex flex-col">
      <label for="owner" class="mb-1 font-semibold">Eigenaar:</label>
      <input id="owner" class="input input-bordered" bind:value={owner} />
    </div>

    <div class="flex items-center space-x-2">
      <input id="private" type="checkbox" bind:checked={isPrivate} />
      <label for="private" class="font-semibold">Privé</label>
    </div>

    <button type="submit" class="btn btn-primary">Opslaan</button>
  </form>
{:else}
  <div class="flex items-center justify-center py-12">
    <span class="loading loading-spinner loading-lg"></span>
    <span class="ml-3">Laden...</span>
  </div>
{/if}
