<script lang="ts">
  import type { Story } from '$lib/types/tool';
  import { createEventDispatcher } from 'svelte';
  import { updateStory } from '$lib/api';
  import AlertBanner from '$lib/components/AlertBanner.svelte';

  export let story: Story | null = null;
  let modalRef: HTMLDialogElement;

  let name = '';
  let description = '';
  let content = '';

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;

  const dispatch = createEventDispatcher();

  export function showModal(s: Story) {
    story = s;
    name = s.name || '';
    description = s.description || '';
    content = s.content ? JSON.stringify(s.content, null, 2) : '';
    errorBanner?.hide?.();
    successBanner?.hide?.();
    modalRef.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!story) return;

    let payload: any = { name, description };
    if (content && content.trim() !== '') {
      try {
        payload.content = JSON.parse(content);
      } catch (e) {
        errorBanner?.show();
        return;
      }
    }

    try {
      const updated = await updateStory(String(story.id), payload);
      dispatch('updated', updated);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error) {
      errorBanner?.show();
      console.error('Update failed', error);
    }
  }
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Story succesvol bijgewerkt!"
/>

<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message="Content moet geldig JSON zijn!"
  />

  <form on:submit|preventDefault={handleSubmit} class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4">
    <h3 class="col-span-4 mb-4 text-lg font-bold">Story bewerken</h3>

    <label for="name" class="pr-4 text-right font-semibold">Naam:</label>
    <input id="name" type="text" class="input input-bordered col-span-3 w-full" bind:value={name} required />

    <label for="description" class="pr-4 text-right font-semibold">Beschrijving:</label>
    <input id="description" type="text" class="input input-bordered col-span-3 w-full" bind:value={description} />

    <label for="content" class="pr-4 text-right font-semibold">Content (JSON):</label>
    <textarea
      id="content"
      class="textarea textarea-bordered col-span-3 w-full min-h-[12rem]"
      bind:value={content}
      rows="10"
    ></textarea>

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>