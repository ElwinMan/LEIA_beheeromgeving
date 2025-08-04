<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createBookmark } from '$lib/api';
  import type { Bookmark } from '$lib/types/tool';
  import AlertBanner from '$lib/components/AlertBanner.svelte';

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

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;

  export function showModal() {
    title = '';
    description = '';
    x = 0;
    y = 0;
    z = 0;
    heading = 0;
    pitch = 0;
    duration = 0;
    errorBanner?.hide?.();
    successBanner?.hide?.();
    modalRef.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();

    const payload = {
      title,
      description,
      x,
      y,
      z,
      heading,
      pitch,
      duration
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
    on:submit|preventDefault={handleSubmit}
    class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4"
  >
    <h3 class="col-span-4 mb-4 text-lg font-bold">Nieuwe Bookmark Aanmaken</h3>

    <label for="title" class="pr-4 text-right font-semibold">Titel:</label>
    <input id="title" class="input input-bordered col-span-3 w-full" bind:value={title} required />

    <label for="description" class="pr-4 text-right font-semibold">Beschrijving:</label>
    <input id="description" class="input input-bordered col-span-3 w-full" bind:value={description} />

    <!-- Position fields -->
    <label for="x" class="pr-4 text-right font-semibold">X-coördinaat:</label>
    <input id="x" type="number" step="any" class="input input-bordered col-span-3 w-full" bind:value={x} required />

    <label for="y" class="pr-4 text-right font-semibold">Y-coördinaat:</label>
    <input id="y" type="number" step="any" class="input input-bordered col-span-3 w-full" bind:value={y} required />

    <label for="z" class="pr-4 text-right font-semibold">Z-coördinaat:</label>
    <input id="z" type="number" step="any" class="input input-bordered col-span-3 w-full" bind:value={z} required />

    <!-- Camera orientation fields -->
    <label for="heading" class="pr-4 text-right font-semibold">Heading (graden):</label>
    <input id="heading" type="number" step="any" class="input input-bordered col-span-3 w-full" bind:value={heading} required />

    <label for="pitch" class="pr-4 text-right font-semibold">Pitch (graden):</label>
    <input id="pitch" type="number" step="any" class="input input-bordered col-span-3 w-full" bind:value={pitch} required />

    <label for="duration" class="pr-4 text-right font-semibold">Duur (seconden):</label>
    <input id="duration" type="number" step="any" class="input input-bordered col-span-3 w-full" bind:value={duration} required />

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>