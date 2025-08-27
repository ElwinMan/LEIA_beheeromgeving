<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createBookmark } from '$lib/api';
  import type { Bookmark } from '$lib/types/tool';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';
  import MissingRequiredFields from '$lib/components/MissingRequiredFields.svelte';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Bookmark }>();

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

  function resetModal() {
    title = '';
    description = '';
    x = 0;
    y = 0;
    z = 0;
    heading = 0;
    pitch = 0;
    duration = 0;
    missingFields = [];
    errorBanner?.hide?.();
    successBanner?.hide?.();
  }

  export function showModal() {
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
      const newBookmark = await createBookmark(payload);
      dispatch('created', newBookmark);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error) {
      errorBanner?.show();
      console.error('Bookmark creation failed', error);
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
  message="Bookmark succesvol aangemaakt!"
/>

<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message="Er is een fout opgetreden bij het aanmaken van de bookmark!"
  />

  <form
    onsubmit={handleSubmit}
    class="modal-box grid w-full max-w-4xl min-h-[700px] grid-cols-4 items-center gap-4"
  >
    <div class="form-control col-span-4">
      <h3 class="mb-4 text-lg font-bold">Nieuwe Bookmark Aanmaken</h3>
      <MissingRequiredFields {missingFields} />
    </div>

    <label for="title" class="pr-4 text-right font-semibold">Titel <span class="text-error">*</span>:</label>
    <input id="title" class="input input-bordered col-span-3 w-full" bind:value={title} />

    <label for="description" class="pr-4 text-right font-semibold">Beschrijving:</label>
    <input id="description" class="input input-bordered col-span-3 w-full" bind:value={description} />

    <!-- X, Y, Z coordinates row -->
    <label for="x" class="pr-4 text-right font-semibold">Coördinaten (X, Y, Z):</label>
    <div class="col-span-3 flex gap-2">
      <input id="x" type="number" step="any" class="input input-bordered w-full" bind:value={x} required placeholder="X-coördinaat" />
      <input id="y" type="number" step="any" class="input input-bordered w-full" bind:value={y} required placeholder="Y-coördinaat" />
      <input id="z" type="number" step="any" class="input input-bordered w-full" bind:value={z} required placeholder="Z-coördinaat" />
    </div>

    <!-- Heading, Pitch, Duration row -->
    <label for="heading" class="pr-4 text-right font-semibold">Oriëntatie & Duur:</label>
    <div class="col-span-3 flex gap-2">
      <input id="heading" type="number" step="any" class="input input-bordered w-full" bind:value={heading} required placeholder="Heading (graden)" />
      <input id="pitch" type="number" step="any" class="input input-bordered w-full" bind:value={pitch} required placeholder="Pitch (graden)" />
      <input id="duration" type="number" step="any" class="input input-bordered w-full" bind:value={duration} required placeholder="Duur (seconden)" />
    </div>

    <!-- Position Selector -->
    <div class="pr-4 text-right font-semibold">Positie Selector:</div>
    <div class="col-span-3">
      <PositionSelector 
        buttonText="Selecteer positie op kaart"
        initialPosition={{ x, y, z, heading, pitch, duration }}
        on:coordinatesSelected={handleCoordinatesSelected}
      />
    </div>

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" onclick={() => { modalRef.close(); resetModal(); }}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>