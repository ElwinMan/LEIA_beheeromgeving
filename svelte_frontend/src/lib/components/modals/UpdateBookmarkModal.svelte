<script lang="ts">
  import type { Bookmark } from '$lib/types/tool';
  import { createEventDispatcher } from 'svelte';
  import { updateBookmark } from '$lib/api';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';
  import MissingRequiredFields from '$lib/components/MissingRequiredFields.svelte';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';

  export let bookmark: Bookmark | null = null;
  let modalRef: HTMLDialogElement;

  let title = '';
  let description = '';
  let x = 0;
  let y = 0;
  let z = 0;
  let heading = 0;
  let pitch = 0;
  let duration = 0;
  let missingFields: string[] = [];

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;

  const dispatch = createEventDispatcher();

  function resetModal() {
    missingFields = [];
    errorBanner?.hide?.();
    successBanner?.hide?.();
  }

  export function showModal(b: Bookmark) {
    bookmark = b;
    title = b.title || '';
    description = b.description || '';
    x = b.x || 0;
    y = b.y || 0;
    z = b.z || 0;
    heading = b.heading || 0;
    pitch = b.pitch || 0;
    duration = b.duration || 0;
    resetModal();
    modalRef.showModal();
  }

  function getMissingRequiredFields(): string[] {
    const fields: { label: string; value: any }[] = [
      { label: 'Titel', value: title }
    ];
    return fields.filter(f => !f.value || (typeof f.value === 'string' && !f.value.trim())).map(f => f.label);
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!bookmark) return;
    missingFields = getMissingRequiredFields();
    if (missingFields.length > 0) return;

    const payload = {
      title,
      description,
      x,
      y,
      z,
      heading,
      pitch,
      duration,
      last_updated: new Date().toISOString()
    };

    try {
      const updated = await updateBookmark(String(bookmark.id), payload);
      dispatch('updated', updated);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error) {
      errorBanner?.show();
      console.error('Update failed', error);
    }
  }

  function handleCoordinatesSelected(event: CustomEvent) {
    const coords = event.detail;
    x = coords.x || 0;
    y = coords.y || 0;
    z = coords.z || 0;
    heading = coords.heading || 0;
    pitch = coords.pitch || 0;
    duration = coords.duration || 0;
  }
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Bookmark succesvol bijgewerkt!"
/>

<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message="Er is een fout opgetreden bij het bijwerken van de bookmark!"
  />

  <form on:submit|preventDefault={handleSubmit} class="modal-box grid w-full max-w-4xl min-h-[700px] grid-cols-4 items-center gap-4">
    <div class="form-control col-span-4">
      <h3 class="mb-4 text-lg font-bold">Bookmark bewerken</h3>
      {#if missingFields.length > 0}
        <MissingRequiredFields {missingFields} />
      {/if}
    </div>

    <label for="title" class="pr-4 text-right font-semibold">
      Titel <span class="text-error">*</span>:
      <HelpTooltip tip="De titel van de bookmark." position="right" />
    </label>
    <input id="title" type="text" class="input input-bordered col-span-3 w-full" bind:value={title} />

    <label for="description" class="pr-4 text-right font-semibold">
      Beschrijving:
      <HelpTooltip tip="Een optionele beschrijving van de bookmark." position="right" />
    </label>
    <input id="description" type="text" class="input input-bordered col-span-3 w-full" bind:value={description} />

    <!-- Position Selector -->
    <span class="pr-4 text-right font-semibold">
      Positie Selecteren:
      <HelpTooltip tip="Gebruik de kaart om een positie te selecteren. Dit vult automatisch de coördinaten in." position="right" />
    </span>
    <div class="col-span-3">
      <PositionSelector 
        buttonText="Selecteer positie op kaart"
        initialPosition={{ x, y, z, heading, pitch, duration }}
        on:coordinatesSelected={handleCoordinatesSelected}
      />
    </div>

    <!-- X, Y, Z coordinates row with labels above each input -->
    <div></div>
    <div class="col-span-3 flex gap-2">
      <div class="flex flex-col w-full">
        <label for="x" class="block text-xs font-medium mb-1">
          X
          <HelpTooltip tip="X-coördinaat (longitude) van de positie." />
        </label>
        <input id="x" type="number" step="any" class="input input-bordered w-full" bind:value={x} placeholder="X-coördinaat" />
      </div>
      <div class="flex flex-col w-full">
        <label for="y" class="block text-xs font-medium mb-1">
          Y
          <HelpTooltip tip="Y-coördinaat (latitude) van de positie." />
        </label>
        <input id="y" type="number" step="any" class="input input-bordered w-full" bind:value={y} placeholder="Y-coördinaat" />
      </div>
      <div class="flex flex-col w-full">
        <label for="z" class="block text-xs font-medium mb-1">
          Z
          <HelpTooltip tip="Z-coördinaat (hoogte) van de positie." />
        </label>
        <input id="z" type="number" step="any" class="input input-bordered w-full" bind:value={z} placeholder="Z-coördinaat" />
      </div>
    </div>

    <!-- Heading, Pitch, Duration row with labels above each input -->
    <div></div>
    <div class="col-span-3 flex gap-2">
      <div class="flex flex-col w-full">
        <label for="heading" class="block text-xs font-medium mb-1">
          Heading
          <HelpTooltip tip="De richting waarin de camera kijkt (in graden)." />
        </label>
        <input id="heading" type="number" step="any" class="input input-bordered w-full" bind:value={heading} placeholder="Heading (graden)" />
      </div>
      <div class="flex flex-col w-full">
        <label for="pitch" class="block text-xs font-medium mb-1">
          Pitch
          <HelpTooltip tip="De kantelhoek van de camera (omhoog/omlaag in graden)." />
        </label>
        <input id="pitch" type="number" step="any" class="input input-bordered w-full" bind:value={pitch} placeholder="Pitch (graden)" />
      </div>
      <div class="flex flex-col w-full">
        <label for="duration" class="block text-xs font-medium mb-1">
          Duur
          <HelpTooltip tip="De duur van de camera animatie in seconden." />
        </label>
        <input id="duration" type="number" step="any" class="input input-bordered w-full" bind:value={duration} placeholder="Duur (seconden)" />
      </div>
    </div>

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => { modalRef.close(); resetModal(); }}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>